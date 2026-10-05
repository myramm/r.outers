import os
import sys
import json
import time
import requests
import select
import tty
import termios
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from ui import console
from config import (
    load_full_config, save_full_config, get_active_config,
    update_active_model, add_new_provider, switch_provider,
    CONFIG_FILE, PRESET_PROVIDERS, setup_initial_config
)
from memory import load_memory, GLOBAL_MEMORY_FILE, LOCAL_MEMORY_FILE

def read_key_raw_fd(fd):
    try:
        raw = os.read(fd, 32)
    except Exception:
        return None
    if not raw:
        return None

    if raw == b'\x1b':
        r, _, _ = select.select([fd], [], [], 0.08)
        if r:
            extra = os.read(fd, 31)
            raw = raw + extra

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
    return None

def wait_esc_or_enter():
    if not sys.stdin.isatty():
        return
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            k = read_key_raw_fd(fd)
            if k in ('ESC', 'ENTER', 'CTRL_C'):
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def render_settings_frame(items, selected_idx, width):
    lines = []
    title = "⚙️  r.outers Setup Hub"
    esc_label = "[Esc: Keluar]"
    
    gap = width - len(title) - len(esc_label) - 2
    if gap < 1: gap = 1
    lines.append(f"\033[1;36m{title}\033[0m{' ' * gap}\033[90m{esc_label}\033[0m")
    lines.append(f"\033[90m{'─' * width}\033[0m")
    lines.append("")

    for idx, it in enumerate(items):
        is_sel = (idx == selected_idx)
        label = it["label"]
        status = it.get("status", "")
        
        prefix = "▸ " if is_sel else "  "
        avail_w = width - 4
        
        if len(label) + len(status) + len(prefix) + 2 > avail_w:
            max_lbl = avail_w - len(status) - len(prefix) - 3
            if max_lbl > 6:
                label = label[:max_lbl] + ".."
            else:
                label = label[:avail_w - 4]
                status = ""

        gap_s = avail_w - len(prefix) - len(label) - len(status)
        if gap_s < 1: gap_s = 1
        
        if is_sel:
            row_full = f"{prefix}{label}{' ' * gap_s}{status}"
            lines.append(f"\033[7m\033[1m {row_full:<{avail_w}} \033[0m")
        else:
            lines.append(f"{prefix}\033[1;37m{label}\033[0m{' ' * gap_s}\033[90m{status}\033[0m")

    lines.append("")
    lines.append(f"\033[90m{'─' * width}\033[0m")
    lines.append(" \033[1;33m↑↓/Tab\033[0m \033[90mPilih\033[0m  \033[1;32mEnter\033[0m \033[90mBuka\033[0m  \033[90mEsc Keluar\033[0m")
    return lines

