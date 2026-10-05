import os
import subprocess
from rich.prompt import Prompt
from ui import console
from memory import save_global_memory, save_project_memory

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "execute_bash",
            "description": "Menjalankan perintah bash di Termux (pkg install, npm, pip, git, node, python, dll)",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Perintah bash yang akan dijalankan"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Membaca isi file teks atau kode",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path file"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Membuat atau menimpa file dengan kode lengkap",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path tujuan file"},
                    "content": {"type": "string", "description": "Konten file lengkap"}
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Mengganti blok teks lama dengan blok teks baru pada file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path file"},
                    "old_content": {"type": "string", "description": "Teks lama yang diganti"},
                    "new_content": {"type": "string", "description": "Teks baru pengganti"}
                },
                "required": ["filepath", "old_content", "new_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "Melihat file dan folder dalam proyek",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Direktori (default: '.')"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Mencari keyword/string di file proyek (grep)",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Kata kunci pencarian"},
                    "path": {"type": "string", "description": "Direktori pencarian (default: '.')"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Menyimpan preferensi/informasi penting ke memori r.outers",
            "parameters": {
                "type": "object",
                "properties": {
                    "scope": {"type": "string", "enum": ["global", "project"]},
                    "key": {"type": "string"},
                    "value": {"type": "string"}
                },
                "required": ["scope", "key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "Memuat instruksi dan panduan spesialisasi skill teknis (contoh: antislop, antislop-ui, antislop-code, systematic-debugging, test-driven-development, dll)",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string", "description": "Nama skill yang ingin dimuat (misal: antislop, antislop-ui, systematic-debugging, test-driven-development)"}
                },
                "required": ["skill_name"]
            }
        }
    }
]

