import os
import sys
import json
import select
import tty
import termios
from ui import console
from config import load_full_config, save_full_config

# Color themes with ANSI escape codes
THEMES = {
    "tokyonight": {
        "name": "Tokyo Night",
        "primary": "\033[1;36m",      # Cyan
        "secondary": "\033[1;35m",    # Magenta / Violet
        "accent": "\033[1;34m",       # Deep Blue
        "dim": "\033[90m",            # Gray
        "success": "\033[1;32m",      # Green
        "warn": "\033[1;33m",         # Yellow
        "bracket": "\033[1;36m",      # Cyan
        "arrow": "\033[1;35m",        # Magenta
        "reset": "\033[0m"
    },
    "cyberpunk": {
        "name": "Cyberpunk Neon",
        "primary": "\033[1;35m",      # Neon Pink / Magenta
        "secondary": "\033[1;33m",    # Neon Yellow
        "accent": "\033[1;36m",       # Neon Cyan
        "dim": "\033[90m",
        "success": "\033[1;32m",
        "warn": "\033[1;33m",
        "bracket": "\033[1;35m",
        "arrow": "\033[1;33m",
        "reset": "\033[0m"
    },
    "matrix": {
        "name": "Matrix Green",
        "primary": "\033[1;32m",      # Bright Green
        "secondary": "\033[0;32m",    # Darker Green
        "accent": "\033[1;92m",       # Mint
        "dim": "\033[90m",
        "success": "\033[1;32m",
        "warn": "\033[1;33m",
        "bracket": "\033[1;32m",
        "arrow": "\033[1;92m",
        "reset": "\033[0m"
    },
    "dracula": {
        "name": "Dracula Purple",
        "primary": "\033[1;35m",      # Purple
        "secondary": "\033[1;36m",    # Cyan
        "accent": "\033[1;31m",       # Coral Red
        "dim": "\033[90m",
        "success": "\033[1;32m",
        "warn": "\033[1;33m",
        "bracket": "\033[1;35m",
        "arrow": "\033[1;36m",
        "reset": "\033[0m"
    },
    "monokai": {
        "name": "Monokai Pro",
        "primary": "\033[1;33m",      # Yellow
        "secondary": "\033[1;32m",    # Green
        "accent": "\033[1;35m",       # Magenta
        "dim": "\033[90m",
        "success": "\033[1;32m",
        "warn": "\033[1;33m",
        "bracket": "\033[1;33m",
        "arrow": "\033[1;32m",
        "reset": "\033[0m"
    },
    "nord": {
        "name": "Nord Arctic",
        "primary": "\033[1;34m",      # Frost Blue
        "secondary": "\033[1;36m",    # Ice Cyan
        "accent": "\033[1;37m",       # Snow White
        "dim": "\033[90m",
        "success": "\033[1;32m",
        "warn": "\033[1;33m",
        "bracket": "\033[1;34m",
        "arrow": "\033[1;36m",
        "reset": "\033[0m"
    },
    "minimal": {
        "name": "Minimal Zinc",
        "primary": "\033[1;37m",      # Pure White
        "secondary": "\033[0;37m",    # Slate
        "accent": "\033[1;37m",
        "dim": "\033[90m",
        "success": "\033[1;32m",
        "warn": "\033[1;33m",
        "bracket": "\033[90m",
        "arrow": "\033[1;37m",
        "reset": "\033[0m"
    }
}

PROMPT_STYLES = {
    "agy": {
        "id": "agy",
        "name": "Agy Double-Line (Antigravity Futuristic)",
        "desc": "╭─ ⚡ [rts:nemotron] · Termux · Auto\n╰─❯ [prompt]"
    },
    "cyber": {
        "id": "cyber",
        "name": "Cyber Box (Neon Terminal)",
        "desc": "┌── 🚀 [rts // nemotron] ── [Ready]\n└── ❯ [prompt]"
    },
    "powerline": {
        "id": "powerline",
        "name": "Powerline Segments",
        "desc": "▰▰ rts ▰ nemotron ▰ Auto ▰\n❯ [prompt]"
    },
    "minimal": {
        "id": "minimal",
        "name": "Minimal Compact",
        "desc": "rts (nemotron) ❯ [prompt]"
    },
    "classic": {
        "id": "classic",
        "name": "Classic r.outers",
        "desc": "r.outers > [prompt]\n⚡ Nemotron · Auto · Ready"
    }
}

def get_current_style_settings():
    full_cfg = load_full_config()
    settings = full_cfg.get("settings", {})
    style_id = settings.get("prompt_style", "agy")
    theme_id = settings.get("theme", "tokyonight")
    
    if style_id not in PROMPT_STYLES:
        style_id = "agy"
    if theme_id not in THEMES:
        theme_id = "tokyonight"
        
    return style_id, theme_id

def set_style_settings(style_id=None, theme_id=None):
    full_cfg = load_full_config()
    if "settings" not in full_cfg or not isinstance(full_cfg["settings"], dict):
        full_cfg["settings"] = {}
    
    if style_id and style_id in PROMPT_STYLES:
        full_cfg["settings"]["prompt_style"] = style_id
    if theme_id and theme_id in THEMES:
        full_cfg["settings"]["theme"] = theme_id
        
    save_full_config(full_cfg)