def show_settings_hub(current_config, auto_approve_ref=None):
    if not sys.stdin.isatty():
        return current_config

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    selected_idx = 0

    while True:
        full_cfg = load_full_config()
        active_prov = full_cfg.get("active_provider", "clouvia")
        providers = full_cfg.get("providers", {})
        curr_prov_info = providers.get(active_prov, {})
        curr_model = curr_prov_info.get("model", "free-model")
        
        has_key = bool(curr_prov_info.get("api_key", "").strip())
        key_status = "[Tersimpan]" if has_key else "[Kosong]"
        
        perm_mode = full_cfg.get("permission_mode", "ask")
        if perm_mode == "always_allow" or (auto_approve_ref and auto_approve_ref[0]):
            perm_status = "[Auto-Approve]"
        else:
            perm_status = "[Tanya y/n]"

        items = [
            {"id": "api_key", "label": "🔑 Kelola API Key", "status": f"{active_prov}: {key_status}"},
            {"id": "provider", "label": "📡 Ganti / Tambah Provider", "status": f"[{active_prov}]"},
            {"id": "model", "label": "🤖 Pilih Model AI", "status": f"[{curr_model}]"},
            {"id": "permission", "label": "🛡️ Izin Eksekusi Shell", "status": perm_status},
            {"id": "memory", "label": "🧠 Kelola Memori Agent", "status": "[Global/Proyek]"},
            {"id": "test", "label": "🧪 Test Endpoint (Ping API)", "status": "[Uji Latency]"},
            {"id": "diag", "label": "📋 Diagnostik Sistem", "status": "[Status Info]"},
            {"id": "reset", "label": "🔄 Reset ke Setelan Pabrik", "status": "[Factory Reset]"},
            {"id": "exit", "label": "⬅️ Selesai & Kembali ke Chat", "status": "[Kembali]"}
        ]

        sys.stdout.write("\033[?1049h\033[?25l\033[H\033[2J")
        sys.stdout.flush()

        try:
            tty.setraw(fd)
            sys.stdout.write("\033[?7l")
            sys.stdout.flush()

            while True:
                try:
                    term_cols = os.get_terminal_size().columns
                except Exception:
                    term_cols = 50

                modal_width = max(34, min(term_cols - 2, 56))

                lines = render_settings_frame(items, selected_idx, modal_width)
                output_buf = ["\033[H"]
                for l in lines:
                    output_buf.append(f"\r\033[2K{l}\r\n")
                output_buf.append("\r\033[J")
                sys.stdout.write("".join(output_buf))
                sys.stdout.flush()

                k = read_key_raw_fd(fd)

                if k in ('ESC', 'CTRL_C'):
                    return get_active_config()

                elif k in ('UP', 'SHIFT_TAB'):
                    if selected_idx > 0:
                        selected_idx -= 1
                    else:
                        selected_idx = len(items) - 1

                elif k in ('DOWN', 'TAB'):
                    if selected_idx < len(items) - 1:
                        selected_idx += 1
                    else:
                        selected_idx = 0

                elif k == 'PAGE_UP':
                    selected_idx = max(0, selected_idx - 4)

                elif k == 'PAGE_DOWN':
                    selected_idx = min(len(items) - 1, selected_idx + 4)

                elif k == 'ENTER':
                    chosen_action = items[selected_idx]["id"]
                    break

        finally:
            sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
            sys.stdout.flush()
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if chosen_action == "exit":
            console.print("[bold green]✔ Pengaturan disimpan. Kembali ke mode chat.[/bold green]\n")
            return get_active_config()

        elif chosen_action == "api_key":
            handle_manage_api_keys_interactive(full_cfg)

        elif chosen_action == "provider":
            switch_provider()

        elif chosen_action == "model":
            from selector import select_model_interactive
            current_config = select_model_interactive(get_active_config())

        elif chosen_action == "permission":
            handle_permission_settings_interactive(full_cfg, auto_approve_ref)

        elif chosen_action == "memory":
            handle_manage_memory_interactive()

        elif chosen_action == "test":
            handle_test_connection()
            console.print("\n[dim]Tekan ESC atau Enter untuk kembali...[/dim]")
            wait_esc_or_enter()

        elif chosen_action == "diag":
            handle_system_diagnostics(get_active_config(), auto_approve_ref)
            console.print("[dim]Tekan ESC atau Enter untuk kembali...[/dim]")
            wait_esc_or_enter()

        elif chosen_action == "reset":
            handle_factory_reset()

def handle_manage_api_keys_interactive(full_cfg):
    if not sys.stdin.isatty():
        return

    providers = full_cfg.get("providers", {})
    p_keys = list(providers.keys())
    if not p_keys:
        return

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    selected = 0

    items = []
    for k in p_keys:
        p = providers[k]
        k_val = p.get("api_key", "").strip()
        status_txt = f"{k_val[:6]}...{k_val[-4:]}" if len(k_val) > 10 else ("[Tersimpan]" if k_val else "[Kosong]")
        items.append({"id": k, "label": p.get("name", k), "status": status_txt})
    items.append({"id": "back", "label": "⬅️ Kembali", "status": ""})

    sys.stdout.write("\033[?1049h\033[?25l\033[H\033[2J")
    sys.stdout.flush()

    try:
        tty.setraw(fd)
        sys.stdout.write("\033[?7l")
        sys.stdout.flush()

        while True:
            try:
                term_cols = os.get_terminal_size().columns
            except Exception:
                term_cols = 50
            width = max(34, min(term_cols - 2, 56))

            lines = []
            lines.append(f"\033[1;36m🔑  Kelola API Key Provider\033[0m{' ' * (width - 30)}\033[90m[Esc]\033[0m")
            lines.append(f"\033[90m{'─' * width}\033[0m")
            lines.append("")

            for idx, it in enumerate(items):
                is_sel = (idx == selected)
                pfx = "▸ " if is_sel else "  "
                avail = width - 4
                gap_s = avail - len(pfx) - len(it["label"]) - len(it["status"])
                if gap_s < 1: gap_s = 1
                row_str = f"{pfx}{it['label']}{' ' * gap_s}{it['status']}"
                if is_sel:
                    lines.append(f"\033[7m\033[1m {row_str:<{avail}} \033[0m")
                else:
                    lines.append(f"{pfx}\033[37m{it['label']}\033[0m{' ' * gap_s}\033[90m{it['status']}\033[0m")

            lines.append("")
            lines.append(f"\033[90m{'─' * width}\033[0m")
            lines.append(" \033[1;33m↑↓/Tab\033[0m \033[90mPilih\033[0m  \033[1;32mEnter\033[0m \033[90mUbah\033[0m  \033[90mEsc Kembali\033[0m")

            out_buf = ["\033[H"]
            for l in lines:
                out_buf.append(f"\r\033[2K{l}\r\n")
            out_buf.append("\r\033[J")
            sys.stdout.write("".join(out_buf))
            sys.stdout.flush()

            k = read_key_raw_fd(fd)
            if k in ('ESC', 'CTRL_C'):
                return

            elif k in ('UP', 'SHIFT_TAB'):
                selected = (selected - 1) % len(items)
            elif k in ('DOWN', 'TAB'):
                selected = (selected + 1) % len(items)
            elif k == 'ENTER':
                chosen_target = items[selected]["id"]
                break

    finally:
        sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if chosen_target != "back":
        curr_entry = providers[chosen_target]
        console.print(f"\n[bold yellow]Mengubah API Key untuk {curr_entry.get('name')}:[/bold yellow]")
        new_key = Prompt.ask("Masukkan API Key baru (atau tekan Enter/kosongkan untuk batal)", password=True).strip()
        if new_key:
            curr_entry["api_key"] = new_key
            save_full_config(full_cfg)
            console.print("[bold green]✔ API Key berhasil diperbarui![/bold green]\n")

