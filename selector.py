import os
import sys
import select
import tty
import termios
from ui import console
from config import (
    load_full_config, save_full_config, update_active_model,
    add_new_provider, switch_provider, PRESET_PROVIDERS
)
from model_fetcher import get_all_available_models, fetch_provider_models

def read_key_raw_fd(fd):
    try:
        raw = os.read(fd, 4096)
    except Exception:
        return None
    if not raw:
        return None

    if b'\x1b[200~' in raw:
        raw = raw.replace(b'\x1b[200~', b'').replace(b'\x1b[201~', b'')

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
    if raw == b'\x01':  # Ctrl+A
        return 'CTRL_A'
    if raw == b'\x06':  # Ctrl+F
        return 'CTRL_F'
    if raw == b'\x12':  # Ctrl+R
        return 'CTRL_R'
    if raw == b'\x03':  # Ctrl+C
        return 'CTRL_C'
    if raw == b'\x04':  # Ctrl+D
        return 'CTRL_D'
    if raw == b'\x15':  # Ctrl+U
        return 'CTRL_U'

    try:
        decoded = raw.decode('utf-8', errors='ignore')
        printable_text = ''.join(c for c in decoded if c.isprintable() or c == ' ')
        if printable_text:
            return printable_text
    except Exception:
        pass
    return None

def get_tag_color(tag):
    mapping = {
        "FREE": "\033[1;32m",
        "AUTO": "\033[1;32m",
        "CODE": "\033[1;36m",
        "FAST": "\033[1;33m",
        "SMART": "\033[1;35m",
        "REASON": "\033[1;34m",
        "TOP": "\033[1;31m",
        "SPEED": "\033[1;33m",
        "LOCAL": "\033[1;37m",
        "SETUP": "\033[1;33m",
        "CUSTOM": "\033[36m"
    }
    return mapping.get(tag, "\033[37m")

def render_frame_lines(query, filtered_items, selected_idx, scroll_offset, max_visible, width, active_model_id, is_loading=False):
    lines = []
    
    # Header bar
    title = "⚡ r.outers Model"
    badge = "[Refreshing...]" if is_loading else f"[{len(filtered_items)}]"
    esc_label = "[Esc]"
    
    gap = width - len(title) - len(badge) - len(esc_label) - 2
    if gap < 1: gap = 1
    lines.append(f"\033[1;36m{title}\033[0m{' ' * gap}\033[1;33m{badge}\033[0m \033[90m{esc_label}\033[0m")
    lines.append(f"\033[90m{'─' * width}\033[0m")

    # Search query
    cursor = "\033[1;36m▌\033[0m"
    if query:
        lines.append(f" \033[1;33m🔍\033[0m \033[1;37m{query}\033[0m{cursor}")
    else:
        lines.append(f" \033[1;33m🔍\033[0m \033[90m(ketik nama model / filter...)\033[0m {cursor}")
    
    lines.append(f"\033[90m{'─' * width}\033[0m")

    # Visible items
    visible_slice = filtered_items[scroll_offset:scroll_offset + max_visible]
    for idx_in_slice, item in enumerate(visible_slice):
        actual_idx = scroll_offset + idx_in_slice
        is_selected = (actual_idx == selected_idx)
        is_active = (item.get("id") == active_model_id)
        
        name = item["name"]
        prov = item["provider_name"]
        tag = item.get("tag", "AI")
        tag_col = get_tag_color(tag)

        prefix = "▸ " if is_selected else "  "
        active_mark = " ●" if is_active else ""
        
        left_label = f"{name}{active_mark}"
        
        # Always show tag; include short provider name if terminal is wide enough
        prov_short = prov.split()[0] if prov else ""
        if width >= 48:
            right_label = f"{prov_short} [{tag}]"
            right_colored = f"{prov_short} {tag_col}[{tag}]\033[0m"
        else:
            right_label = f"[{tag}]"
            right_colored = f"{tag_col}[{tag}]\033[0m"

        avail_w = width - 2
        needed_len = len(prefix) + len(left_label) + len(right_label) + 2
        if needed_len > avail_w:
            max_left = avail_w - len(prefix) - len(right_label) - 3
            if max_left > 4:
                left_label = left_label[:max_left - 1] + ".."
            else:
                left_label = left_label[:max_left]
        
        spacing = avail_w - len(prefix) - len(left_label) - len(right_label)
        if spacing < 1: spacing = 1

        if is_selected:
            content_left = f"{prefix}{left_label}"
            row_full = f"{content_left}{' ' * spacing}{right_label}"
            lines.append(f"\033[7m\033[1m {row_full:<{avail_w}} \033[0m")
        else:
            dim_right = f"\033[90m{right_colored}\033[0m"
            lines.append(f"{prefix}\033[37m{left_label}\033[0m{' ' * spacing}{dim_right}")

    # Empty slots
    remaining = max_visible - len(visible_slice)
    for _ in range(remaining):
        lines.append("")

    # Footer
    lines.append(f"\033[90m{'─' * width}\033[0m")
    if width >= 50:
        footer = " \033[1;33m↑↓/Tab\033[0m \033[90mPilih\033[0m \033[1;32mEnter\033[0m \033[90mPakai\033[0m \033[1;36m^R\033[0m \033[90mRefresh\033[0m \033[1;35m^A\033[0m \033[90m+API\033[0m"
    elif width >= 40:
        footer = " \033[1;33m↑↓\033[0m \033[90mPilih\033[0m \033[1;32mEnter\033[0m \033[90mPakai\033[0m \033[1;36m^R\033[0m \033[90mRef\033[0m \033[1;35m^A\033[0m \033[90m+API\033[0m"
    else:
        footer = " \033[1;33m↑↓\033[0m \033[90mPilih\033[0m \033[1;32mEnter\033[0m \033[90mPakai\033[0m \033[1;35m^A\033[0m \033[90m+API\033[0m"
    lines.append(footer)
    
    return lines

def is_cancel_input(val):
    if val is None:
        return True
    val_clean = str(val).strip().lower()
    return (
        val_clean in ("e", "esc", "q", "exit", "batal", "back", "\x1b", "^[", "^[^[", "^[^[^[", "^[^[^[^[")
        or "\x1b" in val_clean
        or "^[" in val_clean
        or val_clean.startswith("^")
    )

