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

                full_cfg = load_full_config()
                providers = full_cfg.get("providers", {})
                
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
                        if target_prov_id == "atria":
                            existing_api_key = env_keys.get("ATRIA_API_KEY", os.environ.get("ATRIA_API_KEY", "")).strip()
                        elif target_prov_id == "clouvia":
                            existing_api_key = env_keys.get("CLOUVIA_API_KEY", os.environ.get("CLOUVIA_API_KEY", "")).strip()
                        elif target_prov_id == "nvidia":
                            existing_api_key = env_keys.get("NVIDIA_API_KEY", os.environ.get("NVIDIA_API_KEY", os.environ.get("NVAPI_KEY", ""))).strip()

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