def handle_permission_settings_interactive(full_cfg, auto_approve_ref):
    if not sys.stdin.isatty():
        return

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    selected = 0 if full_cfg.get("permission_mode") != "always_allow" else 1

    options = [
        {"id": "ask", "label": "🛡️ Selalu Minta Izin", "desc": "Tanya konfirmasi (y/n) setiap perintah shell"},
        {"id": "always", "label": "⚡ Selalu Diizinkan (Auto-Approve)", "desc": "Eksekusi perintah shell otomatis tanpa konfirmasi"},
        {"id": "back", "label": "⬅️ Batal / Kembali", "desc": "Kembali ke menu pengaturan"}
    ]

    sys.stdout.write("\033[?1049h\033[?25l\033[H\033[2J")
    sys.stdout.flush()

    try:
        tty.setraw(fd)
        sys.stdout.write("\033[?7l")
        sys.stdout.flush()

        while True:
            try:
                term_cols = os.get_terminal_size().columns
            except Exception:
                term_cols = 50
            width = max(34, min(term_cols - 2, 56))

            lines = []
            lines.append(f"\033[1;36m🛡️  Pengaturan Izin Shell\033[0m{' ' * (width - 28)}\033[90m[Esc]\033[0m")
            lines.append(f"\033[90m{'─' * width}\033[0m")
            lines.append("")

            for idx, opt in enumerate(options):
                is_sel = (idx == selected)
                pfx = "▸ " if is_sel else "  "
                avail = width - 4
                row_str = f"{pfx}{opt['label']}"
                if is_sel:
                    lines.append(f"\033[7m\033[1m {row_str:<{avail}} \033[0m")
                    lines.append(f"    \033[1;33m↳ {opt['desc']}\033[0m")
                else:
                    lines.append(f"{pfx}\033[37m{opt['label']}\033[0m")
                    lines.append(f"    \033[90m↳ {opt['desc']}\033[0m")
                lines.append("")

            lines.append(f"\033[90m{'─' * width}\033[0m")
            lines.append(" \033[1;33m↑↓/Tab\033[0m \033[90mPilih\033[0m  \033[1;32mEnter\033[0m \033[90mSimpan\033[0m  \033[90mEsc Batal\033[0m")

            out_buf = ["\033[H"]
            for l in lines:
                out_buf.append(f"\r\033[2K{l}\r\n")
            out_buf.append("\r\033[J")
            sys.stdout.write("".join(out_buf))
            sys.stdout.flush()

            k = read_key_raw_fd(fd)
            if k in ('ESC', 'CTRL_C'):
                return

            elif k in ('UP', 'SHIFT_TAB'):
                selected = (selected - 1) % len(options)
            elif k in ('DOWN', 'TAB'):
                selected = (selected + 1) % len(options)
            elif k == 'ENTER':
                chosen = options[selected]["id"]
                if chosen == "ask":
                    full_cfg["permission_mode"] = "ask"
                    full_cfg["auto_approve"] = False
                    if auto_approve_ref:
                        auto_approve_ref[0] = False
                    save_full_config(full_cfg)
                elif chosen == "always":
                    full_cfg["permission_mode"] = "always_allow"
                    full_cfg["auto_approve"] = True
                    if auto_approve_ref:
                        auto_approve_ref[0] = True
                    save_full_config(full_cfg)
                return

    finally:
        sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def handle_manage_memory_interactive():
    mem = load_memory()
    console.print(Panel(json.dumps(mem, indent=2), title="🧠 Memori Saat Ini", border_style="cyan"))
    console.print("\n[bold yellow]Opsi Memori:[/bold yellow]")
    console.print("  [bold cyan]1[/bold cyan]. Hapus Memori Global (~/.routers_memory.json)")
    console.print("  [bold cyan]2[/bold cyan]. Hapus Memori Proyek (.routers_project_memory.json)")
    console.print("  [bold cyan]3[/bold cyan]. Hapus Seluruh Memori (Global & Proyek)")
    console.print("  [bold red]0 / Esc[/bold red]. Kembali")

    sel = Prompt.ask("Pilih (0-3, e)", default="0").strip()
    if sel == "1":
        if os.path.exists(GLOBAL_MEMORY_FILE):
            os.remove(GLOBAL_MEMORY_FILE)
            console.print("[bold green]✔ Memori Global dihapus.[/bold green]")
    elif sel == "2":
        if os.path.exists(LOCAL_MEMORY_FILE):
            os.remove(LOCAL_MEMORY_FILE)
            console.print("[bold green]✔ Memori Proyek dihapus.[/bold green]")
    elif sel == "3":
        if os.path.exists(GLOBAL_MEMORY_FILE):
            os.remove(GLOBAL_MEMORY_FILE)
        if os.path.exists(LOCAL_MEMORY_FILE):
            os.remove(LOCAL_MEMORY_FILE)
        console.print("[bold green]✔ Seluruh memori berhasil dibersihkan.[/bold green]")
    elif sel in ("0", "e", "esc"):
        return

