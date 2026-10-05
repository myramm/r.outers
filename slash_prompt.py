import os
import sys
import select
import shutil
import signal
import tty
import termios
import re
from ui import console
from styles import (
    get_current_style_settings,
    render_prompt_layout,
    get_terminal_width,
    get_safe_width,
    truncate_text,
    wrap_text,
    COLOR_SCHEMES,
    THEMES_MAP,
    THEMES
)

SLASH_COMMANDS = [
    {"cmd": "/gas", "desc": "Lanjutkan & paksa agent teruskan task (Force Continue / Resume)"},
    {"cmd": "/lanjut", "desc": "Lanjutkan proses atau tugas sebelumnya (/continue)"},
    {"cmd": "/status", "desc": "Lihat status aktif agent, antrean task, dan model"},
    {"cmd": "/stop", "desc": "Hentikan atau batalkan task yang sedang aktif (/cancel)"},
    {"cmd": "/setup", "desc": "Pusat Pengaturan (API Key, Izin Shell, Model, Provider, Reset)"},
    {"cmd": "/theme", "desc": "Pilih Color Scheme (terminal, light, dark, solarized, tokyo night)"},
    {"cmd": "/model", "desc": "Pilih dan ganti model AI aktif (/m)"},
    {"cmd": "/provider", "desc": "Pindah atau tambah Provider API (/p)"},
    {"cmd": "/skills", "desc": "Kelola & lihat daftar skill terpasang"},
    {"cmd": "/add-skill", "desc": "Pasang skill baru dari URL GitHub / repo"},
    {"cmd": "/memory", "desc": "Lihat dan kelola memori tersimpan"},
    {"cmd": "/list", "desc": "Tabel daftar Provider dan Model AI"},
    {"cmd": "/clear", "desc": "Bersihkan riwayat chat & reset tampilan layar (/cls)"},
    {"cmd": "/help", "desc": "Tampilkan panduan bantuan r.outers"},
    {"cmd": "/exit", "desc": "Keluar dari r.outers (/quit)"},
]

def read_key_raw(fd, timeout=0.05):
    try:
        r, _, _ = select.select([fd], [], [], timeout)
        if not r:
            return 'TIMEOUT'
        raw = os.read(fd, 4096)
    except Exception:
        return 'TIMEOUT'
    if not raw:
        return 'TIMEOUT'

    # Handle bracketed paste mode
    if b'\x1b[200~' in raw:
        raw = raw.replace(b'\x1b[200~', b'').replace(b'\x1b[201~', b'')

    # Escape sequence
    if raw == b'\x1b':
        r, _, _ = select.select([fd], [], [], 0.08)
        if r:
            extra = os.read(fd, 31)
            raw = raw + extra

    if raw.startswith((b'\x1b[A', b'\x1bOA', b'\x1b[1;2A', b'\x1b[1;5A')):
        return 'UP'
    if raw.startswith((b'\x1b[B', b'\x1bOB', b'\x1b[1;2B', b'\x1b[1;5B')):
        return 'DOWN'
    if raw.startswith((b'\x1b[C', b'\x1bOC')):
        return 'RIGHT'
    if raw.startswith((b'\x1b[D', b'\x1bOD')):
        return 'LEFT'
    if raw.startswith((b'\x1b[5~', b'\x1b[V')):
        return 'PAGE_UP'
    if raw.startswith((b'\x1b[6~', b'\x1b[U')):
        return 'PAGE_DOWN'
    if raw.startswith((b'\x1b[Z',)):
        return 'SHIFT_TAB'
    if raw == b'\t':
        return 'TAB'
    if raw == b'\x0e':
        return 'DOWN'
    if raw == b'\x10':
        return 'UP'
    if raw in (b'\r', b'\n'):
        return 'ENTER'
    if raw in (b'\x7f', b'\x08'):
        return 'BACKSPACE'
    if raw == b'\x1b':
        return 'ESC'
    if raw == b'\x03':
        return 'CTRL_C'
    if raw == b'\x04':
        return 'CTRL_D'
    if raw == b'\x15':
        return 'CTRL_U'

    try:
        decoded = raw.decode('utf-8', errors='ignore')
        printable_text = ''.join(c for c in decoded if c.isprintable() or c == ' ')
        if printable_text:
            return printable_text
    except Exception:
        pass
    return None

def render_slash_autocomplete(query, matches, selected_idx, width, max_items=5):
    lines = []
    sep_width = max(30, min(width, 50))
    lines.append(f"\033[90m{'─' * sep_width}\033[0m")

    visible = matches[:max_items]
    for idx, item in enumerate(visible):
        is_sel = (idx == selected_idx)
        cmd_str = item["cmd"]
        desc_str = item["desc"]

        avail_w = sep_width - 4
        cmd_col_w = 12
        desc_avail = avail_w - cmd_col_w
        if len(desc_str) > desc_avail:
            desc_str = desc_str[:desc_avail - 2] + ".."

        if is_sel:
            row = f" > \033[1;36m{cmd_str:<10}\033[0m  \033[32m{desc_str}\033[0m"
        else:
            row = f"   \033[36m{cmd_str:<10}\033[0m  \033[90m{desc_str}\033[0m"
        lines.append(row)

    if len(matches) > max_items:
        diff = len(matches) - max_items
        lines.append(f"   \033[90m_ {diff} more\033[0m")

    return lines