def render_prompt_layout(style_id, theme_id, model_name="nemotron", auto_approve=True, current_input="", cursor_col=0):
    t = THEMES.get(theme_id, THEMES["tokyonight"])
    perm_str = "Auto" if auto_approve else "Ask"
    perm_icon = "⚡" if auto_approve else "🛡️"
    
    # Format model name short
    short_model = model_name.split("/")[-1].split(":")[0]
    if len(short_model) > 18:
        short_model = short_model[:16] + ".."

    cursor_block = "\033[42m \033[0m"
    before = current_input[:cursor_col]
    after = current_input[cursor_col:]
    input_rendered = f"{before}{cursor_block}{after}"

    if style_id == "agy":
        top_line = f"{t['bracket']}╭─{t['reset']} {t['warn']}{perm_icon}{t['reset']} {t['bracket']}[{t['primary']}rts{t['bracket']}:{t['secondary']}{short_model}{t['bracket']}]{t['reset']} {t['dim']}·{t['reset']} {t['accent']}Termux{t['reset']} {t['dim']}·{t['reset']} {t['success']}{perm_str}{t['reset']}"
        bottom_prefix = f"{t['bracket']}╰─{t['arrow']}❯{t['reset']} "
        return {
            "type": "double_top",
            "top_line": top_line,
            "bottom_prefix": bottom_prefix,
            "prefix_visible_len": 4,
            "input_rendered": input_rendered
        }

    elif style_id == "cyber":
        top_line = f"{t['primary']}┌──{t['reset']} 🚀 {t['bracket']}[{t['secondary']}rts{t['dim']} // {t['primary']}{short_model}{t['bracket']}]{t['reset']} {t['primary']}──{t['reset']} {t['bracket']}[{t['success']}{perm_str}{t['bracket']}]{t['reset']}"
        bottom_prefix = f"{t['primary']}└──{t['reset']} {t['arrow']}❯{t['reset']} "
        return {
            "type": "double_top",
            "top_line": top_line,
            "bottom_prefix": bottom_prefix,
            "prefix_visible_len": 6,
            "input_rendered": input_rendered
        }

    elif style_id == "powerline":
        top_line = f"{t['secondary']}▰▰{t['reset']} {t['primary']}rts{t['reset']} {t['dim']}▰{t['reset']} {t['secondary']}{short_model}{t['reset']} {t['dim']}▰{t['reset']} {t['success']}{perm_str}{t['reset']} {t['dim']}▰{t['reset']}"
        bottom_prefix = f"{t['arrow']}❯{t['reset']} "
        return {
            "type": "double_top",
            "top_line": top_line,
            "bottom_prefix": bottom_prefix,
            "prefix_visible_len": 2,
            "input_rendered": input_rendered
        }

    elif style_id == "minimal":
        prefix = f"{t['primary']}rts{t['dim']}({t['secondary']}{short_model}{t['dim']}){t['reset']} {t['arrow']}❯{t['reset']} "
        vlen = len(f"rts({short_model}) ❯ ")
        return {
            "type": "single",
            "bottom_prefix": prefix,
            "prefix_visible_len": vlen,
            "input_rendered": input_rendered
        }

    else: # classic
        bottom_prefix = f"{t['primary']}r.outers >{t['reset']} "
        sub_info = f"{t['warn']}{perm_icon}{t['reset']} {short_model}  {t['dim']}·{t['reset']}  {perm_str}  {t['dim']}·{t['reset']}  Ready"
        return {
            "type": "double_bottom",
            "bottom_prefix": bottom_prefix,
            "sub_info": sub_info,
            "prefix_visible_len": 11,
            "input_rendered": input_rendered
        }

