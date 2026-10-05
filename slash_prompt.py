import os
import sys
import select
import tty
import termios
from ui import console

SLASH_COMMANDS = [
    {"cmd": "/setup", "desc": "Pusat Pengaturan (API Key, Izin Shell, Model, Provider, Reset)"},
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

def read_key_raw(fd):
    try:
        raw = os.read(fd, 4096)
    except Exception:
        return None
    if not raw:
        return None

    # Handle bracketed paste mode (Termux / Linux / Mac terminals)
    if b'\x1b[200~' in raw:
        raw = raw.replace(b'\x1b[200~', b'').replace(b'\x1b[201~', b'')

    # Jika hanya \x1b, periksa apakah ada byte lanjutan (escape sequence)
    if raw == b'\x1b':
        r, _, _ = select.select([fd], [], [], 0.08)
        if r:
            extra = os.read(fd, 31)
            raw = raw + extra

    # Escape sequences navigasi
    if raw in (b'\x1b[A', b'\x1bOA', b'\x1b[1;2A', b'\x1b[1;5A'):
        return 'UP'
    if raw in (b'\x1b[B', b'\x1bOB', b'\x1b[1;2B', b'\x1b[1;5B'):
        return 'DOWN'
    if raw in (b'\x1b[C', b'\x1bOC'):
        return 'RIGHT'
    if raw in (b'\x1b[D', b'\x1bOD'):
        return 'LEFT'
    if raw in (b'\x1b[5~', b'\x1b[V'):
        return 'PAGE_UP'
    if raw in (b'\x1b[6~', b'\x1b[U'):
        return 'PAGE_DOWN'
    if raw in (b'\x1b[Z',):
        return 'SHIFT_TAB'
    if raw == b'\t':
        return 'TAB'
    if raw == b'\x0e':  # Ctrl+N
        return 'DOWN'
    if raw == b'\x10':  # Ctrl+P
        return 'UP'
    if raw in (b'\r', b'\n'):
        return 'ENTER'
    if raw in (b'\x7f', b'\x08'):
        return 'BACKSPACE'
    if raw == b'\x1b':
        return 'ESC'
    if raw == b'\x03':  # Ctrl+C
        return 'CTRL_C'
    if raw == b'\x04':  # Ctrl+D
        return 'CTRL_D'
    if raw == b'\x15':  # Ctrl+U
        return 'CTRL_U'

    try:
        decoded = raw.decode('utf-8', errors='ignore')
        # Filter karakter printable dan spasi (mendukung paste teks panjang / multi-karakter)
        printable_text = ''.join(c for c in decoded if c.isprintable() or c == ' ')
        if printable_text:
            return printable_text
    except Exception:
        pass
    return None

def render_slash_autocomplete(query, matches, selected_idx, width, max_items=5):
    lines = []
    
    sep_width = max(32, min(width, 65))
    lines.append(f"\033[90m{'─' * sep_width}\033[0m")

    visible = matches[:max_items]
    for idx, item in enumerate(visible):
        is_sel = (idx == selected_idx)
        cmd_str = item["cmd"]
        desc_str = item["desc"]

        avail_w = sep_width - 4
        cmd_col_w = 14
        desc_avail = avail_w - cmd_col_w
        if len(desc_str) > desc_avail:
            desc_str = desc_str[:desc_avail - 2] + ".."

        if is_sel:
            row = f" > \033[1;36m{cmd_str:<12}\033[0m  \033[32m{desc_str}\033[0m"
        else:
            row = f"   \033[36m{cmd_str:<12}\033[0m  \033[90m{desc_str}\033[0m"
        lines.append(row)

    if len(matches) > max_items:
        diff = len(matches) - max_items
        lines.append(f"   \033[90m_ {diff} more\033[0m")

    lines.append("")
    footer_hint = " \033[90m_/_ Navigate • \033[1;37menter\033[0m \033[90mSelect • \033[1;37mtab\033[0m \033[90mComplete • esc to cancel\033[0m"
    lines.append(footer_hint)

    return lines

import re

def get_visible_len(s):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return len(ansi_escape.sub('', s))

def clear_popup_lines(count):
    if count <= 0:
        return
    buf = []
    for _ in range(count):
        buf.append("\033[B\033[2K")
    buf.append("\033[J")
    buf.append(f"\033[{count}A\r")
    sys.stdout.write("".join(buf))
    sys.stdout.flush()

def get_smart_input(prompt_display_str, sub_info=""):
    if not sys.stdin.isatty():
        from rich.prompt import Prompt
        if sub_info:
            console.print(f"\033[90m{sub_info}\033[0m")
        return Prompt.ask(prompt_display_str)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    current_text = ""
    cursor_pos = 0
    selected_idx = 0
    last_popup_lines_count = 0
    prompt_vlen = get_visible_len(prompt_display_str)

    try:
        tty.setraw(fd)
        sys.stdout.write("\033[?7l")
        sys.stdout.flush()

        while True:
            try:
                term_cols = os.get_terminal_size().columns
            except Exception:
                term_cols = 50

            if last_popup_lines_count > 0:
                clear_popup_lines(last_popup_lines_count)
                last_popup_lines_count = 0

            cursor_block = "\033[42m \033[0m"
            before = current_text[:cursor_pos]
            after = current_text[cursor_pos:]
            cursor_col = prompt_vlen + 1 + len(before)
            
            if sub_info:
                prompt_line = f"\r\033[2K{prompt_display_str} {before}{cursor_block}{after}\r\n\033[2K\033[90m{sub_info}\033[0m\033[1A\r\033[{cursor_col}C"
            else:
                prompt_line = f"\r\033[2K{prompt_display_str} {before}{cursor_block}{after}"

            sys.stdout.write(prompt_line)
            sys.stdout.flush()

            if current_text.startswith("/"):
                q = current_text.strip().lower()
                matches = [c for c in SLASH_COMMANDS if q in c["cmd"].lower() or c["cmd"].startswith(q)]
                if not matches:
                    matches = [{"cmd": current_text, "desc": "Jalankan perintah"}]

                if selected_idx >= len(matches):
                    selected_idx = max(0, len(matches) - 1)

                popup_lines = render_slash_autocomplete(current_text, matches, selected_idx, term_cols)
                
                output_buf = []
                if sub_info:
                    output_buf.append(f"\r\n\033[2K\033[90m{sub_info}\033[0m")
                for pl in popup_lines:
                    output_buf.append(f"\r\n\033[2K{pl}")
                
                up_steps = len(popup_lines) + (1 if sub_info else 0)
                output_buf.append(f"\033[{up_steps}A\r\033[{cursor_col}C")
                sys.stdout.write("".join(output_buf))
                sys.stdout.flush()
                
                last_popup_lines_count = len(popup_lines) + (1 if sub_info else 0)

            k = read_key_raw(fd)

            if k == 'CTRL_C':
                if last_popup_lines_count > 0:
                    clear_popup_lines(last_popup_lines_count)
                    last_popup_lines_count = 0
                if sub_info:
                    sys.stdout.write(f"\r\033[2K{prompt_display_str} {current_text}\r\n\033[2K\033[90m{sub_info}\033[0m\r\n")
                else:
                    sys.stdout.write("\r\n")
                sys.stdout.flush()
                return ""

            elif k == 'CTRL_D':
                if not current_text:
                    if last_popup_lines_count > 0:
                        clear_popup_lines(last_popup_lines_count)
                        last_popup_lines_count = 0
                    if sub_info:
                        sys.stdout.write(f"\r\033[2K{prompt_display_str}\r\n\033[2K\033[90m{sub_info}\033[0m\r\n")
                    else:
                        sys.stdout.write("\r\n")
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

            elif k in ('DOWN',):
                if current_text.startswith("/"):
                    q = current_text.strip().lower()
                    matches = [c for c in SLASH_COMMANDS if q in c["cmd"].lower() or c["cmd"].startswith(q)]
                    if matches:
                        selected_idx = (selected_idx + 1) % len(matches)

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
                
                if sub_info:
                    sys.stdout.write(f"\r\033[2K{prompt_display_str} {current_text}\r\n\033[2K\033[90m{sub_info}\033[0m\r\n")
                else:
                    sys.stdout.write(f"\r\033[2K{prompt_display_str} {current_text}\r\n")
                sys.stdout.flush()
                return current_text.strip()

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
                # Mendukung pengetikan karakter tunggal maupun paste teks panjang
                current_text = current_text[:cursor_pos] + k + current_text[cursor_pos:]
                cursor_pos += len(k)
                selected_idx = 0

    finally:
        sys.stdout.write("\033[?7h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
