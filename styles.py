import os
import sys
import json
import select
import tty
import termios
from ui import console
from config import load_full_config, save_full_config

# Precise Color Schemes aligned with standard agent / Claude / AGY palettes
COLOR_SCHEMES = [
    {
        "id": "terminal",
        "name": "terminal",
        "desc": "Default Terminal Colors",
        "palette": {
            "prompt_user": "\033[1;36m",      # Cyan
            "prompt_arrow": "\033[1;32m",     # Green
            "text": "\033[0m",
            "dim": "\033[90m",
            "keyword": "\033[1;35m",          # Magenta
            "string": "\033[32m",             # Green
            "diff_del": "\033[31m",           # Red
            "diff_add": "\033[32m",           # Green
            "diff_del_bg": "\033[31m",
            "diff_add_bg": "\033[32m",
            "lineno": "\033[90m",
            "bracket": "\033[1;36m",
            "accent": "\033[1;34m"
        }
    },
    {
        "id": "light",
        "name": "light",
        "desc": "Clean Light Mode",
        "palette": {
            "prompt_user": "\033[1;34m",      # Blue
            "prompt_arrow": "\033[1;36m",
            "text": "\033[37m",
            "dim": "\033[90m",
            "keyword": "\033[1;35m",
            "string": "\033[32m",
            "diff_del": "\033[1;31m",
            "diff_add": "\033[1;32m",
            "diff_del_bg": "\033[31m",
            "diff_add_bg": "\033[32m",
            "lineno": "\033[90m",
            "bracket": "\033[34m",
            "accent": "\033[36m"
        }
    },
    {
        "id": "solarized_light",
        "name": "solarized light",
        "desc": "Solarized Warm Light",
        "palette": {
            "prompt_user": "\033[1;33m",      # Yellow
            "prompt_arrow": "\033[1;36m",     # Cyan
            "text": "\033[37m",
            "dim": "\033[90m",
            "keyword": "\033[1;32m",          # Green
            "string": "\033[36m",             # Cyan
            "diff_del": "\033[1;31m",         # Red
            "diff_add": "\033[1;32m",         # Green
            "diff_del_bg": "\033[31m",
            "diff_add_bg": "\033[32m",
            "lineno": "\033[90m",
            "bracket": "\033[33m",
            "accent": "\033[36m"
        }
    },
    {
        "id": "colorblind_light",
        "name": "colorblind-friendly light",
        "desc": "High Contrast Accessible Light",
        "palette": {
            "prompt_user": "\033[1;34m",      # Deep Blue
            "prompt_arrow": "\033[1;33m",     # Amber
            "text": "\033[37m",
            "dim": "\033[90m",
            "keyword": "\033[1;34m",
            "string": "\033[33m",
            "diff_del": "\033[1;33m",         # Vermillion / Amber
            "diff_add": "\033[1;34m",         # High-contrast Blue
            "diff_del_bg": "\033[33m",
            "diff_add_bg": "\033[34m",
            "lineno": "\033[90m",
            "bracket": "\033[34m",
            "accent": "\033[33m"
        }
    },
    {
        "id": "dark",
        "name": "dark",
        "desc": "High Contrast Dark",
        "palette": {
            "prompt_user": "\033[1;37m",      # Bright White
            "prompt_arrow": "\033[1;32m",
            "text": "\033[37m",
            "dim": "\033[90m",
            "keyword": "\033[1;36m",          # Cyan
            "string": "\033[1;32m",           # Green
            "diff_del": "\033[1;31m",         # Red
            "diff_add": "\033[1;32m",         # Green
            "diff_del_bg": "\033[31m",
            "diff_add_bg": "\033[32m",
            "lineno": "\033[90m",
            "bracket": "\033[90m",
            "accent": "\033[1;37m"
        }
    },
    {
        "id": "solarized_dark",
        "name": "solarized dark",
        "desc": "Solarized Deep Dark",
        "palette": {
            "prompt_user": "\033[1;36m",      # Cyan
            "prompt_arrow": "\033[1;33m",     # Yellow
            "text": "\033[37m",
            "dim": "\033[90m",
            "keyword": "\033[1;32m",          # Green
            "string": "\033[1;36m",           # Cyan
            "diff_del": "\033[1;35m",         # Magenta
            "diff_add": "\033[1;32m",         # Green
            "diff_del_bg": "\033[35m",
            "diff_add_bg": "\033[32m",
            "lineno": "\033[90m",
            "bracket": "\033[36m",
            "accent": "\033[33m"
        }
    },
    {
        "id": "colorblind_dark",
        "name": "colorblind-friendly dark",
        "desc": "High Contrast Accessible Dark",
        "palette": {
            "prompt_user": "\033[1;36m",      # Sky Blue
            "prompt_arrow": "\033[1;33m",     # Amber
            "text": "\033[37m",
            "dim": "\033[90m",
            "keyword": "\033[1;36m",
            "string": "\033[1;33m",
            "diff_del": "\033[1;33m",         # Amber
            "diff_add": "\033[1;36m",         # Cyan / Sky Blue
            "diff_del_bg": "\033[33m",
            "diff_add_bg": "\033[36m",
            "lineno": "\033[90m",
            "bracket": "\033[36m",
            "accent": "\033[33m"
        }
    },
    {
        "id": "tokyonight",
        "name": "tokyo night",
        "desc": "Tokyo Night Futuristic",
        "palette": {
            "prompt_user": "\033[1;36m",      # Cyan
            "prompt_arrow": "\033[1;35m",     # Magenta
            "text": "\033[37m",
            "dim": "\033[90m",
            "keyword": "\033[1;35m",          # Purple
            "string": "\033[1;32m",           # Emerald
            "diff_del": "\033[1;31m",         # Red / Coral
            "diff_add": "\033[1;32m",         # Bright Green
            "diff_del_bg": "\033[31m",
            "diff_add_bg": "\033[32m",
            "lineno": "\033[90m",
            "bracket": "\033[1;36m",
            "accent": "\033[1;34m"
        }
    },
    {
        "id": "cyberpunk",
        "name": "cyberpunk",
        "desc": "Cyberpunk Neon",
        "palette": {
            "prompt_user": "\033[1;35m",      # Neon Pink
            "prompt_arrow": "\033[1;33m",     # Neon Yellow
            "text": "\033[37m",
            "dim": "\033[90m",
            "keyword": "\033[1;36m",          # Neon Cyan
            "string": "\033[1;33m",           # Yellow
            "diff_del": "\033[1;35m",         # Neon Pink
            "diff_add": "\033[1;36m",         # Neon Cyan
            "diff_del_bg": "\033[35m",
            "diff_add_bg": "\033[36m",
            "lineno": "\033[90m",
            "bracket": "\033[1;35m",
            "accent": "\033[1;33m"
        }
    },
    {
        "id": "matrix",
        "name": "matrix",
        "desc": "Matrix Phosphor Green",
        "palette": {
            "prompt_user": "\033[1;32m",      # Bright Green
            "prompt_arrow": "\033[1;92m",     # Mint
            "text": "\033[32m",
            "dim": "\033[90m",
            "keyword": "\033[1;92m",
            "string": "\033[0;32m",
            "diff_del": "\033[1;31m",
            "diff_add": "\033[1;92m",
            "diff_del_bg": "\033[31m",
            "diff_add_bg": "\033[92m",
            "lineno": "\033[90m",
            "bracket": "\033[1;32m",
            "accent": "\033[1;92m"
        }
    }
]

