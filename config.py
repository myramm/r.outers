import os
import json
from rich.prompt import Prompt, Confirm
from ui import console

CONFIG_FILE = os.path.expanduser("~/.routers_config.json")

PRESET_PROVIDERS = {
    "openrouter": {
        "name": "OpenRouter (DeepSeek V3/R1, Claude, GPT, Gemini)",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "deepseek/deepseek-chat"
    },
    "deepseek": {
        "name": "DeepSeek Official",
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat"
    },
    "groq": {
        "name": "Groq Cloud (Ultra Fast Llama 3.3)",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile"
    },
    "openai": {
        "name": "OpenAI Official (GPT-4o, o1, o3-mini)",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini"
    },
    "ollama": {
        "name": "Ollama (Local / Termux)",
        "base_url": "http://localhost:11434/v1",
        "default_model": "qwen2.5-coder"
    },
    "together": {
        "name": "Together AI",
        "base_url": "https://api.together.xyz/v1",
        "default_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    }
}

def load_full_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                # Migrasi struktur lama jika ada
                if "base_url" in data and "providers" not in data:
                    migrated = {
                        "active_provider": "custom_default",
                        "providers": {
                            "custom_default": {
                                "name": "Default Provider",
                                "base_url": data.get("base_url", ""),
                                "api_key": data.get("api_key", ""),
                                "model": data.get("model", "deepseek-chat")
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

def get_active_config():
    full_cfg = load_full_config()
    active_key = full_cfg.get("active_provider", "openrouter")
    providers = full_cfg.get("providers", {})
    
    if active_key not in providers:
        if providers:
            active_key = list(providers.keys())[0]
            full_cfg["active_provider"] = active_key
            save_full_config(full_cfg)
        else:
            return setup_initial_config()["providers"]["openrouter"]

    curr = providers[active_key]
    return {
        "provider_id": active_key,
        "provider_name": curr.get("name", active_key),
        "base_url": curr.get("base_url", ""),
        "api_key": curr.get("api_key", ""),
        "model": curr.get("model", "deepseek-chat")
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
    console.print("\n[bold cyan]➕ Tambah Provider Baru[/bold cyan]")
    console.print("Pilih Preset atau Custom:")
    keys = list(PRESET_PROVIDERS.keys())
    for idx, k in enumerate(keys, 1):
        p = PRESET_PROVIDERS[k]
        console.print(f"  [bold yellow]{idx}[/bold yellow]. {p['name']}")
    console.print(f"  [bold yellow]{len(keys) + 1}[/bold yellow]. Custom Provider / Endpoint Lain")

    choice = Prompt.ask(f"Pilih (1-{len(keys) + 1})", default="1")
    try:
        c_idx = int(choice) - 1
        if 0 <= c_idx < len(keys):
            p_key = keys[c_idx]
            preset = PRESET_PROVIDERS[p_key]
            name = preset["name"]
            base_url = preset["base_url"]
            default_m = preset["default_model"]
            prov_id = p_key
        else:
            prov_id = Prompt.ask("ID Provider unik (contoh: sambanova / deepinfra)").strip().lower()
            name = Prompt.ask("Nama Tampilan Provider", default=prov_id.capitalize())
            base_url = Prompt.ask("Base URL (contoh: https://api.sambanova.ai/v1)")
            default_m = Prompt.ask("Default Model")
    except ValueError:
        prov_id = "custom"
        name = "Custom Provider"
        base_url = Prompt.ask("Base URL")
        default_m = Prompt.ask("Default Model")

    api_key = Prompt.ask("Masukkan API Key", password=True)
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

    console.print("\n[bold cyan]📡 Daftar Provider Tersimpan:[/bold cyan]")
    p_keys = list(providers.keys())
    active_key = full_cfg.get("active_provider")

    for idx, k in enumerate(p_keys, 1):
        p = providers[k]
        is_active = " [bold green](AKTIF)[/bold green]" if k == active_key else ""
        console.print(f"  [bold yellow]{idx}[/bold yellow]. {p.get('name', k)} ({p.get('model')}){is_active}")
    console.print(f"  [bold cyan]+[/bold cyan]. Tambah Provider Baru")

    sel = Prompt.ask("\nPilih nomor provider untuk diaktifkan atau '+' untuk tambah", default="1")
    if sel.strip() == "+":
        return add_new_provider()
    
    try:
        idx = int(sel) - 1
        if 0 <= idx < len(p_keys):
            target_key = p_keys[idx]
            full_cfg["active_provider"] = target_key
            save_full_config(full_cfg)
            target = providers[target_key]
            console.print(f"[bold green]✔ Berganti ke Provider: {target.get('name')} (Model: {target.get('model')})[/bold green]\n")
            return get_active_config()
    except Exception:
        pass
    
    return get_active_config()

def setup_initial_config():
    console.print("\n[bold cyan]🛠️ Inisialisasi r.outers Configuration[/bold cyan]")
    return add_new_provider()