def test_model_connectivity(base_url, api_key, model_id, timeout=8):
    """
    Performs a lightweight verification ping to check if 9Router / provider can serve the model.
    Returns (True, "OK") or (False, error_message).
    """
    import requests
    try:
        url = base_url.rstrip("/")
        if not url.endswith("/v1"):
            url = f"{url}/v1"
        r = requests.post(
            f"{url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 1
            },
            timeout=timeout
        )
        if r.status_code == 200:
            return True, "OK"
        else:
            try:
                err_data = r.json()
                msg = err_data.get("error", {}).get("message") or err_data.get("error") or r.text
            except Exception:
                try:
                    err_data, _ = json.JSONDecoder().raw_decode(r.text.strip())
                    msg = err_data.get("error", {}).get("message") or err_data.get("error") or r.text
                except Exception:
                    msg = r.text
            return False, f"HTTP {r.status_code}: {msg}"
    except Exception as e:
        return False, str(e)

def prompt_text_with_esc(prompt_text, default="", mask=False):

    """
    Interactive text input that handles physical/virtual ESC key immediately without printing '^['
    and supports inline editing, backspace, and default value.
    Uses clean multi-line layout to prevent text duplication on mobile/narrow screens.
    """
    if not sys.stdin.isatty():
        try:
            def_str = f" ({default})" if default else ""
            val = input(f"{prompt_text}{def_str}: ").strip()
            return val if val else default
        except Exception:
            return None

    # 1. Print prompt description once on its own line
    clean_prompt = prompt_text.strip()
    sys.stdout.write(f"\n{clean_prompt}\n")
    if default:
        sys.stdout.write(f"  \033[90m[Default: {default}]\033[0m\n")

    # 2. Input prompt line (short prefix ensures line clearing never wraps)
    input_prefix = "  \033[1;32m❯\033[0m "
    sys.stdout.write(f"\r\033[2K{input_prefix}")
    sys.stdout.flush()

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    buffer = ""

    try:
        tty.setraw(fd)
        while True:
            k = read_key_raw_fd(fd)
            if k in ('ESC', 'CTRL_C'):
                sys.stdout.write(f"\r\033[2K  \033[90m(Batal)\033[0m\r\n\n")
                sys.stdout.flush()
                return None
            elif k in ('ENTER',):
                final_val = buffer.strip() if buffer.strip() else default
                disp_val = ("*" * len(final_val)) if (mask and final_val) else final_val
                sys.stdout.write(f"\r\033[2K{input_prefix}\033[1;33m{disp_val}\033[0m\r\n\n")
                sys.stdout.flush()
                return final_val
            elif k in ('BACKSPACE',):
                if buffer:
                    buffer = buffer[:-1]
            elif k in ('CTRL_U',):
                buffer = ""
            elif k and isinstance(k, str) and not k.startswith(('UP', 'DOWN', 'LEFT', 'RIGHT', 'TAB', 'PAGE_', 'SHIFT_', 'CTRL_')):
                buffer += k

            disp_b = ("*" * len(buffer)) if (mask and buffer) else buffer
            sys.stdout.write(f"\r\033[2K{input_prefix}\033[1;33m{disp_b}\033[0m")
            sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def setup_9router_interactive(current_config=None):
    from config import get_active_config
    console.print("\n[bold cyan]⚡ Setup & Hubungkan 9Router[/bold cyan] [dim](Tekan Esc atau ketik 'e' untuk batal)[/dim]")
    console.print("[dim]Masukkan URL domain 9Router Anda (misal Railway/VPS), API Key, dan pilih Model AI.[/dim]\n")

    full_cfg = load_full_config()
    providers = full_cfg.get("providers", {})
    existing_9r = providers.get("9router", {})

    try:
        # 1. Masukkan Domain / Base URL
        def_url = existing_9r.get("base_url", "")
        raw_url = prompt_text_with_esc(
            "\033[1;36m1. Masukkan Domain / Base URL 9Router\033[0m \033[90m(Esc/e: batal)\033[0m",
            default=def_url if def_url else ""
        )
        
        if raw_url is None or is_cancel_input(raw_url) or not raw_url.strip():
            console.print("[yellow]Batal setup 9Router.[/yellow]\n")
            return current_config or get_active_config()

        raw_url = raw_url.strip()
        if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
            raw_url = "https://" + raw_url
        raw_url = raw_url.rstrip("/")
        if not raw_url.endswith("/v1"):
            raw_url = f"{raw_url}/v1"
        base_url = raw_url

        # 2. Masukkan API Key
        def_key = existing_9r.get("api_key", "")
        api_key = prompt_text_with_esc(
            "\033[1;36m2. Masukkan / Paste API Key 9Router\033[0m \033[90m(Esc/e: batal)\033[0m",
            default=def_key if def_key else "",
            mask=True
        )

        if api_key is None or is_cancel_input(api_key) or not api_key.strip():
            console.print("[yellow]Batal setup 9Router (API Key kosong atau dibatalkan).[/yellow]\n")
            return current_config or get_active_config()

        api_key = api_key.strip()

        # 3. Auto-fetch live models and validate model
        console.print("\n[dim]⏳ Mengambil & memverifikasi katalog model aktif dari 9Router...[/dim]")
        from model_fetcher import fetch_provider_models
        live_models = fetch_provider_models("9router", base_url=base_url, api_key=api_key, force_refresh=True)

        suggested_model = "ag/gemini-3.7-flash-high"
        model_ids = []
        if live_models:
            model_ids = [m["id"] for m in live_models]
            if existing_9r.get("model") in model_ids:
                suggested_model = existing_9r.get("model")
            elif any("gemini-3.7-flash" in m["id"] for m in live_models):
                suggested_model = next(m["id"] for m in live_models if "gemini-3.7-flash" in m["id"])
            elif any("gemini" in m["id"] for m in live_models):
                suggested_model = next(m["id"] for m in live_models if "gemini" in m["id"])
            else:
                suggested_model = model_ids[0]

            console.print(f"[bold green]✔ Berhasil terhubung! Terdeteksi {len(live_models)} model terdaftar di 9Router.[/bold green]")
            preview_list = ", ".join(model_ids[:6])
            if len(model_ids) > 6:
                preview_list += f", ... (+{len(model_ids)-6} lainnya)"
            console.print(f"[dim]Contoh model tersedia: {preview_list}[/dim]\n")
        else:
            console.print("[yellow]⚠ Catatan: Tidak dapat mengambil katalog live secara otomatis, masukkan nama model secara manual.[/yellow]\n")

        chosen_model = None
        while True:
            raw_model = prompt_text_with_esc(
                "\033[1;36m3. Masukkan Model AI yang Ingin Digunakan\033[0m \033[90m(Esc/e: batal)\033[0m",
                default=suggested_model
            )

            if raw_model is None or is_cancel_input(raw_model) or not raw_model.strip():
                console.print("[yellow]Batal setup 9Router.[/yellow]\n")
                return current_config or get_active_config()

            candidate = raw_model.strip()

            if live_models and model_ids:
                if candidate in model_ids:
                    console.print(f"[dim]⏳ Menguji verifikasi model '{candidate}'...[/dim]")
                    ok, detail = test_model_connectivity(base_url, api_key, candidate)
                    if ok:
                        console.print(f"[bold green]✔ Model '{candidate}' terverifikasi aktif & siap digunakan![/bold green]")
                        chosen_model = candidate
                        break
                    else:
                        console.print(f"\n[bold red]❌ Model '{candidate}' terdaftar namun belum memiliki API Key aktif di 9Router:[/bold red]")
                        console.print(f"[yellow]Pesan 9Router: {detail}[/yellow]")
                        console.print(f"[dim]Silakan tambahkan API key provider terkait di dashboard 9Router, atau gunakan model dengan credentials aktif (misal ag/gemini-3.7-flash-high).[/dim]\n")
                        suggested_model = next((m for m in model_ids if m.startswith("ag/")), model_ids[0])
                        continue

                # Check suffix / prefix match
                matched_id = None
                for m_id in model_ids:
                    if m_id.endswith(f"/{candidate}") or candidate.endswith(f"/{m_id}") or m_id.lower() == candidate.lower():
                        matched_id = m_id
                        break

                if matched_id:
                    console.print(f"[bold cyan]🔍 Model dicocokkan ke ID resmi: [bold yellow]{matched_id}[/bold yellow][/bold cyan]")
                    console.print(f"[dim]⏳ Menguji verifikasi model '{matched_id}'...[/dim]")
                    ok, detail = test_model_connectivity(base_url, api_key, matched_id)
                    if ok:
                        console.print(f"[bold green]✔ Model '{matched_id}' terverifikasi aktif & siap digunakan![/bold green]")
                        chosen_model = matched_id
                        break
                    else:
                        console.print(f"\n[bold red]❌ Model '{matched_id}' gagal diakses: {detail}[/bold red]")
                        console.print("[yellow]Model ini belum memiliki API key di dashboard 9Router. Pilih model lain yang aktif.[/yellow]\n")
                        suggested_model = next((m for m in model_ids if m.startswith("ag/")), model_ids[0])
                        continue

                # Not found at all
                console.print(f"\n[bold red]❌ Model '{candidate}' TIDAK DITEMUKAN di katalog 9Router Anda![/bold red]")
                console.print(f"[yellow]Daftar model aktif yang dapat digunakan:[/yellow]")
                for idx_m, m_id in enumerate(model_ids[:10], 1):
                    console.print(f"  {idx_m}. [bold cyan]{m_id}[/bold cyan]")
                if len(model_ids) > 10:
                    console.print(f"  [dim]... dan {len(model_ids)-10} model lainnya[/dim]")
                console.print("[dim]Ketik salah satu model di atas (misal ag/gemini-3.7-flash-high).[/dim]\n")
                suggested_model = next((m for m in model_ids if m.startswith("ag/")), model_ids[0])
                continue
            else:
                console.print(f"[dim]⏳ Menguji akses model '{candidate}' ke 9Router...[/dim]")
                ok, detail = test_model_connectivity(base_url, api_key, candidate)
                if ok:
                    console.print(f"[bold green]✔ Model '{candidate}' terverifikasi aktif![/bold green]")
                    chosen_model = candidate
                    break
                else:
                    console.print(f"[bold red]⚠ Akses model '{candidate}' gagal: {detail}[/bold red]")
                    from rich.prompt import Confirm
                    if Confirm.ask(f"[yellow]Tetap gunakan model '{candidate}' meskipun belum terverifikasi?[/yellow]", default=False):
                        chosen_model = candidate
                        break
                    else:
                        continue

        model = chosen_model


    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Batal setup 9Router.[/yellow]\n")
        return current_config or get_active_config()

    providers["9router"] = {
        "name": "9Router",
        "base_url": base_url,
        "api_key": api_key,
        "model": model
    }
    full_cfg["active_provider"] = "9router"
    full_cfg["providers"] = providers
    save_full_config(full_cfg)

    console.print(f"\n[bold green]✔ 9Router berhasil dihubungkan dan diaktifkan![/bold green]")
    console.print(f"  • Base URL: [cyan]{base_url}[/cyan]")
    console.print(f"  • Model Aktif: [bold yellow]{model}[/bold yellow]\n")

    return get_active_config()

