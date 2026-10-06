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
    if not val:
        return False
    val_clean = str(val).strip().lower()
    return val_clean in ("e", "esc", "q", "exit", "batal", "back", "\x1b") or val_clean.startswith("\x1b")

def setup_9router_interactive(current_config=None):
    from rich.prompt import Prompt
    from config import get_active_config
    console.print("\n[bold cyan]⚡ Setup & Hubungkan 9Router[/bold cyan] [dim](Ketik 'esc' / 'e' kapan saja untuk batal)[/dim]")
    console.print("[dim]Masukkan URL domain 9Router Anda (misal Railway/VPS), API Key, dan pilih Model AI.[/dim]\n")

    full_cfg = load_full_config()
    providers = full_cfg.get("providers", {})
    existing_9r = providers.get("9router", {})

    try:
        # 1. Masukkan Domain / Base URL
        def_url = existing_9r.get("base_url", "")
        raw_url = Prompt.ask(
            "[bold cyan]1. Masukkan Domain / Base URL 9Router[/bold cyan] [dim](contoh: https://your-9router.up.railway.app - Esc/e: batal)[/dim]",
            default=def_url if def_url else ""
        ).strip()
        
        if is_cancel_input(raw_url):
            console.print("[yellow]Batal setup 9Router.[/yellow]\n")
            return current_config or get_active_config()

        if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
            raw_url = "https://" + raw_url
        raw_url = raw_url.rstrip("/")
        if not raw_url.endswith("/v1"):
            raw_url = f"{raw_url}/v1"
        base_url = raw_url

        # 2. Masukkan API Key
        def_key = existing_9r.get("api_key", "")
        api_key = Prompt.ask(
            "[bold cyan]2. Masukkan / Paste API Key 9Router[/bold cyan] [dim](Esc/e: batal)[/dim]",
            default=def_key if def_key else ""
        ).strip()

        if not api_key or is_cancel_input(api_key):
            console.print("[yellow]Batal setup 9Router (API Key kosong atau dibatalkan).[/yellow]\n")
            return current_config or get_active_config()

        # 3. Auto-fetch live models and prompt model
        console.print("\n[dim]⏳ Mengambil daftar model aktif dari 9Router...[/dim]")
        from model_fetcher import fetch_provider_models
        live_models = fetch_provider_models("9router", base_url=base_url, api_key=api_key, force_refresh=True)

        suggested_model = "ag/gemini-3.7-flash-high"
        if live_models:
            model_ids = [m["id"] for m in live_models]
            if existing_9r.get("model") in model_ids:
                suggested_model = existing_9r.get("model")
            elif any("gemini-3.7-flash" in m["id"] for m in live_models):
                suggested_model = next(m["id"] for m in live_models if "gemini-3.7-flash" in m["id"])
            else:
                suggested_model = model_ids[0]

            console.print(f"[bold green]✔ Berhasil terhubung! Terdeteksi {len(live_models)} model aktif.[/bold green]")
            console.print("[dim]Contoh model tersedia: " + ", ".join(model_ids[:5]) + "[/dim]\n")
        else:
            console.print("[yellow]⚠ Catatan: Tidak dapat mengambil katalog live secara otomatis, masukkan nama model secara manual.[/yellow]\n")

        model = Prompt.ask(
            "[bold cyan]3. Masukkan Model AI yang Ingin Digunakan[/bold cyan] [dim](Esc/e: batal)[/dim]",
            default=suggested_model
        ).strip()

        if is_cancel_input(model):
            console.print("[yellow]Batal setup 9Router.[/yellow]\n")
            return current_config or get_active_config()

        if not model:
            model = suggested_model

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
                    "provider_id": current_config.get("provider_id", "clouvia"),
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
                        elif target_prov_id == "clouvia":
                            existing_api_key = env_keys.get("CLOUVIA_API_KEY", os.environ.get("CLOUVIA_API_KEY", "")).strip()
                        elif target_prov_id == "nvidia":
                            existing_api_key = env_keys.get("NVIDIA_API_KEY", os.environ.get("NVIDIA_API_KEY", os.environ.get("NVAPI_KEY", ""))).strip()
                        elif target_prov_id == "openrouter":
                            existing_api_key = env_keys.get("OPENROUTER_API_KEY", os.environ.get("OPENROUTER_API_KEY", "")).strip()

                    # Jika 9router belum memiliki domain / base_url, minta user input
                    if target_prov_id == "9router" and not prov_entry.get("base_url"):
                        from rich.prompt import Prompt
                        console.print("\n[bold yellow]🌐 9Router membutuhkan Domain / Base URL.[/bold yellow]")
                        user_domain = Prompt.ask("[bold cyan]Masukkan Domain / Base URL 9Router (contoh: https://9router-production-b35d.up.railway.app)[/bold cyan]").strip()
                        if user_domain:
                            if not user_domain.startswith("http://") and not user_domain.startswith("https://"):
                                user_domain = "https://" + user_domain
                            user_domain = user_domain.rstrip("/")
                            if not user_domain.endswith("/v1"):
                                user_domain = f"{user_domain}/v1"
                            prov_entry["base_url"] = user_domain
                            console.print(f"[bold green]✔ Base URL 9Router disimpan: {user_domain}[/bold green]")

                    # Jika API Key masih kosong dan bukan clouvia bawaan gratis, minta user input sekali saja
                    if not existing_api_key and target_prov_id != "clouvia":
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
    curr_model = current_config.get("model", "free-model")
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

