import os
import sys
import json
from rich.prompt import Prompt
from ui import console

CONFIG_FILE = os.path.expanduser("~/.routers_config.json")
ENV_FILE = os.path.expanduser("~/.env")

PRESET_PROVIDERS = {
    "9router": {
        "name": "9Router (Self-Hosted AI Gateway)",
        "base_url": "",
        "default_model": "ag/gemini-3.7-flash-high"
    },
    "clouvia": {
        "name": "Clouvia Router (coding-high, free-model)",
        "base_url": "https://router.clouvia.id/v1",
        "default_model": "free-model"
    },
    "atria": {
        "name": "Atria ASI (Atria-Dawn-Preview)",
        "base_url": "https://api.atria-asi.ai/v1",
        "default_model": "Atria-Dawn-Preview"
    },
    "nvidia": {
        "name": "NVIDIA NIM / Build (integrate.api.nvidia.com)",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "default_model": "nvidia/llama-3.1-nemotron-70b-instruct"
    },
    "openrouter": {
        "name": "OpenRouter (openrouter.ai/api/v1)",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "deepseek/deepseek-r1:free"
    }
}

def load_env_keys():
    keys = {}
    paths = [".env", ENV_FILE]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            keys[k.strip()] = v.strip().strip("'\"")
            except Exception:
                pass
    return keys

def load_full_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                if "base_url" in data and "providers" not in data:
                    migrated = {
                        "active_provider": "clouvia",
                        "providers": {
                            "clouvia": {
                                "name": "Clouvia Router",
                                "base_url": "https://router.clouvia.id/v1",
                                "api_key": data.get("api_key", ""),
                                "model": "free-model"
                            }
                        }
                    }
                    save_full_config(migrated)
                    return migrated
                return data
        except Exception:
            pass
    return setup_initial_config()

def save_full_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=2)

THINKING_MODES = {
    "off": {
        "id": "off",
        "label": "Off",
        "desc": "Tanpa thinking (Respons instan, hemat token)",
        "budget_tokens": 0,
        "reasoning_effort": "none",
        "tag": "OFF",
        "color": "\033[90m"
    },
    "low": {
        "id": "low",
        "label": "Low",
        "desc": "Thinking ringan (~2k token, penalaran cepat)",
        "budget_tokens": 2048,
        "reasoning_effort": "low",
        "tag": "LOW",
        "color": "\033[1;36m"
    },
    "medium": {
        "id": "medium",
        "label": "Medium",
        "desc": "Thinking seimbang (~8k token, logika analitis)",
        "budget_tokens": 8192,
        "reasoning_effort": "medium",
        "tag": "MED",
        "color": "\033[1;34m"
    },
    "high": {
        "id": "high",
        "label": "High",
        "desc": "Thinking mendalam (~16k token, arsitektur & coding)",
        "budget_tokens": 16384,
        "reasoning_effort": "high",
        "tag": "HIGH",
        "color": "\033[1;35m"
    },
    "max": {
        "id": "max",
        "label": "Max",
        "desc": "Thinking maksimal (~32k token, deep reasoning & proof)",
        "budget_tokens": 32768,
        "reasoning_effort": "high",
        "tag": "MAX",
        "color": "\033[1;31m"
    }
}

REASONING_MODEL_KEYWORDS = [
    "thinking", "reason", "r1", "qwq", "o1", "o3", "o4", "gpt-5",
    "claude-3-7", "claude-sonnet-5", "claude-opus-4.8",
    "gemini-2.0-flash-thinking", "gemini-2.5-flash-thinking", "gemini-3.8-flash-high",
    "nemotron", "cosmos-reason", "qwen-3.8-max-thinking", "glm5.3-thinking",
    "deepseek-v4-pro", "deepseek-r1", "coding-high", "atria-dawn"
]

def is_thinking_supported(model_id):
    if not model_id:
        return False
    m_lower = str(model_id).lower()
    for kw in REASONING_MODEL_KEYWORDS:
        if kw in m_lower:
            return True
    return False

def get_thinking_mode():
    full_cfg = load_full_config()
    return full_cfg.get("thinking_mode", "high")

def update_thinking_mode(mode):
    full_cfg = load_full_config()
    full_cfg["thinking_mode"] = str(mode).lower()
    save_full_config(full_cfg)
    return full_cfg["thinking_mode"]

def get_thinking_budget(mode_str):
    mode_str = str(mode_str).lower()
    if mode_str in THINKING_MODES:
        return THINKING_MODES[mode_str]["budget_tokens"]
    try:
        val = int(mode_str)
        return max(0, val)
    except Exception:
        return 16384