def prompt_add_custom_model_interactive(provider_id=None, current_config=None, initial_model_id=""):
    from config import load_full_config, save_full_config, get_active_config, add_custom_model, is_thinking_supported
    
    full_cfg = load_full_config()
    if provider_id is None:
        provider_id = full_cfg.get("active_provider", "9router")
    providers = full_cfg.get("providers", {})
    prov_name = providers.get(provider_id, {}).get("name", provider_id.capitalize())

    console.print(f"\n[bold cyan]➕ Tambah Model Custom Baru ([yellow]{prov_name}[/yellow])[/bold cyan]")
    try:
        model_id = prompt_text_with_esc(
            "\033[1;36mMasukkan ID / Nama Model\033[0m \033[90m(Esc/e: batal)\033[0m",
            default=initial_model_id
        )
    except (KeyboardInterrupt, EOFError):
        return current_config or get_active_config()

    if model_id is None or is_cancel_input(model_id) or not model_id.strip():
        console.print("[yellow]Batal menambah model.[/yellow]\n")
        return current_config or get_active_config()

    model_id = model_id.strip()

    try:
        display_name = prompt_text_with_esc(
            "\033[1;36mNama Tampilan (Opsional)\033[0m \033[90m(tekan Enter untuk default)\033[0m",
            default=model_id
        )
    except (KeyboardInterrupt, EOFError):
        display_name = model_id

    display_name = display_name.strip() if (display_name and display_name.strip()) else model_id

    add_custom_model(model_id, provider_id=provider_id, name=display_name, tag="CUSTOM", set_as_active=True)
    
    cfg = get_active_config()
    cfg["model"] = model_id

    # Invalidate model cache so it refreshes immediately
    from model_fetcher import fetch_provider_models
    try:
        fetch_provider_models(provider_id, force_refresh=True)
    except Exception:
        pass
    
    if is_thinking_supported(model_id):
        return select_thinking_interactive(cfg, model_name_display=display_name, provider_name_display=prov_name, is_inline=True)
    else:
        console.print(f"[bold green]✔ Model custom '[yellow]{display_name}[/yellow]' ([cyan]{model_id}[/cyan]) berhasil disimpan dan diaktifkan![/bold green]\n")
        return cfg

