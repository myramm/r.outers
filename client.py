import os
import sys
import json
import time
import requests
import threading
import termios
import tty
import select
from ui import console
from memory import load_memory
from tools import TOOLS_SCHEMA
from queue_manager import AsyncInputQueueWatcher

def get_available_skills_list():
    found = set()
    dirs = [
        os.path.join(os.path.dirname(__file__), "skills"),
        os.path.expanduser("~/.agents/skills"),
        os.path.expanduser("~/.gemini/antigravity-cli/builtin/skills")
    ]
    for sdir in dirs:
        if os.path.exists(sdir):
            for d in os.listdir(sdir):
                if os.path.isdir(os.path.join(sdir, d)) and os.path.exists(os.path.join(sdir, d, "SKILL.md")):
                    found.add(d)
    return sorted(list(found))

def build_system_prompt():
    memory = load_memory()
    cwd = os.getcwd()
    skills = get_available_skills_list()
    skills_summary = ", ".join(skills) if skills else "antislop, antislop-ui, antislop-code, systematic-debugging, test-driven-development"
    
    return f"""Anda adalah R.OUTERS AGENT (RTS), AI software engineer otonom di Android Linux Termux.

STATUS LINGKUNGAN:
- Direktori Kerja: {cwd}
- Memori Tersimpan:
{json.dumps(memory, indent=2)}

KEMAMPUAN UTAMA:
1. Menjalankan bash Termux secara nyata via tool `execute_bash` (`pkg install`, `npm install`, `pip install`, `node`, `python`, `git`, dll).
2. Membaca file (`read_file`), membuat file (`write_file`), mengedit file (`edit_file`), dan menghapus file (`delete_file`).
3. Mencari file dan string (`search_code`, `list_dir`).
4. Mengakses URL web (`fetch_url`).
5. Menyimpan data penting ke memori (`remember`).
6. Memuat panduan spesialisasi skill teknis (`load_skill`).
7. Mengajukan pertanyaan interaktif dengan pilihan menu panah keyboard (`ask_user`).

PRINSIP REKAYASA PERANGKAT LUNAK (SUPERPOWERS & ANTI-SLOP):
- **Anti-Slop Standard**: Hasilkan kode dan antarmuka yang presisi, berkarakter, dan bersih. Hindari kode boilerplate yang membengkak atau teks AI generik.
- **Systematic Debugging & TDD**: Lakukan investigasi akar masalah secara sistematis saat menemukan bug. Verifikasi fungsionalitas dengan pengujian nyata.
- **Skill Terpasang**: {skills_summary}
  *(Gunakan tool `load_skill` kapan saja Anda butuh instruksi detail mengenai skill tertentu)*

ATURAN UTAMA AGENT:
- JANGAN HANYA MEMBERIKAN KODE SEBAGAI TEKS BIASA DI CHAT! Ketika user meminta Anda membuat, mengedit, atau membangun web/proyek/skrip, Anda WAJIB langsung memanggil tool `write_file` atau `edit_file` untuk menulis file nyata ke sistem file.
- KETIKA BUTUH KLARIFIKASI / PILIHAN DARI USER (seperti mode antislop 1/2, arah desain, atau pilihan teknologi): PANGGIL tool `ask_user` agar muncul menu interaktif dengan tombol panah (UP/DOWN) di terminal pengguna, JANGAN mencetak teks pertanyaan nomor manual di chat!
- Buat file dengan kode lengkap dan siap jalan tanpa placeholder.
- Pasang dependensi yang dibutuhkan secara otomatis dengan memanggil tool `execute_bash`.
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

    watcher = AsyncInputQueueWatcher()
    watcher.start()

    session = requests.Session()
    result_container = {"data": None, "error": None, "done": False}

    def fetch_worker():
        try:
            resp = session.post(url, headers=headers, json=payload, timeout=180)
            if resp.status_code == 200:
                result_container["data"] = resp.json()
            else:
                result_container["error"] = f"HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            result_container["error"] = str(e)
        finally:
            result_container["done"] = True

    worker_t = threading.Thread(target=fetch_worker, daemon=True)
    worker_t.start()

    try:
        while not result_container["done"]:
            if watcher.stop_requested.is_set():
                session.close()
                watcher.stop()
                console.print("\n[bold yellow]⏹ Proses dihentikan oleh pengguna (ESC ditekan).[/bold yellow]")
                return {"cancelled": True}
            time.sleep(0.05)
    finally:
        watcher.stop()

    if watcher.stop_requested.is_set():
        console.print("\n[bold yellow]⏹ Proses dihentikan oleh pengguna (ESC ditekan).[/bold yellow]")
        return {"cancelled": True}

    if result_container["data"]:
        return result_container["data"]
    elif result_container["error"]:
        if not watcher.stop_requested.is_set():
            console.print(f"[bold red]API Error:[/bold red] {result_container['error']}")
        return None

    return None
