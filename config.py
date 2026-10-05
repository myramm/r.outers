import os
import json
from rich.prompt import Prompt
from ui import console

CONFIG_FILE = os.path.expanduser("~/.routers_config.json")

PROVIDERS = {
    "1": {"name": "OpenRouter (DeepSeek V3, Claude, GPT-4o)", "base_url": "https://openrouter.ai/api/v1", "default_model": "deepseek/deepseek-chat"},
    "2": {"name": "DeepSeek Official", "base_url": "https://api.deepseek.com", "default_model": "deepseek-chat"},
    "3": {"name": "Groq Cloud (Llama 3.3 70B)", "base_url": "https://api.groq.com/openai/v1", "default_model": "llama-3.3-70b-versatile"},
    "4": {"name": "OpenAI Official", "base_url": "https://api.openai.com/v1", "default_model": "gpt-4o-mini"},
    "5": {"name": "Custom Endpoint (Ollama / Local / API Lain)", "base_url": "", "default_model": ""}
}

def setup_config():
    console.print("\n[bold cyan]🛠️ r.outers Setup Konfigurasi[/bold cyan]")
    for k, v in PROVIDERS.items():
        console.print(f"  [bold yellow]{k}[/bold yellow]. {v['name']}")
    
    choice = Prompt.ask("\nPilih Provider (1-5)", default="1")
    prov = PROVIDERS.get(choice, PROVIDERS["1"])

    base_url = prov["base_url"] or Prompt.ask("Masukkan Base URL")
    default_m = prov["default_model"] or "llama3"

    api_key = Prompt.ask("Masukkan API Key", password=True)
    model = Prompt.ask("Nama Model", default=default_m)

    cfg = {"base_url": base_url.rstrip("/"), "api_key": api_key, "model": model}
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    console.print("[bold green]✔ Konfigurasi tersimpan![/bold green]\n")
    return cfg

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return setup_config()