def show_9router_hub_interactive(current_config=None):
    from rich.prompt import Prompt
    from config import load_full_config, save_full_config, get_active_config

    if not sys.stdin.isatty():
        return current_config or get_active_config()

    full_cfg = load_full_config()
    providers = full_cfg.get("providers", {})
    entry = providers.get("9router", {})

    url = entry.get("base_url", "")
    key = entry.get("api_key", "")
    model = entry.get("model", "oc/space-bunny-free")
    is_active = (full_cfg.get("active_provider") == "9router")

    key_masked = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else ("[Tersimpan]" if key else "[Belum Diisi]")
    active_badge_str = "● SEDANG AKTIF" if is_active else "○ Standby"

    menu_items = [
        {
            "id": "setup_all",
            "name": "🌐 Setup Lengkap",
            "desc": "Konfigurasi Domain URL, API Key & Model sekaligus",
            "tag": "SETUP",
            "color": "\033[1;36m"
        },
        {
            "id": "change_url",
            "name": "🔗 Ubah Domain / Base URL Saja",
            "desc": "Ganti URL endpoint 9Router (Railway / Custom Domain)",
            "tag": "URL",
            "color": "\033[1;33m"
        },
        {
            "id": "change_key",
            "name": "🔑 Ubah API Key Saja",
            "desc": "Update atau paste API Key 9Router baru",
            "tag": "KEY",
            "color": "\033[1;32m"
        },
        {
            "id": "select_model",
            "name": "🤖 Pilih / Ganti Model AI",
            "desc": "Live API Model Discovery dari katalog 9Router",
            "tag": "MODEL",
            "color": "\033[1;35m"
        },
        {
            "id": "add_model",
            "name": "➕ Tambah Model Custom Baru",
            "desc": "Tambahkan ID model AI baru ke katalog 9Router & aktifkan",
            "tag": "ADD",
            "color": "\033[1;32m"
        },
        {
            "id": "activate",
            "name": "⚡ Aktifkan Sebagai Provider Utama",
            "desc": "Jadikan 9Router sebagai AI Provider aktif di r.outers",
            "tag": "ACTIVE",
            "color": "\033[1;32m"
        },
        {
            "id": "ping_test",
            "name": "🧪 Test Koneksi & Ping API",
            "desc": "Uji latency & responsivitas endpoint 9Router",
            "tag": "PING",
            "color": "\033[1;34m"
        },
        {
            "id": "back",
            "name": "⬅️ Kembali ke Chat",
            "desc": "Keluar dari menu 9Router Hub",
            "tag": "ESC",
            "color": "\033[90m"
        }
    ]

    selected_idx = 0
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    sys.stdout.write("\033[?1049h\033[?25l\033[H\033[2J")
    sys.stdout.flush()

    chosen = None
    try:
        tty.setraw(fd)
        sys.stdout.write("\033[?7l")
        sys.stdout.flush()

        while True:
            try:
                term_cols = os.get_terminal_size().columns
            except Exception:
                term_cols = 52
            width = max(38, min(term_cols - 2, 64))

            lines = []
            title_tag = "⚡ 9Router Management Hub"
            gap_t = max(1, width - len(title_tag) - 7)
            lines.append(f"\033[1;36m{title_tag}\033[0m{' ' * gap_t}\033[90m[Esc]\033[0m")

            # Status bar
            badge_color = "\033[1;32m" if is_active else "\033[90m"
            status_line = f"\033[90mStatus: {badge_color}[{active_badge_str}]\033[0m"
            lines.append(status_line)

            # Details
            disp_url = url if url else "[Belum Dikonfigurasi]"
            if len(disp_url) > width - 12:
                disp_url = disp_url[:width - 15] + "..."
            lines.append(f"\033[90m• URL   : \033[1;36m{disp_url}\033[0m")
            lines.append(f"\033[90m• Key   : \033[1;33m{key_masked}\033[0m  \033[90mModel:\033[0m \033[1;33m{model}\033[0m")
            lines.append(f"\033[90m{'─' * width}\033[0m")
            lines.append("")

            for idx, item in enumerate(menu_items):
                is_sel = (idx == selected_idx)
                pfx = "▸ " if is_sel else "  "
                tag_badge = f"{item['color']}[{item['tag']}]\033[0m " if item["tag"] else ""

                avail_w = width - 4
                row_txt = f"{pfx}{tag_badge}\033[1m{item['name']}\033[0m"
                desc_line = f"     \033[90m{item['desc']}\033[0m"

                if is_sel:
                    lines.append(f"\033[7m\033[1m {row_txt:<{avail_w}} \033[0m")
                    if item["id"] != "back":
                        lines.append(f"\033[7m {desc_line:<{avail_w}} \033[0m")
                else:
                    lines.append(f" {row_txt}")
                    if item["id"] != "back":
                        lines.append(f" {desc_line}")
                lines.append("")

            lines.append(f"\033[90m{'─' * width}\033[0m")
            lines.append(f" \033[1;33m↑↓/Tab\033[0m \033[90mPilih\033[0m  \033[1;32mEnter\033[0m \033[90mEksekusi\033[0m  \033[90mEsc Kembali\033[0m")

            out_buf = ["\033[H"]
            for l in lines:
                out_buf.append(f"\r\033[2K{l}\r\n")
            out_buf.append("\r\033[J")
            sys.stdout.write("".join(out_buf))
            sys.stdout.flush()

            k = read_key_raw_fd(fd)
            if k in ('ESC', 'CTRL_C', 'e', 'E', 'q', 'Q'):
                chosen = "back"
                break
            elif k in ('UP', 'SHIFT_TAB'):
                selected_idx = (selected_idx - 1) % len(menu_items)
            elif k in ('DOWN', 'TAB'):
                selected_idx = (selected_idx + 1) % len(menu_items)
            elif k == 'ENTER':
                chosen = menu_items[selected_idx]["id"]
                break
            elif k in ('1', '2', '3', '4', '5', '6', '7', '8'):
                num_idx = int(k) - 1
                if 0 <= num_idx < len(menu_items):
                    selected_idx = num_idx
                    chosen = menu_items[selected_idx]["id"]
                    break
    finally:
        sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if not chosen or chosen == "back":
        console.print("[yellow]Kembali ke mode chat.[/yellow]\n")
        return current_config or get_active_config()

    if chosen == "setup_all":
        return setup_9router_interactive(current_config)
    elif chosen == "change_url":
        def_url = entry.get("base_url", "")
        raw_url = prompt_text_with_esc(
            "\033[1;36mMasukkan Domain / Base URL 9Router baru\033[0m \033[90m(Esc/e: batal)\033[0m",
            default=def_url if def_url else ""
        )
        if raw_url is not None and not is_cancel_input(raw_url) and raw_url.strip():
            raw_url = raw_url.strip()
            if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
                raw_url = "https://" + raw_url
            raw_url = raw_url.rstrip("/")
            if not raw_url.endswith("/v1"):
                raw_url = f"{raw_url}/v1"
            entry["base_url"] = raw_url
            providers["9router"] = entry
            full_cfg["providers"] = providers
            save_full_config(full_cfg)
            console.print(f"[bold green]✔ Base URL 9Router diperbarui ke:[/bold green] [cyan]{raw_url}[/cyan]\n")
        else:
            console.print("[yellow]Batal mengubah URL.[/yellow]\n")
        return get_active_config()
    elif chosen == "change_key":
        def_key = entry.get("api_key", "")
        raw_key = prompt_text_with_esc(
            "\033[1;36mMasukkan / Paste API Key 9Router baru\033[0m \033[90m(Esc/e: batal)\033[0m",
            default=def_key if def_key else "",
            mask=True
        )
        if raw_key is not None and not is_cancel_input(raw_key) and raw_key.strip():
            raw_key = raw_key.strip()
            entry["api_key"] = raw_key
            providers["9router"] = entry
            full_cfg["providers"] = providers
            save_full_config(full_cfg)
            console.print(f"[bold green]✔ API Key 9Router berhasil diperbarui![/bold green]\n")
        else:
            console.print("[yellow]Batal mengubah API Key.[/yellow]\n")
        return get_active_config()
    elif chosen == "select_model":
        if not url or not key:
            console.print("[bold yellow]⚠ URL atau API Key 9Router belum dikonfigurasi. Menjalankan setup lengkap...[/bold yellow]")
            return setup_9router_interactive(current_config)
        console.print("\n[dim]⏳ Mengambil katalog model live dari 9Router...[/dim]")
        from model_fetcher import fetch_provider_models
        live_models = fetch_provider_models("9router", base_url=url, api_key=key, force_refresh=True)
        if live_models:
            full_cfg["active_provider"] = "9router"
            save_full_config(full_cfg)
            return select_model_interactive(get_active_config())
        else:
            return prompt_add_custom_model_interactive(provider_id="9router", current_config=current_config, initial_model_id=model)
    elif chosen == "add_model":
        return prompt_add_custom_model_interactive(provider_id="9router", current_config=current_config)
    elif chosen == "activate":
        if not url or not key:
            console.print("[bold yellow]⚠ URL atau API Key 9Router belum lengkap. Menjalankan setup...[/bold yellow]")
            return setup_9router_interactive(current_config)
        full_cfg["active_provider"] = "9router"
        save_full_config(full_cfg)
        console.print("[bold green]✔ 9Router berhasil diaktifkan sebagai provider utama![/bold green]\n")
        return get_active_config()
    elif chosen == "ping_test":
        if not url or not key:
            console.print("[bold yellow]⚠ URL atau API Key 9Router belum diisi.[/bold yellow]\n")
            return get_active_config()
        console.print(f"\n[dim]⏳ Melakukan test ping ke {url}...[/dim]")
        import time, requests
        t0 = time.time()
        try:
            r = requests.post(f"{url}/chat/completions", headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }, json={
                "model": model,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 5
            }, timeout=15)
            dt = (time.time() - t0) * 1000
            if r.status_code == 200:
                console.print(f"[bold green]✔ Test Berhasil! (Latency: {dt:.0f}ms, Status: 200 OK)[/bold green]")
                console.print(f"  • Endpoint: [cyan]{url}[/cyan]")
                console.print(f"  • Model Digunakan: [bold yellow]{model}[/bold yellow]\n")
            else:
                console.print(f"[bold red]✘ Gagal (HTTP {r.status_code}):[/bold red] {r.text}\n")
        except Exception as e:
            console.print(f"[bold red]✘ Gagal menghubungi 9Router:[/bold red] {e}\n")
        return get_active_config()

    return get_active_config()

