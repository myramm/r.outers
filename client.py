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
EscWatcher = AsyncInputQueueWatcher

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

def build_system_prompt(thinking_mode="high", model_id=None):
    from config import is_thinking_supported
    memory = load_memory()
    cwd = os.getcwd()
    skills = get_available_skills_list()
    skills_summary = ", ".join(skills) if skills else "antislop, antislop-ui, antislop-code, systematic-debugging, test-driven-development"
    
    thinking_instruction = ""
    # Only append thinking instructions if model supports reasoning (or model_id not specified)
    if model_id is None or is_thinking_supported(model_id):
        th_m = str(thinking_mode).lower()
        if th_m == "off":
            thinking_instruction = "\n- **Mode Thinking**: OFF (Langsung berikan solusi dan tindakan secara padat dan efisien tanpa overthinking)."
        elif th_m == "low":
            thinking_instruction = "\n- **Mode Thinking**: LOW (~2k token budget - lakukan penalaran ringkas dan cepat sebelum eksekusi)."
        elif th_m == "medium":
            thinking_instruction = "\n- **Mode Thinking**: MEDIUM (~8k token budget - lakukan analisis seimbang dan terstruktur sebelum eksekusi)."
        elif th_m == "max":
            thinking_instruction = "\n- **Mode Thinking**: MAX (~32k token budget - lakukan penalaran mendalam maksimum, pembuktian logis, dan mitigasi edge cases secara ekstensif)."
        elif th_m.isdigit():
            thinking_instruction = f"\n- **Mode Thinking**: CUSTOM ({th_m} token budget - sesuaikan kedalaman analisis dengan alokasi token ini)."
        else:
            thinking_instruction = "\n- **Mode Thinking**: HIGH (~16k token budget - lakukan penalaran arsitektur mendalam, step-by-step reasoning, dan perencanaan sistematis sebelum menulis kode atau memanggil tools)."

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
- **Skill Terpasang**: {skills_summary}{thinking_instruction}
  *(Gunakan tool `load_skill` kapan saja Anda butuh instruksi detail mengenai skill tertentu)*

ATURAN UTAMA AGENT:
- JANGAN HANYA MEMBERIKAN KODE SEBAGAI TEKS BIASA DI CHAT! Ketika user meminta Anda membuat, mengedit, atau membangun web/proyek/skrip, Anda WAJIB langsung memanggil tool `write_file` atau `edit_file` untuk menulis file nyata ke sistem file.
- KETIKA BUTUH KLARIFIKASI / PILIHAN DARI USER (seperti mode antislop 1/2, arah desain, atau pilihan teknologi): PANGGIL tool `ask_user` agar muncul menu interaktif dengan tombol panah (UP/DOWN) di terminal pengguna, JANGAN mencetak teks pertanyaan nomor manual di chat!
- Buat file dengan kode lengkap dan siap jalan tanpa placeholder.
- Pasang dependensi yang dibutuhkan secara otomatis dengan memanggil tool `execute_bash`.
"""

def call_ai(messages, config):
    from config import is_thinking_supported, get_thinking_budget
    url = f"{config['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    thinking_mode = str(config.get("thinking_mode", "high")).lower()
    model_id = config.get("model", "")
    model_supports_thinking = is_thinking_supported(model_id)

    payload = {
        "model": model_id,
        "messages": messages,
        "tools": TOOLS_SCHEMA,
        "tool_choice": "auto"
    }

    # Inject reasoning_effort & thinking budget ONLY if model supports thinking and mode is not 'off'
    if model_supports_thinking and thinking_mode != "off":
        if thinking_mode in ("low", "medium", "high"):
            payload["reasoning_effort"] = thinking_mode
        elif thinking_mode == "max":
            payload["reasoning_effort"] = "high"

        budget = get_thinking_budget(thinking_mode)
        if budget >= 1024:
            payload["thinking"] = {
                "type": "enabled",
                "budget_tokens": budget
            }

    watcher = AsyncInputQueueWatcher()

    session = requests.Session()
    result_container = {"data": None, "error": None, "done": False}

    def fetch_worker():
        try:
            resp = session.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                result_container["data"] = resp.json()
            elif resp.status_code == 400 and any(k in resp.text.lower() for k in ("reasoning", "thinking", "extra_forbidden", "unrecognized")):
                # Graceful fallback: retry without reasoning/thinking parameter if endpoint rejects them
                fallback_payload = {k: v for k, v in payload.items() if k not in ("reasoning_effort", "thinking", "reasoning")}
                fb_resp = session.post(url, headers=headers, json=fallback_payload, timeout=60)
                if fb_resp.status_code == 200:
                    result_container["data"] = fb_resp.json()
                else:
                    result_container["error"] = f"HTTP {fb_resp.status_code}: {fb_resp.text}"
            else:
                result_container["error"] = f"HTTP {resp.status_code}: {resp.text}"
        except requests.exceptions.Timeout:
            result_container["error"] = "Permintaan ke server AI timeout (60 detik)."
        except Exception as e:
            result_container["error"] = str(e)
        finally:
            result_container["done"] = True

    worker_t = threading.Thread(target=fetch_worker, daemon=True)
    worker_t.start()

    from ui import get_turn_tip

    if model_supports_thinking and thinking_mode != "off":
        th_tag = thinking_mode.capitalize()
        status_label = f"[bold cyan]Thinking ({th_tag})...[/bold cyan] [dim](ESC: Stop)[/dim]"
    else:
        status_label = "[bold cyan]Thinking...[/bold cyan] [dim](ESC: Stop)[/dim]"

    current_tip = get_turn_tip()
    tip_line = f"  [dim]└ Tip: {current_tip}[/dim]"

    try:
        with console.status(f"{status_label}\n{tip_line}") as status:
            def update_thinking_status():
                txt = watcher.get_buffer_text()
                if txt:
                    status.update(f"{status_label}\n{tip_line}\n  [bold cyan]>[/bold cyan] [bold white]{txt}[/bold white][bold green]█[/bold green]")
                else:
                    status.update(f"{status_label}\n{tip_line}")

            watcher.on_change = update_thinking_status
            watcher.start()

            while not result_container["done"]:
                if watcher.stop_requested.is_set():
                    session.close()
                    console.print("\n[bold yellow]⏹ Proses dihentikan oleh pengguna (ESC ditekan).[/bold yellow]\n")
                    return {"cancelled": True}
                update_thinking_status()
                time.sleep(0.08)
    finally:
        watcher.stop()

    if watcher.stop_requested.is_set():
        console.print("\n[bold yellow]⏹ Proses dihentikan oleh pengguna (ESC ditekan).[/bold yellow]\n")
        return {"cancelled": True}

    if result_container["data"]:
        return result_container["data"]
    elif result_container["error"]:
        if not watcher.stop_requested.is_set():
            console.print(f"[bold red]API Error:[/bold red] {result_container['error']}\n")
        return None

    return None