HISTORY_FILE = os.path.expanduser("~/.routers_history")
_GLOBAL_HISTORY = None

def load_input_history():
    global _GLOBAL_HISTORY
    if _GLOBAL_HISTORY is None:
        _GLOBAL_HISTORY = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    _GLOBAL_HISTORY = [line.rstrip("\r\n") for line in f if line.strip()]
            except Exception:
                _GLOBAL_HISTORY = []
    return _GLOBAL_HISTORY

def append_input_history(entry):
    global _GLOBAL_HISTORY
    if not entry or not entry.strip():
        return
    entry = entry.strip()
    history = load_input_history()
    if not history or history[-1] != entry:
        history.append(entry)
        try:
            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception:
            pass

_terminal_resized = False

def _sigwinch_handler(signum, frame):
    global _terminal_resized
    _terminal_resized = True

def clear_popup_lines(count):
    if count <= 0:
        return
    # Cursor sits on Line 2. Move down 3 lines to Line 5, clear downwards, move back up to Line 2.
    sys.stdout.write("\033[3B\033[J\033[3A\r")
    sys.stdout.flush()

def get_smart_input(prompt_display_str="", sub_info="", provider_name="clouvia", model_name="free-model", auto_approve=True):
    global _terminal_resized
    _terminal_resized = False
    _, theme_id = get_current_style_settings()

    if not sys.stdin.isatty():
        from rich.prompt import Prompt
        res = Prompt.ask("")
        if res and res.strip():
            append_input_history(res.strip())
        return res

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    from queue_manager import get_and_clear_pending_draft
    draft = get_and_clear_pending_draft()
    current_text = draft if draft else ""
    cursor_pos = len(current_text)
    selected_idx = 0
    last_popup_lines_count = 0
    
    history = list(load_input_history())
    history_idx = len(history)
    saved_draft = ""

    old_sigwinch = None
    try:
        old_sigwinch = signal.signal(signal.SIGWINCH, _sigwinch_handler)
    except Exception:
        pass

    try:
        tty.setraw(fd)
        sys.stdout.write("\033[?7l")
        sys.stdout.flush()

        is_first_render = True
        last_rendered_cols = -1
        need_redraw = True

        while True:
            try:
                term_cols = shutil.get_terminal_size((80, 24)).columns
            except Exception:
                term_cols = 80

            if _terminal_resized or term_cols != last_rendered_cols:
                _terminal_resized = False
                need_redraw = True

            if need_redraw:
                last_rendered_cols = term_cols

                if last_popup_lines_count > 0:
                    clear_popup_lines(last_popup_lines_count)
                    last_popup_lines_count = 0

                layout = render_prompt_layout("box", theme_id, provider_name=provider_name, model_name=model_name, auto_approve=auto_approve, current_input=current_text, cursor_col=cursor_pos, term_cols=term_cols)
                cursor_col = layout.get("cursor_col", cursor_pos)
                cursor_move = f"\033[{cursor_col}C" if cursor_col > 0 else ""

                prefix_jump = "" if is_first_render else "\033[1A\r"
                is_first_render = False

                # Complete 4-line Box Layout:
                # Line 1: Top divider
                # Line 2: Input line (cursor sits here)
                # Line 3: Bottom divider
                # Line 4: Status footer (always formatted to fit)
                prompt_bundle = (
                    f"{prefix_jump}\033[2K{layout['divider']}\r\n"
                    f"\033[2K{layout['input_rendered']}\r\n"
                    f"\033[2K{layout['divider']}\r\n"
                    f"\033[2K{layout['status_footer']}"
                )

                if current_text.startswith("/"):
                    q = current_text.strip().lower()
                    matches = [c for c in SLASH_COMMANDS if q in c["cmd"].lower() or c["cmd"].startswith(q)]
                    if not matches:
                        matches = [{"cmd": current_text, "desc": "Jalankan perintah"}]

                    if selected_idx >= len(matches):
                        selected_idx = max(0, len(matches) - 1)

                    popup_lines = render_slash_autocomplete(current_text, matches, selected_idx, term_cols)
                    
                    popup_buf = []
                    for pl in popup_lines:
                        popup_buf.append(f"\r\n\033[2K{pl}")
                    
                    total_up = 2 + len(popup_lines)
                    sys.stdout.write(f"{prompt_bundle}{''.join(popup_buf)}\033[{total_up}A\r{cursor_move}")
                    sys.stdout.flush()
                    last_popup_lines_count = len(popup_lines)
                else:
                    sys.stdout.write(f"{prompt_bundle}\033[2A\r{cursor_move}")
                    sys.stdout.flush()

                need_redraw = False

            k = read_key_raw(fd)

            if k == 'TIMEOUT':
                try:
                    new_cols = shutil.get_terminal_size((80, 24)).columns
                except Exception:
                    new_cols = term_cols
                if _terminal_resized or new_cols != last_rendered_cols:
                    need_redraw = True
                continue

            need_redraw = True

            if k == 'CTRL_C':
                if last_popup_lines_count > 0:
                    clear_popup_lines(last_popup_lines_count)
                    last_popup_lines_count = 0
                sys.stdout.write(f"\033[1A\r\033[2K{layout['divider']}\r\n\033[2K\033[90m>\033[0m {current_text}\r\n\033[2K\r\n\033[2K\033[1A\r")
                sys.stdout.flush()
                return ""

            elif k == 'CTRL_D':
                if not current_text:
                    if last_popup_lines_count > 0:
                        clear_popup_lines(last_popup_lines_count)
                        last_popup_lines_count = 0
                    sys.stdout.write(f"\033[1A\r\033[2K{layout['divider']}\r\n\033[2K\033[90m>\033[0m \r\n\033[2K\r\n\033[2K\033[1A\r")
                    sys.stdout.flush()
                    raise EOFError()

            elif k == 'ESC':
                if current_text.startswith("/"):
                    current_text = ""
                    cursor_pos = 0
                    selected_idx = 0
                else:
                    current_text = ""
                    cursor_pos = 0

            elif k in ('UP', 'SHIFT_TAB'):
                if current_text.startswith("/"):
                    q = current_text.strip().lower()
                    matches = [c for c in SLASH_COMMANDS if q in c["cmd"].lower() or c["cmd"].startswith(q)]
                    if matches:
                        selected_idx = (selected_idx - 1) % len(matches)
                else:
                    if history:
                        if history_idx == len(history):
                            saved_draft = current_text
                        if history_idx > 0:
                            history_idx -= 1
                            current_text = history[history_idx]
                            cursor_pos = len(current_text)

            elif k in ('DOWN',):
                if current_text.startswith("/"):
                    q = current_text.strip().lower()
                    matches = [c for c in SLASH_COMMANDS if q in c["cmd"].lower() or c["cmd"].startswith(q)]
                    if matches:
                        selected_idx = (selected_idx + 1) % len(matches)
                else:
                    if history and history_idx < len(history):
                        history_idx += 1
                        if history_idx < len(history):
                            current_text = history[history_idx]
                            cursor_pos = len(current_text)
                        else:
                            current_text = saved_draft
                            cursor_pos = len(current_text)

            elif k == 'TAB':
                if current_text.startswith("/"):
                    q = current_text.strip().lower()
                    matches = [c for c in SLASH_COMMANDS if q in c["cmd"].lower() or c["cmd"].startswith(q)]
                    if matches:
                        chosen = matches[selected_idx]["cmd"]
                        current_text = chosen
                        cursor_pos = len(current_text)

            elif k == 'ENTER':
                if current_text.startswith("/"):
                    q = current_text.strip().lower()
                    matches = [c for c in SLASH_COMMANDS if q in c["cmd"].lower() or c["cmd"].startswith(q)]
                    if matches and selected_idx < len(matches):
                        if current_text == "/" or current_text in [m["cmd"][:len(current_text)] for m in matches]:
                            current_text = matches[selected_idx]["cmd"]

                if last_popup_lines_count > 0:
                    clear_popup_lines(last_popup_lines_count)
                    last_popup_lines_count = 0
                
                # Finalize: leave clean top divider + user input line in history
                sys.stdout.write(f"\033[1A\r\033[2K{layout['divider']}\r\n\033[2K\033[90m>\033[0m \033[1;37m{current_text}\033[0m\r\n\033[2K\r\n\033[2K\033[1A\r")
                sys.stdout.flush()
                
                res = current_text.strip()
                if res:
                    append_input_history(res)
                return res

            elif k == 'BACKSPACE':
                if cursor_pos > 0:
                    current_text = current_text[:cursor_pos - 1] + current_text[cursor_pos:]
                    cursor_pos -= 1
                    selected_idx = 0

            elif k == 'CTRL_U':
                current_text = ""
                cursor_pos = 0
                selected_idx = 0

            elif k == 'LEFT':
                if cursor_pos > 0:
                    cursor_pos -= 1

            elif k == 'RIGHT':
                if cursor_pos < len(current_text):
                    cursor_pos += 1

            elif k and isinstance(k, str) and not k.startswith(('UP', 'DOWN', 'LEFT', 'RIGHT', 'ESC', 'TAB', 'ENTER', 'BACKSPACE', 'CTRL_', 'SHIFT_', 'PAGE_')):
                current_text = current_text[:cursor_pos] + k + current_text[cursor_pos:]
                cursor_pos += len(k)
                selected_idx = 0

    finally:
        if old_sigwinch is not None:
            try:
                signal.signal(signal.SIGWINCH, old_sigwinch)
            except Exception:
                pass
        sys.stdout.write("\033[?7h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