def get_active_config():
    full_cfg = load_full_config()
    active_key = full_cfg.get("active_provider", "nvidia")
    providers = full_cfg.get("providers", {})
    
    if active_key not in providers:
        if providers:
            active_key = list(providers.keys())[0]
            full_cfg["active_provider"] = active_key
            save_full_config(full_cfg)
        else:
            return setup_initial_config()["providers"]["nvidia"]

    curr = providers[active_key]
    
    # Auto-inject from env jika kosong
    env_keys = load_env_keys()
    api_k = curr.get("api_key", "")
    if not api_k:
        if active_key == "9router":
            api_k = env_keys.get("NINEROUTER_API_KEY", env_keys.get("ROUTER9_API_KEY", env_keys.get("NINE_ROUTER_API_KEY", os.environ.get("NINEROUTER_API_KEY", os.environ.get("ROUTER9_API_KEY", os.environ.get("NINE_ROUTER_API_KEY", ""))))))
        elif active_key == "clouvia":
            api_k = env_keys.get("CLOUVIA_API_KEY", os.environ.get("CLOUVIA_API_KEY", ""))
        elif active_key == "atria":
            api_k = env_keys.get("ATRIA_API_KEY", os.environ.get("ATRIA_API_KEY", ""))
        elif active_key == "nvidia":
            api_k = env_keys.get("NVIDIA_API_KEY", os.environ.get("NVIDIA_API_KEY", os.environ.get("NVAPI_KEY", "")))
        elif active_key == "openrouter":
            api_k = env_keys.get("OPENROUTER_API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))
        else:
            api_k = env_keys.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))

    return {
        "provider_id": active_key,
        "provider_name": curr.get("name", active_key),
        "base_url": curr.get("base_url", "").rstrip("/"),
        "api_key": api_k,
        "model": curr.get("model", "nvidia/nemotron-3-super-120b-a12b"),
        "timeout": curr.get("timeout", 180),
        "temperature": curr.get("temperature", 0.2),
        "max_tokens": curr.get("max_tokens", 8192),
        "thinking_mode": full_cfg.get("thinking_mode", curr.get("thinking_mode", "high")),
        "settings": full_cfg.get("settings", {})
    }

def update_active_model(new_model):
    full_cfg = load_full_config()
    active_key = full_cfg.get("active_provider")
    if active_key in full_cfg.get("providers", {}):
        full_cfg["providers"][active_key]["model"] = new_model
        save_full_config(full_cfg)
        return True
    return False

def add_new_provider():
    console.print("\n[bold cyan]➕ Tambah / Setup Provider[/bold cyan]")
    console.print("Pilih Provider:")
    keys = list(PRESET_PROVIDERS.keys())
    for idx, k in enumerate(keys, 1):
        p = PRESET_PROVIDERS[k]
        console.print(f"  [bold yellow]{idx}[/bold yellow]. {p['name']}")
    console.print(f"  [bold yellow]{len(keys) + 1}[/bold yellow]. Custom Provider / Endpoint Lain")
    console.print(f"  [bold red]e / E[/bold red]. Batal")

    choice = Prompt.ask(f"Pilih (1-{len(keys) + 1}, e)", default="1").strip()
    if choice.lower() == "e":
        console.print("[yellow]Batal menambah provider.[/yellow]")
        return get_active_config()

    try:
        c_idx = int(choice) - 1
        if 0 <= c_idx < len(keys):
            p_key = keys[c_idx]
            preset = PRESET_PROVIDERS[p_key]
            name = preset["name"]
            base_url = preset["base_url"]
            default_m = preset["default_model"]
            prov_id = p_key

            if not base_url or p_key == "9router":
                raw_url = Prompt.ask("Domain / Base URL 9Router Anda (contoh: https://your-9router.up.railway.app)").strip()
                if not raw_url or raw_url.lower() == "e":
                    console.print("[yellow]Batal menambah provider.[/yellow]")
                    return get_active_config()
                if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
                    raw_url = "https://" + raw_url
                raw_url = raw_url.rstrip("/")
                if not raw_url.endswith("/v1"):
                    raw_url = f"{raw_url}/v1"
                base_url = raw_url
        elif c_idx == len(keys):
            prov_id = Prompt.ask("ID Provider unik (contoh: sambanova / deepinfra)").strip().lower()
            if not prov_id or prov_id == "e":
                return get_active_config()
            name = Prompt.ask("Nama Tampilan Provider", default=prov_id.capitalize())
            base_url = Prompt.ask("Base URL (contoh: https://api.sambanova.ai/v1)").strip()
            if not base_url.startswith("http://") and not base_url.startswith("https://"):
                base_url = "https://" + base_url
            base_url = base_url.rstrip("/")
            if not base_url.endswith("/v1"):
                base_url = f"{base_url}/v1"
            default_m = Prompt.ask("Default Model", default="default-model")
        else:
            console.print("[bold red]❌ Input nomor tidak valid![/bold red]")
            return get_active_config()
    except ValueError:
        console.print("[bold red]❌ Input tidak valid![/bold red]")
        return get_active_config()

    api_key = Prompt.ask("Masukkan / Paste API Key").strip()
    model = Prompt.ask("Model", default=default_m)

    full_cfg = load_full_config()
    if "providers" not in full_cfg:
        full_cfg["providers"] = {}

    full_cfg["providers"][prov_id] = {
        "name": name,
        "base_url": base_url.rstrip("/"),
        "api_key": api_key,
        "model": model
    }
    full_cfg["active_provider"] = prov_id
    save_full_config(full_cfg)
    console.print(f"[bold green]✔ Provider '{name}' berhasil disimpan dan diaktifkan![/bold green]\n")
    return get_active_config()