THEMES_MAP = {s["id"]: s for s in COLOR_SCHEMES}

PROMPT_STYLES = {
    "agy": {
        "id": "agy",
        "name": "Agy Double-Line (Antigravity)",
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
    if theme_id not in THEMES_MAP:
        theme_id = "tokyonight"
        
    return style_id, theme_id

def set_style_settings(style_id=None, theme_id=None):
    full_cfg = load_full_config()
    if "settings" not in full_cfg or not isinstance(full_cfg["settings"], dict):
        full_cfg["settings"] = {}
    
    if style_id and style_id in PROMPT_STYLES:
        full_cfg["settings"]["prompt_style"] = style_id
    if theme_id and theme_id in THEMES_MAP:
        full_cfg["settings"]["theme"] = theme_id
        
    save_full_config(full_cfg)

def render_prompt_layout(style_id, theme_id, model_name="nemotron", auto_approve=True, current_input="", cursor_col=0):
    scheme = THEMES_MAP.get(theme_id, THEMES_MAP["tokyonight"])
    p = scheme["palette"]
    perm_str = "Auto" if auto_approve else "Ask"
    perm_icon = "⚡" if auto_approve else "🛡️"
    
    short_model = model_name.split("/")[-1].split(":")[0]
    if len(short_model) > 18:
        short_model = short_model[:16] + ".."

    cursor_block = "\033[42m \033[0m"
    before = current_input[:cursor_col]
    after = current_input[cursor_col:]
    input_rendered = f"{before}{cursor_block}{after}"

    if style_id == "agy":
        top_line = f"{p['bracket']}╭─\033[0m \033[1;33m{perm_icon}\033[0m {p['bracket']}[{p['prompt_user']}rts{p['bracket']}:{p['prompt_arrow']}{short_model}{p['bracket']}]\033[0m {p['dim']}·\033[0m {p['accent']}Termux\033[0m {p['dim']}·\033[0m {p['diff_add']}{perm_str}\033[0m"
        bottom_prefix = f"{p['bracket']}╰─{p['prompt_arrow']}❯\033[0m "
        return {
            "type": "double_top",
            "top_line": top_line,
            "bottom_prefix": bottom_prefix,
            "prefix_visible_len": 4,
            "input_rendered": input_rendered
        }

    elif style_id == "cyber":
        top_line = f"{p['prompt_user']}┌──\033[0m 🚀 {p['bracket']}[{p['prompt_arrow']}rts{p['dim']} // {p['prompt_user']}{short_model}{p['bracket']}]\033[0m {p['prompt_user']}──\033[0m {p['bracket']}[{p['diff_add']}{perm_str}{p['bracket']}]\033[0m"
        bottom_prefix = f"{p['prompt_user']}└──\033[0m {p['prompt_arrow']}❯\033[0m "
        return {
            "type": "double_top",
            "top_line": top_line,
            "bottom_prefix": bottom_prefix,
            "prefix_visible_len": 6,
            "input_rendered": input_rendered
        }

    elif style_id == "powerline":
        top_line = f"{p['prompt_arrow']}▰▰\033[0m {p['prompt_user']}rts\033[0m {p['dim']}▰\033[0m {p['prompt_arrow']}{short_model}\033[0m {p['dim']}▰\033[0m {p['diff_add']}{perm_str}\033[0m {p['dim']}▰\033[0m"
        bottom_prefix = f"{p['prompt_arrow']}❯\033[0m "
        return {
            "type": "double_top",
            "top_line": top_line,
            "bottom_prefix": bottom_prefix,
            "prefix_visible_len": 2,
            "input_rendered": input_rendered
        }

    elif style_id == "minimal":
        prefix = f"{p['prompt_user']}rts{p['dim']}({p['prompt_arrow']}{short_model}{p['dim']})\033[0m {p['prompt_arrow']}❯\033[0m "
        vlen = len(f"rts({short_model}) ❯ ")
        return {
            "type": "single",
            "bottom_prefix": prefix,
            "prefix_visible_len": vlen,
            "input_rendered": input_rendered
        }

    else: # classic
        bottom_prefix = f"{p['prompt_user']}r.outers >\033[0m "
        sub_info = f"\033[1;33m{perm_icon}\033[0m {short_model}  {p['dim']}·\033[0m  {perm_str}  {p['dim']}·\033[0m  Ready"
        return {
            "type": "double_bottom",
            "bottom_prefix": bottom_prefix,
            "sub_info": sub_info,
            "prefix_visible_len": 11,
            "input_rendered": input_rendered
        }

def render_split_preview_lines(scheme, width=40):
    p = scheme["palette"]
    
    # 2-column Right side code diff preview lines
    lines = [
        f"{p['prompt_user']}> you: \033[0madd a greeting function",
        "",
        f"  \033[1mHere's the change:\033[0m",
        "",
        f"{p['lineno']} 3\033[0m   {p['keyword']}import\033[0m {p['string']}\"fmt\"\033[0m",
        f"{p['lineno']} 4\033[0m",
        f"{p['lineno']} 5\033[0m {p['diff_del']}- func main() {{\033[0m",
        f"{p['lineno']} 5\033[0m {p['diff_add']}+ func greet(name string) {{\033[0m",
        f"{p['lineno']} 6\033[0m {p['diff_add']}+     fmt.Println(\"Hello, \" + name)\033[0m",
        f"{p['lineno']} 7\033[0m {p['diff_add']}+ }}\033[0m"
    ]
    return lines

def select_style_and_theme_interactive():
    if not sys.stdin.isatty():
        return
        
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    current_style, current_theme = get_current_style_settings()
    
    styles_list = list(PROMPT_STYLES.values())
    themes_list = COLOR_SCHEMES
    
    active_tab = 1  # Default directly to Color Scheme tab
    sel_style_idx = next((i for i, s in enumerate(styles_list) if s["id"] == current_style), 0)
    sel_theme_idx = next((i for i, s in enumerate(themes_list) if s["id"] == current_theme), 0)
    
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
                term_cols = 80
                
            modal_width = max(55, min(term_cols - 2, 95))
            
            cur_st = styles_list[sel_style_idx]["id"]
            cur_th_obj = themes_list[sel_theme_idx]
            cur_th = cur_th_obj["id"]
            
            lines = []
            
            # Header Title bar
            title_tag = "color scheme Color Scheme"
            sep_line = "─" * max(10, modal_width - len(title_tag) - 4)
            lines.append(f"\033[1;37m{title_tag}\033[0m   \033[90m_{sep_line}\033[0m")
            
            # Tabs bar
            tab0 = f" 1. Prompt Format ({styles_list[sel_style_idx]['name'].split()[0]}) "
            tab1 = f" 2. Color Scheme ({cur_th_obj['name']}) "
            if active_tab == 1:
                lines.append(f"\033[90m{tab0}\033[0m  \033[1;36m\033[7m{tab1}\033[0m")
            else:
                lines.append(f"\033[1;32m\033[7m{tab0}\033[0m  \033[90m{tab1}\033[0m")
            lines.append(f"\033[90m{'─' * modal_width}\033[0m")
            
            # Two-Column Split Layout
            left_col_w = 32
            right_col_w = modal_width - left_col_w - 4
            if right_col_w < 20:
                right_col_w = 20
                
            preview_lines = render_split_preview_lines(cur_th_obj, width=right_col_w)
            
            if active_tab == 1:
                # Color Scheme List on Left, Live Diff Preview on Right
                total_rows = max(len(themes_list), len(preview_lines))
                for row_idx in range(total_rows):
                    # Left column
                    if row_idx < len(themes_list):
                        th_item = themes_list[row_idx]
                        is_sel = (row_idx == sel_theme_idx)
                        is_curr = (th_item["id"] == current_theme)
                        
                        curr_tag = " (current)" if is_curr else ""
                        name_str = f"{th_item['name']}{curr_tag}"
                        
                        if is_sel:
                            left_str = f"  \033[1;36m> {name_str:<{left_col_w - 4}}\033[0m"
                        else:
                            left_str = f"    \033[37m{name_str:<{left_col_w - 4}}\033[0m"
                    else:
                        left_str = " " * left_col_w
                        
                    # Right column
                    if row_idx < len(preview_lines):
                        right_str = preview_lines[row_idx]
                    else:
                        right_str = ""
                        
                    lines.append(f"{left_str} \033[90m│\033[0m {right_str}")
            else:
                # Prompt Format List on Left, Live Prompt Preview on Right
                total_rows = max(len(styles_list) + 4, len(preview_lines))
                prompt_preview = render_prompt_layout(cur_st, cur_th, model_name="nemotron-3-super-120b", auto_approve=True, current_input="buatkan greeting function", cursor_col=26)
                
                custom_right = [
                    f"\033[1;36mLIVE PROMPT PREVIEW:\033[0m",
                    "",
                    prompt_preview.get("top_line", ""),
                    f"{prompt_preview['bottom_prefix']}{prompt_preview['input_rendered']}",
                    prompt_preview.get("sub_info", ""),
                    "",
                    f"\033[90mStyle: {styles_list[sel_style_idx]['desc'].replace(chr(10), ' | ')}\033[0m"
                ]
                
                for row_idx in range(total_rows):
                    if row_idx < len(styles_list):
                        st_item = styles_list[row_idx]
                        is_sel = (row_idx == sel_style_idx)
                        is_curr = (st_item["id"] == current_style)
                        curr_tag = " (current)" if is_curr else ""
                        name_str = f"{st_item['name'].split('(')[0].strip()}{curr_tag}"
                        
                        if is_sel:
                            left_str = f"  \033[1;32m> {name_str:<{left_col_w - 4}}\033[0m"
                        else:
                            left_str = f"    \033[37m{name_str:<{left_col_w - 4}}\033[0m"
                    else:
                        left_str = " " * left_col_w
                        
                    if row_idx < len(custom_right):
                        right_str = custom_right[row_idx]
                    else:
                        right_str = ""
                        
                    lines.append(f"{left_str} \033[90m│\033[0m {right_str}")
                    
            lines.append(f"\033[90m{'─' * modal_width}\033[0m")
            lines.append(" \033[1;33m↑↓\033[0m \033[90mNavigate\033[0m  \033[1;36m←→ / Tab\033[0m \033[90mSwitch Mode\033[0m  \033[1;32mEnter\033[0m \033[90mSelect & Apply\033[0m  \033[90mEsc Exit\033[0m")
            
            output_buf = ["\033[H"]
            for l in lines:
                output_buf.append(f"\r\033[2K{l}\r\n")
            output_buf.append("\r\033[J")
            sys.stdout.write("".join(output_buf))
            sys.stdout.flush()
            
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
                chosen_theme = themes_list[sel_theme_idx]["id"]
                set_style_settings(chosen_style, chosen_theme)
                break
                
    finally:
        sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
    chosen_style, chosen_theme = get_current_style_settings()
    th_name = THEMES_MAP.get(chosen_theme, {}).get("name", chosen_theme)
    console.print(f"[bold green]✔ Color Scheme & Style applied:[/bold green] [bold cyan]{th_name}[/bold cyan] · Prompt: [bold yellow]{PROMPT_STYLES[chosen_style]['name']}[/bold yellow]\n")