def select_style_and_theme_interactive():
    if not sys.stdin.isatty():
        return
        
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    current_style, current_theme = get_current_style_settings()
    
    styles_list = list(PROMPT_STYLES.values())
    themes_list = list(THEMES.items())
    
    # State: tab 0 = style, tab 1 = theme
    active_tab = 0
    sel_style_idx = next((i for i, s in enumerate(styles_list) if s["id"] == current_style), 0)
    sel_theme_idx = next((i for i, (k, _) in enumerate(themes_list) if k == current_theme), 0)
    
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
                
            modal_width = max(36, min(term_cols - 2, 60))
            
            cur_st = styles_list[sel_style_idx]["id"]
            cur_th = themes_list[sel_theme_idx][0]
            
            lines = []
            title = "🎨 Terminal Style & Theme Customizer"
            esc_lbl = "[Esc: Simpan & Tutup]"
            gap = modal_width - len(title) - len(esc_lbl) - 2
            if gap < 1: gap = 1
            lines.append(f"\033[1;36m{title}\033[0m{' ' * gap}\033[90m{esc_lbl}\033[0m")
            lines.append(f"\033[90m{'─' * modal_width}\033[0m")
            
            # Tab Selector Header
            tab0_str = f" 1. Prompt Style ({styles_list[sel_style_idx]['name'].split()[0]}) "
            tab1_str = f" 2. Color Theme ({themes_list[sel_theme_idx][1]['name']}) "
            
            if active_tab == 0:
                header_tabs = f"\033[1;32m\033[7m{tab0_str}\033[0m  \033[90m{tab1_str}\033[0m"
            else:
                header_tabs = f"\033[90m{tab0_str}\033[0m  \033[1;35m\033[7m{tab1_str}\033[0m"
            lines.append(header_tabs)
            lines.append(f"\033[90m{'─' * modal_width}\033[0m")
            lines.append("")
            
            if active_tab == 0:
                lines.append("\033[1;33mPilih Model Tampilan Prompt:\033[0m")
                for idx, st in enumerate(styles_list):
                    is_sel = (idx == sel_style_idx)
                    prefix = "▸ " if is_sel else "  "
                    badge = "[Aktif]" if st["id"] == current_style else ""
                    row_text = f"{prefix}{st['name']}"
                    
                    avail_w = modal_width - 4
                    gap_r = avail_w - len(row_text) - len(badge)
                    if gap_r < 1: gap_r = 1
                    
                    if is_sel:
                        lines.append(f"\033[7m\033[1m {row_text}{' ' * gap_r}{badge} \033[0m")
                    else:
                        lines.append(f"{prefix}\033[1;37m{st['name']}\033[0m{' ' * gap_r}\033[90m{badge}\033[0m")
            else:
                lines.append("\033[1;35mPilih Tema Warna (Palette):\033[0m")
                for idx, (t_id, t_info) in enumerate(themes_list):
                    is_sel = (idx == sel_theme_idx)
                    prefix = "▸ " if is_sel else "  "
                    badge = "[Aktif]" if t_id == current_theme else ""
                    row_text = f"{prefix}{t_info['name']}"
                    
                    avail_w = modal_width - 4
                    gap_r = avail_w - len(row_text) - len(badge)
                    if gap_r < 1: gap_r = 1
                    
                    if is_sel:
                        lines.append(f"\033[7m\033[1m {row_text}{' ' * gap_r}{badge} \033[0m")
                    else:
                        lines.append(f"{prefix}\033[1;37m{t_info['name']}\033[0m{' ' * gap_r}\033[90m{badge}\033[0m")
                        
            # Live Preview Section
            lines.append("")
            lines.append(f"\033[90m{'─' * modal_width}\033[0m")
            lines.append(" \033[1;36mLIVE PREVIEW TAMPILAN:\033[0m")
            
            preview = render_prompt_layout(cur_st, cur_th, model_name="nemotron-3-super-120b", auto_approve=True, current_input="buatkan script bot vibe coding", cursor_col=29)
            if preview["type"] == "double_top":
                lines.append(f" {preview['top_line']}")
                lines.append(f" {preview['bottom_prefix']}{preview['input_rendered']}")
            elif preview["type"] == "double_bottom":
                lines.append(f" {preview['bottom_prefix']}{preview['input_rendered']}")
                lines.append(f" {preview['sub_info']}")
            else:
                lines.append(f" {preview['bottom_prefix']}{preview['input_rendered']}")
                
            lines.append(f"\033[90m{'─' * modal_width}\033[0m")
            lines.append(" \033[1;33m↑↓\033[0m \033[90mPilih\033[0m  \033[1;36m←→ / Tab\033[0m \033[90mGanti Tab\033[0m  \033[1;32mEnter\033[0m \033[90mSimpan\033[0m  \033[90mEsc Batal\033[0m")
            
            output_buf = ["\033[H"]
            for l in lines:
                output_buf.append(f"\r\033[2K{l}\r\n")
            output_buf.append("\r\033[J")
            sys.stdout.write("".join(output_buf))
            sys.stdout.flush()
            
            # Read input
            from slash_prompt import read_key_raw
            k = read_key_raw(fd)
            
            if k in ('ESC', 'CTRL_C'):
                break
            elif k in ('LEFT', 'RIGHT', 'TAB'):
                active_tab = 1 if active_tab == 0 else 0
            elif k in ('UP', 'SHIFT_TAB'):
                if active_tab == 0:
                    sel_style_idx = (sel_style_idx - 1) % len(styles_list)
                else:
                    sel_theme_idx = (sel_theme_idx - 1) % len(themes_list)
            elif k == 'DOWN':
                if active_tab == 0:
                    sel_style_idx = (sel_style_idx + 1) % len(styles_list)
                else:
                    sel_theme_idx = (sel_theme_idx + 1) % len(themes_list)
            elif k == 'ENTER':
                chosen_style = styles_list[sel_style_idx]["id"]
                chosen_theme = themes_list[sel_theme_idx][0]
                set_style_settings(chosen_style, chosen_theme)
                break
                
    finally:
        sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
    chosen_style, chosen_theme = get_current_style_settings()
    console.print(f"[bold green]✔ Style terminal berhasil diubah:[/bold green] [bold cyan]{PROMPT_STYLES[chosen_style]['name']}[/bold cyan] · Tema: [bold magenta]{THEMES[chosen_theme]['name']}[/bold magenta]\n")