def select_model_interactive(current_config):
    if not sys.stdin.isatty():
        return current_config

    models = get_all_available_models(current_config=current_config)
    query = ""
    selected_idx = 0
    scroll_offset = 0
    filter_favorites = False
    active_model_id = current_config.get("model", "")
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    # Masuk ke Alternate Screen Buffer (\033[?1049h) & sembunyikan cursor (\033[?25l)
    sys.stdout.write("\033[?1049h\033[?25l\033[H\033[2J")
    sys.stdout.flush()

    try:
        tty.setraw(fd)

        # Matikan auto-wrap terminal saat modal tampil untuk menghindari glitch
        sys.stdout.write("\033[?7l")
        sys.stdout.flush()

        while True:
            # Ambil ukuran terminal dinamis per frame
            try:
                term_cols = os.get_terminal_size().columns
                term_lines = os.get_terminal_size().lines
            except Exception:
                term_cols, term_lines = 42, 24

            # Batasi lebar agar pas di layar HP / Termux
            modal_width = max(32, min(term_cols - 2, 58))
            max_visible = max(4, min(term_lines - 8, 14))

            # Filter model
            q_clean = query.strip().lower()
            filtered = []
            for m in models:
                if filter_favorites and not m.get("fav"):
                    continue
                if (not q_clean or 
                    q_clean in m["name"].lower() or 
                    q_clean in m["id"].lower() or 
                    q_clean in m["provider_name"].lower() or 
                    q_clean in m.get("tag", "").lower()):
                    filtered.append(m)

            if not filtered:
                filtered = [{
                    "name": f"Gunakan '{query}'",
                    "id": query if query else "custom",
                    "provider_id": current_config.get("provider_id", "9router"),
                    "provider_name": "Custom",
                    "tag": "CUSTOM",
                    "fav": False
                }]

            # Bounds check
            if selected_idx >= len(filtered):
                selected_idx = max(0, len(filtered) - 1)
            if selected_idx < 0:
                selected_idx = 0

            # Scroll offset check
            if selected_idx < scroll_offset:
                scroll_offset = selected_idx
            elif selected_idx >= scroll_offset + max_visible:
                scroll_offset = selected_idx - max_visible + 1

            # Render frame ke alternate screen dari posisi Home (\033[H)
            frame_lines = render_frame_lines(query, filtered, selected_idx, scroll_offset, max_visible, modal_width, active_model_id)
            
            output_buffer = ["\033[H"]
            for line in frame_lines:
                output_buffer.append(f"\r\033[2K{line}\r\n")
            
            output_buffer.append("\r\033[J")
            sys.stdout.write("".join(output_buffer))
            sys.stdout.flush()

            k = read_key_raw_fd(fd)

            if k in ('ESC', 'CTRL_C'):
                break

            elif k in ('UP', 'SHIFT_TAB'):
                if selected_idx > 0:
                    selected_idx -= 1
                else:
                    selected_idx = len(filtered) - 1

            elif k in ('DOWN', 'TAB'):
                if selected_idx < len(filtered) - 1:
                    selected_idx += 1
                else:
                    selected_idx = 0

            elif k == 'PAGE_UP':
                selected_idx = max(0, selected_idx - max_visible)

            elif k == 'PAGE_DOWN':
                selected_idx = min(len(filtered) - 1, selected_idx + max_visible)

            elif k == 'BACKSPACE':
                if query:
                    query = query[:-1]
                    selected_idx = 0
                    scroll_offset = 0

            elif k == 'CTRL_U':
                query = ""
                selected_idx = 0
                scroll_offset = 0

            elif k == 'CTRL_F':
                filter_favorites = not filter_favorites
                selected_idx = 0
                scroll_offset = 0

            elif k == 'CTRL_R':
                # Force refresh models from active provider API
                models = get_all_available_models(current_config=current_config, force_refresh=True)
                selected_idx = 0
                scroll_offset = 0

            elif k == 'CTRL_A':
                # Restore terminal sebelum membuka dialog provider
                sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
                sys.stdout.flush()
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return add_new_provider()

            elif k == 'ENTER':
                chosen = filtered[selected_idx]
                target_model_id = chosen["id"]
                target_prov_id = chosen["provider_id"]

                # Restore terminal
                sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
                sys.stdout.flush()
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

                if target_model_id == "setup_9router":
                    return setup_9router_interactive(current_config)

                if target_model_id == "add_custom_model":
                    return prompt_add_custom_model_interactive(provider_id=target_prov_id, current_config=current_config)

                if chosen.get("tag") == "CUSTOM" and not chosen.get("fav") and target_model_id not in ("setup_9router", "add_custom_model"):
                    return prompt_add_custom_model_interactive(provider_id=target_prov_id, current_config=current_config, initial_model_id=target_model_id)

                full_cfg = load_full_config()
                providers = full_cfg.get("providers", {})

                if target_prov_id == "9router" and (not providers.get("9router", {}).get("base_url") or not providers.get("9router", {}).get("api_key")):
                    return setup_9router_interactive(current_config)
                
                if target_prov_id not in providers and target_prov_id in PRESET_PROVIDERS:
                    preset = PRESET_PROVIDERS[target_prov_id]
                    providers[target_prov_id] = {
                        "name": preset["name"],
                        "base_url": preset["base_url"],
                        "api_key": "",
                        "model": target_model_id
                    }

                if target_prov_id in providers:
                    prov_entry = providers[target_prov_id]
                    prov_name = prov_entry.get("name", target_prov_id)
                    existing_api_key = prov_entry.get("api_key", "").strip()
                    
                    # Auto-check dari environment variables
                    if not existing_api_key:
                        from config import load_env_keys
                        env_keys = load_env_keys()
                        if target_prov_id == "9router":
                            existing_api_key = env_keys.get("NINEROUTER_API_KEY", env_keys.get("ROUTER9_API_KEY", env_keys.get("NINE_ROUTER_API_KEY", os.environ.get("NINEROUTER_API_KEY", os.environ.get("ROUTER9_API_KEY", os.environ.get("NINE_ROUTER_API_KEY", "")))))).strip()
                        elif target_prov_id == "atria":
                            existing_api_key = env_keys.get("ATRIA_API_KEY", os.environ.get("ATRIA_API_KEY", "")).strip()
                        elif target_prov_id == "nvidia":
                            existing_api_key = env_keys.get("NVIDIA_API_KEY", os.environ.get("NVIDIA_API_KEY", os.environ.get("NVAPI_KEY", ""))).strip()
                        elif target_prov_id == "openrouter":
                            existing_api_key = env_keys.get("OPENROUTER_API_KEY", os.environ.get("OPENROUTER_API_KEY", "")).strip()

                    # Jika 9router belum memiliki domain / base_url, minta user input
                    if target_prov_id == "9router" and not prov_entry.get("base_url"):
                        from rich.prompt import Prompt
                        console.print("\n[bold yellow]🌐 9Router membutuhkan Domain / Base URL.[/bold yellow]")
                        user_domain = Prompt.ask("[bold cyan]Masukkan Domain / Base URL 9Router (contoh: https://9router-production-3f3d.up.railway.app)[/bold cyan]").strip()
                        if user_domain:
                            if not user_domain.startswith("http://") and not user_domain.startswith("https://"):
                                user_domain = "https://" + user_domain
                            user_domain = user_domain.rstrip("/")
                            if not user_domain.endswith("/v1"):
                                user_domain = f"{user_domain}/v1"
                            prov_entry["base_url"] = user_domain
                            console.print(f"[bold green]✔ Base URL 9Router disimpan: {user_domain}[/bold green]")

                    # Jika API Key masih kosong, minta user input sekali saja
                    if not existing_api_key:
                        from rich.prompt import Prompt
                        console.print(f"\n[bold yellow]🔑 Provider '{prov_name}' belum memiliki API Key.[/bold yellow]")
                        user_api_key = Prompt.ask("[bold cyan]Masukkan API Key[/bold cyan]").strip()
                        if user_api_key:
                            prov_entry["api_key"] = user_api_key
                            existing_api_key = user_api_key
                            console.print("[bold green]✔ API Key tersimpan![/bold green]\n")

                    full_cfg["active_provider"] = target_prov_id
                    providers[target_prov_id]["model"] = target_model_id
                    if existing_api_key:
                        providers[target_prov_id]["api_key"] = existing_api_key
                    save_full_config(full_cfg)
                    
                    current_config["provider_id"] = target_prov_id
                    current_config["provider_name"] = prov_name
                    current_config["base_url"] = providers[target_prov_id].get("base_url", "")
                    current_config["api_key"] = existing_api_key
                    current_config["model"] = target_model_id
                else:
                    update_active_model(target_model_id)
                    current_config["model"] = target_model_id

                from config import is_thinking_supported
                if is_thinking_supported(target_model_id):
                    # Prompt thinking level for this reasoning model directly
                    current_config = select_thinking_interactive(
                        current_config,
                        model_name_display=chosen['name'],
                        provider_name_display=chosen['provider_name'],
                        is_inline=True
                    )
                else:
                    console.print(f"[bold green]✔ Model aktif:[/bold green] [bold yellow]{chosen['name']}[/bold yellow] ([dim]{chosen['provider_name']}[/dim])")
                return current_config

            elif k and isinstance(k, str) and not k.startswith(('UP', 'DOWN', 'LEFT', 'RIGHT', 'ESC', 'TAB', 'ENTER', 'BACKSPACE', 'CTRL_', 'SHIFT_', 'PAGE_')):
                query += k
                selected_idx = 0
                scroll_offset = 0

    finally:
        sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return current_config