def handle_test_connection():
    cfg = get_active_config()
    url = f"{cfg['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": "ping"}]
    }

    console.print(f"\n[cyan]🧪 Menguji koneksi ke[/cyan] [bold white]{url}[/bold white] (Model: [yellow]{cfg['model']}[/yellow])...")
    start_t = time.time()
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        elapsed = round((time.time() - start_t) * 1000, 2)
        if resp.status_code == 200:
            console.print(f"[bold green]✔ KONEKSI SUKSES![/bold green] (Status: 200 OK, Latency: [bold yellow]{elapsed} ms[/bold yellow])")
        else:
            console.print(f"[bold yellow]⚠️ Respon Server:[/bold yellow] Status {resp.status_code} ({resp.text[:120]}) [Latency: {elapsed} ms]")
    except Exception as e:
        console.print(f"[bold red]❌ Gagal terhubung ke API:[/bold red] {str(e)}")

def handle_system_diagnostics(cfg, auto_approve_ref):
    table = Table(title="📋 Diagnostik Sistem & Environment", header_style="bold cyan")
    table.add_column("Komponen", style="bold yellow")
    table.add_column("Nilai / Status", style="white")

    table.add_row("Agent Version", "r.outers v2.0 (Termux & Linux)")
    table.add_row("Python Version", sys.version.split()[0])
    table.add_row("Current Directory", os.getcwd())
    table.add_row("Config File", CONFIG_FILE)
    table.add_row("Active Provider", cfg.get("provider_name", "N/A"))
    table.add_row("Active Model", cfg.get("model", "N/A"))
    table.add_row("Base URL", cfg.get("base_url", "N/A"))
    table.add_row("API Key Configured", "Ya" if cfg.get("api_key") else "Tidak")
    is_auto = auto_approve_ref[0] if auto_approve_ref else False
    table.add_row("Izin Shell (Auto-Approve)", "[bold green]Aktif (Selalu Izinkan)[/bold green]" if is_auto else "[yellow]Minta Izin (y/n)[/yellow]")

    console.print("\n")
    console.print(table)

def handle_factory_reset():
    confirm = Confirm.ask("[bold red]⚠️ Yakin ingin mereset seluruh konfigurasi r.outers ke default pabrik?[/bold red]")
    if confirm:
        initial = setup_initial_config()
        save_full_config(initial)
        console.print("[bold green]✔ Konfigurasi berhasil direset ke setelan awal pabrik (Clouvia & Atria ASI)![/bold green]\n")
