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

class EscWatcher:
    """Listener keyboard non-blocking untuk mendeteksi tombol ESC / Ctrl+C saat AI berjalan"""
    def __init__(self):
        self.stop_requested = threading.Event()
        self._thread = None
        self._running = False
        self._old_settings = None

    def start(self):
        if not sys.stdin.isatty():
            return
        self._running = True
        try:
            fd = sys.stdin.fileno()
            self._old_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)
            self._thread = threading.Thread(target=self._listen, daemon=True)
            self._thread.start()
        except Exception:
            pass

    def _listen(self):
        try:
            fd = sys.stdin.fileno()
            while self._running and not self.stop_requested.is_set():
                r, _, _ = select.select([fd], [], [], 0.05)
                if r:
                    try:
                        ch = os.read(fd, 1)
                        if ch in (b'\x1b', b'\x03'):
                            self.stop_requested.set()
                            break
                    except Exception:
                        break
        except Exception:
            pass

    def stop(self):
        self._running = False
        if self._old_settings is not None:
            try:
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, self._old_settings)
            except Exception:
                pass

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
5. Memuat panduan spesialisasi skill teknis (`load_skill`).

PRINSIP REKAYASA PERANGKAT LUNAK (SUPERPOWERS & ANTI-SLOP):
- **Anti-Slop Standard**: Hasilkan kode dan antarmuka yang presisi, berkarakter, dan bersih. Hindari kode boilerplate yang membengkak atau teks AI generik.
- **Systematic Debugging & TDD**: Lakukan investigasi akar masalah secara sistematis saat menemukan bug. Verifikasi fungsionalitas dengan pengujian nyata.
- **Skill Terpasang**: {skills_summary}
  *(Gunakan tool `load_skill` kapan saja Anda butuh instruksi detail mengenai skill tertentu seperti antislop-ui, antislop-code, systematic-debugging, test-driven-development, dll)*

ATURAN UTAMA:
- Buat file dengan kode lengkap dan siap jalan tanpa placeholder.
- Pasang dependensi yang dibutuhkan secara otomatis.
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

    watcher = EscWatcher()
    watcher.start()

    session = requests.Session()
    result_container = {"data": None, "error": None, "done": False}

    def fetch_worker():
        try:
            resp = session.post(url, headers=headers, json=payload, timeout=90)
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