def select_thinking_interactive(current_config=None, model_name_display=None, provider_name_display=None, is_inline=False):
    if not sys.stdin.isatty():
        from config import get_active_config
        return get_active_config()

    from config import get_thinking_mode, update_thinking_mode, get_active_config, is_thinking_supported
    from rich.prompt import Prompt

    if current_config is None:
        current_config = get_active_config()

    current_mode = str(get_thinking_mode()).lower()
    curr_model = current_config.get("model", "ag/gemini-3.7-flash-high")
    model_supports_thinking = is_thinking_supported(curr_model)

    if is_inline:
        menu_items = [
            {"id": "off", "name": "Off", "desc": "Tanpa thinking (Respons instan, hemat token)", "tag": "OFF", "color": "\033[90m"},
            {"id": "low", "name": "Low", "desc": "Thinking ringan (~2k token, penalaran cepat)", "tag": "LOW", "color": "\033[1;36m"},
            {"id": "medium", "name": "Medium", "desc": "Thinking seimbang (~8k token, logika analitis)", "tag": "MED", "color": "\033[1;34m"},
            {"id": "high", "name": "High", "desc": "Thinking mendalam (~16k token, arsitektur & coding)", "tag": "HIGH", "color": "\033[1;35m"},
            {"id": "max", "name": "Max", "desc": "Thinking maksimal (~32k token, deep reasoning)", "tag": "MAX", "color": "\033[1;31m"},
            {"id": "custom", "name": "Custom", "desc": "Tentukan budget token manual...", "tag": "EDIT", "color": "\033[1;33m"},
            {"id": "back", "name": "⏭️ Lewati / Gunakan High", "desc": "Gunakan level thinking bawaan (High)", "tag": "", "color": "\033[90m"}
        ]
    else:
        menu_items = [
            {"id": "off", "name": "Off", "desc": "Tanpa thinking (Respons instan, hemat token)", "tag": "OFF", "color": "\033[90m"},
            {"id": "low", "name": "Low", "desc": "Thinking ringan (~2k token, penalaran cepat)", "tag": "LOW", "color": "\033[1;36m"},
            {"id": "medium", "name": "Medium", "desc": "Thinking seimbang (~8k token, logika analitis)", "tag": "MED", "color": "\033[1;34m"},
            {"id": "high", "name": "High", "desc": "Thinking mendalam (~16k token, arsitektur & coding)", "tag": "HIGH", "color": "\033[1;35m"},
            {"id": "max", "name": "Max", "desc": "Thinking maksimal (~32k token, deep reasoning)", "tag": "MAX", "color": "\033[1;31m"},
            {"id": "custom", "name": "Custom", "desc": "Tentukan budget token manual...", "tag": "EDIT", "color": "\033[1;33m"},
            {"id": "back", "name": "⬅️ Batal / Kembali", "desc": "Kembali ke menu", "tag": "", "color": "\033[90m"}
        ]

    selected_idx = 3  # default high
    for idx, it in enumerate(menu_items):
        if it["id"] == current_mode:
            selected_idx = idx
            break
        elif it["id"] == "custom" and current_mode not in ["off", "low", "medium", "high", "max"] and current_mode:
            selected_idx = idx

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    sys.stdout.write("\033[?1049h\033[?25l\033[H\033[2J")
    sys.stdout.flush()

    chosen = None
    try:
        tty.setraw(fd)
        sys.stdout.write("\033[?7l")
        sys.stdout.flush()

        while True:
            try:
                term_cols = os.get_terminal_size().columns
            except Exception:
                term_cols = 50
            width = max(38, min(term_cols - 2, 64))

            lines = []
            if model_name_display:
                title_tag = f"🧠  Pilih Thinking: {model_name_display}"
            else:
                title_tag = "🧠  Mode Thinking / Reasoning (OpenCode)"
            
            if len(title_tag) > width - 8:
                title_tag = title_tag[:width - 11] + ".."
            gap_t = max(1, width - len(title_tag) - 7)
            lines.append(f"\033[1;36m{title_tag}\033[0m{' ' * gap_t}\033[90m[Esc]\033[0m")
            
            # Show model compatibility status in subheader
            short_m = (model_name_display or curr_model).split('/')[-1]
            if len(short_m) > width - 24:
                short_m = short_m[:width - 27] + ".."
            if model_supports_thinking:
                status_sub = f"\033[90mModel: \033[1;37m{short_m}\033[0m \033[1;32m[✔ Reasoning Supported]\033[0m"
            else:
                status_sub = f"\033[90mModel: \033[1;37m{short_m}\033[0m \033[90m[○ Non-Reasoning]\033[0m"
            
            lines.append(status_sub)
            lines.append(f"\033[90m{'─' * width}\033[0m")
            lines.append("")

            for idx, item in enumerate(menu_items):
                is_sel = (idx == selected_idx)
                i_id = item["id"]
                is_active = (current_mode == i_id) or (i_id == "custom" and current_mode not in ["off", "low", "medium", "high", "max"] and current_mode)

                radio = "●" if is_active else "○"
                pfx = "▸ " if is_sel else "  "
                
                tag_badge = f"{item['color']}[{item['tag']}]\033[0m " if item["tag"] else ""
                act_tag = " \033[1;32m(Aktif)\033[0m" if is_active else ""
                
                avail_w = width - 4
                if item["id"] == "back":
                    row_txt = f"{pfx}{item['name']}"
                elif item["id"] == "custom" and current_mode not in ["off", "low", "medium", "high", "max"] and current_mode:
                    row_txt = f"{pfx}{radio} {tag_badge}\033[1mCustom ({current_mode} tok)\033[0m{act_tag}"
                else:
                    row_txt = f"{pfx}{radio} {tag_badge}\033[1m{item['name']}\033[0m{act_tag}"

                desc_line = f"     \033[90m{item['desc']}\033[0m"

                if is_sel:
                    lines.append(f"\033[7m\033[1m {row_txt:<{avail_w}} \033[0m")
                    if item["id"] != "back":
                        lines.append(f"\033[7m {desc_line:<{avail_w}} \033[0m")
                else:
                    lines.append(f" {row_txt}")
                    if item["id"] != "back":
                        lines.append(f" {desc_line}")
                lines.append("")

            lines.append(f"\033[90m{'─' * width}\033[0m")
            hint_esc = "Esc Lewati" if is_inline else "Esc Batal"
            lines.append(f" \033[1;33m↑↓/Tab\033[0m \033[90mPilih\033[0m  \033[1;32mEnter\033[0m \033[90mPilih\033[0m  \033[90m{hint_esc}\033[0m")

            out_buf = ["\033[H"]
            for l in lines:
                out_buf.append(f"\r\033[2K{l}\r\n")
            out_buf.append("\r\033[J")
            sys.stdout.write("".join(out_buf))
            sys.stdout.flush()

            k = read_key_raw_fd(fd)
            if k in ('ESC', 'CTRL_C'):
                chosen = "back"
                break
            elif k in ('UP', 'SHIFT_TAB'):
                selected_idx = (selected_idx - 1) % len(menu_items)
            elif k in ('DOWN', 'TAB'):
                selected_idx = (selected_idx + 1) % len(menu_items)
            elif k == 'ENTER':
                chosen = menu_items[selected_idx]["id"]
                break
    finally:
        sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    disp_m_name = model_name_display or curr_model
    disp_p_name = provider_name_display or current_config.get("provider_name", "")

    if chosen == "back" or not chosen:
        if is_inline:
            # User skipped thinking selector, keep current/default thinking mode
            th = current_mode.upper() if current_mode else "HIGH"
            console.print(f"[bold green]✔ Model aktif:[/bold green] [bold yellow]{disp_m_name}[/bold yellow] [dim]({disp_p_name})[/dim] • [bold magenta]Thinking: {th}[/bold magenta]\n")
        return current_config
    elif chosen == "custom":
        custom_val = Prompt.ask("\n[bold cyan]Masukkan budget token thinking (contoh: 4096, 8192, 32768)[/bold cyan]").strip()
        if custom_val.isdigit() and int(custom_val) > 0:
            update_thinking_mode(custom_val)
            current_config["thinking_mode"] = custom_val
            console.print(f"[bold green]✔ Model aktif:[/bold green] [bold yellow]{disp_m_name}[/bold yellow] [dim]({disp_p_name})[/dim] • [bold magenta]Thinking: {custom_val} tokens[/bold magenta]\n")
        else:
            console.print(f"[bold green]✔ Model aktif:[/bold green] [bold yellow]{disp_m_name}[/bold yellow] [dim]({disp_p_name})[/dim]\n")
        return current_config
    else:
        update_thinking_mode(chosen)
        current_config["thinking_mode"] = chosen
        console.print(f"[bold green]✔ Model aktif:[/bold green] [bold yellow]{disp_m_name}[/bold yellow] [dim]({disp_p_name})[/dim] • [bold magenta]Thinking: {chosen.upper()}[/bold magenta]\n")
        return current_config

