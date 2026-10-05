import os
import json
import requests
from ui import console
from memory import load_memory
from tools import TOOLS_SCHEMA

def build_system_prompt():
    memory = load_memory()
    cwd = os.getcwd()
    
    return f"""Anda adalah R.OUTERS AGENT, AI software engineer otonom di Android Linux Termux.

STATUS LINGKUNGAN:
- Direktori Kerja: {cwd}
- Memori Tersimpan:
{json.dumps(memory, indent=2)}

KEMAMPUAN:
1. Menjalankan bash Termux secara nyata (`pkg install`, `npm install`, `pip install`, `node`, `python`, `git`, dll).
2. Membaca, membuat, mencari, dan mengedit file kode secara otonom.
3. Menangani error secara otomatis (auto-healing).
4. Menyimpan data penting ke memori (`remember`).

ATURAN:
- Buat file dengan kode lengkap dan siap jalan.
- Install dependensi (npm/pip/pkg) otomatis jika belum ada.
"""

def call_ai(messages, config):
    url = f"{config['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": config["model"],
        "messages": messages,
        "tools": TOOLS_SCHEMA,
        "tool_choice": "auto"
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        console.print(f"[bold red]API Error:[/bold red] {str(e)}")
        return None