def switch_provider():
    full_cfg = load_full_config()
    providers = full_cfg.get("providers", {})
    if not providers:
        return add_new_provider()

    if not sys.stdin.isatty():
        return get_active_config()

    p_keys = list(providers.keys())
    active_key = full_cfg.get("active_provider")
    selected = 0
    for i, k in enumerate(p_keys):
        if k == active_key:
            selected = i
            break

    options = []
    for k in p_keys:
        p = providers[k]
        is_act = " (Aktif)" if k == active_key else ""
        options.append({"id": k, "label": f"{p.get('name', k)} [{p.get('model')}]{is_act}"})
    options.append({"id": "+", "label": "➕ Tambah Provider Baru"})
    options.append({"id": "back", "label": "⬅️ Batal / Kembali"})

    fd = sys.stdin.fileno()
    import termios, tty
    old_settings = termios.tcgetattr(fd)

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
            lines.append(f"\033[1;36m📡  Pilih Provider AI Aktif\033[0m{' ' * (width - 28)}\033[90m[Esc]\033[0m")
            lines.append(f"\033[90m{'─' * width}\033[0m")
            lines.append("")

            for idx, opt in enumerate(options):
                is_sel = (idx == selected)
                pfx = "▸ " if is_sel else "  "
                avail = width - 4
                row_str = f"{pfx}{opt['label']}"
                if is_sel:
                    lines.append(f"\033[7m\033[1m {row_str:<{avail}} \033[0m")
                else:
                    lines.append(f"{pfx}\033[37m{opt['label']}\033[0m")

            lines.append("")
            lines.append(f"\033[90m{'─' * width}\033[0m")
            lines.append(" \033[1;33m↑↓/Tab\033[0m \033[90mPilih\033[0m  \033[1;32mEnter\033[0m \033[90mAktifkan\033[0m  \033[90mEsc Kembali\033[0m")

            out_buf = ["\033[H"]
            for l in lines:
                out_buf.append(f"\r\033[2K{l}\r\n")
            out_buf.append("\r\033[J")
            sys.stdout.write("".join(out_buf))
            sys.stdout.flush()

            from settings import read_key_raw_fd
            k = read_key_raw_fd(fd)
            if k in ('ESC', 'CTRL_C'):
                return get_active_config()

            elif k in ('UP', 'SHIFT_TAB'):
                selected = (selected - 1) % len(options)
            elif k in ('DOWN', 'TAB'):
                selected = (selected + 1) % len(options)
            elif k == 'ENTER':
                chosen = options[selected]["id"]
                break

    finally:
        sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if chosen == "+":
        return add_new_provider()
    elif chosen == "back":
        return get_active_config()
    else:
        full_cfg["active_provider"] = chosen
        save_full_config(full_cfg)
        target = providers[chosen]
        console.print(f"[bold green]✔ Berganti ke Provider: {target.get('name')} (Model: {target.get('model')})[/bold green]\n")
        return get_active_config()

def setup_initial_config():
    return {
        "active_provider": "clouvia",
        "thinking_mode": "high",
        "providers": {
            "clouvia": {
                "name": "Clouvia Router",
                "base_url": "https://router.clouvia.id/v1",
                "api_key": "",
                "model": "free-model"
            }
        }
    }