def execute_tool(name, args, auto_approve=False):
    try:
        if name == "execute_bash":
            cmd = args.get("command", "")
            console.print(f"\n[bold yellow]⚡ Shell Command:[/bold yellow] [bold white]{cmd}[/bold white]")
            
            from config import load_full_config, save_full_config
            full_cfg = load_full_config()
            is_always_allowed = auto_approve or (full_cfg.get("permission_mode") == "always_allow") or full_cfg.get("auto_approve", False)

            if not is_always_allowed:
                console.print("[dim]Opsi: [y] Jalankan  [n] Tolak  [a] Selalu Izinkan (Always Allow)[/dim]")
                resp = Prompt.ask("[yellow]Jalankan?[/yellow]", choices=["y", "n", "a", "always"], default="y").strip().lower()
                if resp == "n":
                    return "Dibatalkan oleh pengguna."
                elif resp in ("a", "always"):
                    full_cfg["permission_mode"] = "always_allow"
                    full_cfg["auto_approve"] = True
                    save_full_config(full_cfg)
                    console.print("[bold green]✔ Mode 'Selalu Izinkan' aktif. Perintah shell selanjutnya akan otomatis dijalankan tanpa konfirmasi.[/bold green]")

            import time
            from client import EscWatcher
            watcher = EscWatcher()
            watcher.start()

            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = "", ""
            start_time = time.time()
            cancelled = False
            
            try:
                with console.status("[bold cyan]⏳ Menjalankan script / perintah...[/bold cyan] [dim](ESC: Stop)[/dim]") as status:
                    while proc.poll() is None:
                        if watcher.stop_requested.is_set():
                            proc.kill()
                            cancelled = True
                            break
                        elapsed = time.time() - start_time
                        status.update(f"[bold cyan]⏳ Menjalankan...[/bold cyan] [dim]({elapsed:.1f}s | ESC: Stop)[/dim]")
                        time.sleep(0.1)

                if cancelled:
                    console.print("\n[bold yellow]⏹ Eksekusi shell dihentikan paksa oleh pengguna (ESC).[/bold yellow]")
                    return "Eksekusi command dibatalkan oleh pengguna (ESC)."

                stdout, stderr = proc.communicate()
            finally:
                watcher.stop()

            elapsed = time.time() - start_time
            if proc.returncode == 0:
                console.print(f"[bold green]✔ Selesai[/bold green] [dim]({elapsed:.1f}s)[/dim]")
            else:
                console.print(f"[bold red]✘ Gagal (Exit code: {proc.returncode})[/bold red] [dim]({elapsed:.1f}s)[/dim]")

            out = (stdout + "\n" + stderr).strip()
            return f"Returncode: {proc.returncode}\nOutput:\n{out}" if out else f"Returncode: {proc.returncode}\n(No output)"

        elif name == "read_file":
            fp = args.get("filepath")
            if not os.path.exists(fp):
                return f"Error: File '{fp}' tidak ditemukan."
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            console.print(f"[dim cyan]📖 Membaca {fp}[/dim cyan]")
            return content

        elif name == "write_file":
            fp = args.get("filepath")
            content = args.get("content", "")
            os.makedirs(os.path.dirname(os.path.abspath(fp)), exist_ok=True)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)
            console.print(f"[bold green]✔ File ditulis: {fp}[/bold green]")
            return f"Sukses menulis {fp}"

        elif name == "edit_file":
            fp = args.get("filepath")
            old_c = args.get("old_content")
            new_c = args.get("new_content")
            if not os.path.exists(fp):
                return f"Error: File '{fp}' tidak ditemukan."
            with open(fp, "r", encoding="utf-8") as f:
                data = f.read()
            if old_c not in data:
                return "Error: old_content tidak cocok dengan isi file."
            data = data.replace(old_c, new_c, 1)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(data)
            console.print(f"[bold green]✔ File diedit: {fp}[/bold green]")
            return f"Sukses mengupdate {fp}"

        elif name == "list_dir":
            d = args.get("directory", ".")
            console.print(f"[dim cyan]📁 Memeriksa folder {d}...[/dim cyan]")
            files = []
            for root, dirs, f_list in os.walk(d):
                dirs[:] = [dr for dr in dirs if dr not in ['.git', 'node_modules', '__pycache__', '.cache']]
                for f in f_list:
                    files.append(os.path.relpath(os.path.join(root, f), d))
                if len(files) > 80:
                    files.append("...(daftar dipotong)")
                    break
            return "\n".join(files) if files else "(Direktori kosong)"

        elif name == "search_code":
            q = args.get("query")
            p = args.get("path", ".")
            cmd = f"grep -rnI --exclude-dir={{node_modules,.git,__pycache__}} '{q}' {p} | head -n 25"
            with console.status(f"[bold cyan]🔍 Mencari '{q}'...[/bold cyan]"):
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.stdout if res.stdout else "Tidak ditemukan."

        elif name == "remember":
            scope = args.get("scope", "global")
            key, val = args.get("key"), args.get("value")
            if scope == "global":
                save_global_memory(key, val)
            else:
                save_project_memory(key, val)
            console.print(f"[magenta]🧠 Memory [{scope}]: {key} = {val}[/magenta]")
            return f"Tersimpan di memory {scope}."

        elif name == "load_skill":
            s_name = args.get("skill_name", "").strip().lower()
            skills_dirs = [
                os.path.join(os.path.dirname(__file__), "skills"),
                os.path.expanduser("~/.agents/skills"),
                os.path.expanduser("~/.gemini/antigravity-cli/builtin/skills")
            ]
            for sdir in skills_dirs:
                target_file = os.path.join(sdir, s_name, "SKILL.md")
                if os.path.exists(target_file):
                    with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    console.print(f"[bold cyan]⚡ Memuat Skill:[/bold cyan] [bold green]{s_name}[/bold green]")
                    return f"=== PANDUAN SPESIALISASI SKILL '{s_name}' ===\n{content}"
            return f"Skill '{s_name}' tidak ditemukan di folder skills rts."

    except Exception as e:
        return f"Error tool '{name}': {str(e)}"

    return "Tool tidak dikenal."
