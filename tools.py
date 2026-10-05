import os
import sys
import subprocess
import termios
import tty
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
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Menghapus file yang tidak diperlukan",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path file yang akan dihapus"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Mengambil konten dari URL web (HTTP GET)",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL yang akan diakses"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ask_user",
            "description": "Menampilkan dialog pertanyaan interaktif dengan opsi pilihan (multiple choice) kepada pengguna menggunakan navigasi tombol panah (UP/DOWN/ENTER). Gunakan tool ini KAPAN SAJA Anda membutuhkan klarifikasi, pilihan arah desain, konfirmasi aturan antislop, atau keputusan dari pengguna daripada mengetik pertanyaan panjang di chat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Pertanyaan yang diajukan ke pengguna"
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Daftar opsi pilihan yang dapat dipilih pengguna"
                    },
                    "allow_custom": {
                        "type": "boolean",
                        "description": "Apakah mengizinkan input teks manual custom (default: true)"
                    }
                },
                "required": ["question", "options"]
            }
        }
    }
]

def interactive_ask_user(question, options, allow_custom=True):
    if not sys.stdin.isatty():
        from rich.prompt import Prompt
        console.print(f"\n[bold cyan]❓ {question}[/bold cyan]")
        for idx, opt in enumerate(options, 1):
            console.print(f"  [bold yellow]{idx}[/bold yellow]. {opt}")
        if allow_custom:
            console.print("  [bold cyan]c[/bold cyan]. Ketik jawaban kustom")
        ans = Prompt.ask("Pilih jawaban (nomor atau teks)", default="1").strip()
        if ans.lower() == "c" and allow_custom:
            return Prompt.ask("Ketik jawaban Anda").strip()
        try:
            num = int(ans) - 1
            if 0 <= num < len(options):
                return options[num]
        except Exception:
            pass
        return ans

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    all_options = list(options)
    if allow_custom:
        all_options.append("✏️  Ketik jawaban kustom manual...")

    selected_idx = 0

    try:
        tty.setraw(fd)
        sys.stdout.write("\033[?25l\033[?7l")  # Sembunyikan kursor & matikan wrap
        sys.stdout.flush()

        from slash_prompt import read_key_raw

        last_rendered_lines = 0

        while True:
            try:
                term_cols = os.get_terminal_size().columns
            except Exception:
                term_cols = 50

            if last_rendered_lines > 0:
                buf = []
                for _ in range(last_rendered_lines):
                    buf.append("\033[B\033[2K")
                buf.append("\033[J")
                buf.append(f"\033[{last_rendered_lines}A\r")
                sys.stdout.write("".join(buf))
                sys.stdout.flush()

            lines = []
            box_width = max(24, min(term_cols - 2, 70))
            inner_w = box_width - 4
            sep = "─" * max(2, box_width - 16)
            lines.append(f"\033[1;36m╭─ ❓ Pertanyaan AI {sep}╮\033[0m")
            from styles import wrap_text
            for ql in question.splitlines():
                if ql.strip():
                    wrapped_chunks = wrap_text(ql, width=inner_w)
                    for chunk in wrapped_chunks:
                        lines.append(f"\033[1;36m│\033[0m \033[1;37m{chunk:<{inner_w}}\033[0m \033[1;36m│\033[0m")
            lines.append(f"\033[1;36m╰{'─' * (box_width - 2)}╯\033[0m")

            for idx, opt in enumerate(all_options):
                is_sel = (idx == selected_idx)
                opt_str = opt[:max(10, box_width - 6)]
                if is_sel:
                    lines.append(f"  \033[1;32m▸\033[0m \033[7m\033[1;37m {opt_str} \033[0m")
                else:
                    lines.append(f"    \033[90m{opt_str}\033[0m")

            lines.append("")
            lines.append("\033[90m  [↑/↓: Navigasi  •  Enter: Pilih  •  ESC: Lewati]\033[0m")

            output_buf = []
            for idx_l, pl in enumerate(lines):
                if idx_l == 0:
                    output_buf.append(f"\r\033[2K{pl}")
                else:
                    output_buf.append(f"\r\n\033[2K{pl}")
            
            output_buf.append(f"\033[{len(lines) - 1}A\r")
            sys.stdout.write("".join(output_buf))
            sys.stdout.flush()
            last_rendered_lines = len(lines)

            k = read_key_raw(fd)

            if k in ('UP', 'SHIFT_TAB'):
                selected_idx = (selected_idx - 1) % len(all_options)
            elif k in ('DOWN', 'TAB'):
                selected_idx = (selected_idx + 1) % len(all_options)
            elif k == 'ESC':
                if last_rendered_lines > 0:
                    buf = []
                    for _ in range(last_rendered_lines):
                        buf.append("\033[B\033[2K")
                    buf.append("\033[J")
                    buf.append(f"\033[{last_rendered_lines}A\r")
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()
                return "Dilewati oleh pengguna."
            elif k == 'ENTER':
                chosen = all_options[selected_idx]
                if last_rendered_lines > 0:
                    buf = []
                    for _ in range(last_rendered_lines):
                        buf.append("\033[B\033[2K")
                    buf.append("\033[J")
                    buf.append(f"\033[{last_rendered_lines}A\r")
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()

                if allow_custom and selected_idx == len(all_options) - 1:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    sys.stdout.write("\033[?25h\033[?7h")
                    sys.stdout.flush()
                    from rich.prompt import Prompt
                    custom_val = Prompt.ask("\n[bold cyan]Ketik jawaban kustom Anda[/bold cyan]").strip()
                    console.print(f"[bold green]✔ Jawaban:[/bold green] [bold white]{custom_val}[/bold white]\n")
                    return custom_val if custom_val else chosen

                console.print(f"[bold green]✔ Opsi dipilih:[/bold green] [bold white]{chosen}[/bold white]\n")
                return chosen

    finally:
        sys.stdout.write("\033[?7h\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def get_bash_action_label(cmd):
    cmd_s = cmd.strip()
    c_lower = cmd_s.lower()
    
    if c_lower.startswith("git diff"):
        return "Reviewing changes"
    elif c_lower.startswith("git apply") or "patch" in c_lower:
        return "Applying patch"
    elif c_lower.startswith("git "):
        return f"Running git {cmd_s[4:].strip()}"
    elif any(c_lower.startswith(x) for x in ["npm test", "pytest", "cargo test", "go test", "python -m unittest", "ctest", "make test"]):
        return f"Testing {cmd_s}"
    elif any(c_lower.startswith(x) for x in ["npm run build", "npm run compile", "cargo build", "make", "gradle", "mvn", "cmake", "gcc", "g++", "clang"]):
        return f"Building {cmd_s}"
    elif any(c_lower.startswith(x) for x in ["pkg install", "pkg in ", "apt install", "pip install", "npm i ", "npm install", "yarn add", "cargo install", "gem install"]):
        return f"Installing {cmd_s}"
    elif any(c_lower.startswith(x) for x in ["grep ", "rg ", "ag ", "ack "]):
        return f"Searching {cmd_s}"
    elif any(c_lower.startswith(x) for x in ["find ", "fd ", "glob "]):
        return "Finding files"
    elif any(c_lower.startswith(x) for x in ["ls ", "ls", "dir", "tree"]):
        return f"Listing {cmd_s}"
    elif any(c_lower.startswith(x) for x in ["curl ", "wget ", "http "]):
        return f"Fetching {cmd_s}"
    else:
        return f"Running {cmd_s}"

def execute_tool(name, args, auto_approve=False):
    try:
        if name == "execute_bash":
            cmd = args.get("command", "")
            action_label = get_bash_action_label(cmd)
            console.print(f"\n[bold yellow]⚡ RTS >[/bold yellow] [bold white]{action_label}[/bold white]")
            
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
                    console.print("[bold green]✔ RTS > Always Allow enabled.[/bold green]")

            import time
            from queue_manager import AsyncInputQueueWatcher
            watcher = AsyncInputQueueWatcher()
            watcher.start()

            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = "", ""
            start_time = time.time()
            cancelled = False
            
            try:
                with console.status(f"[bold cyan]RTS > {action_label}...[/bold cyan] [dim](ESC: Stop | Ketik 'gas' untuk teruskan)[/dim]") as status:
                    while proc.poll() is None:
                        if watcher.stop_requested.is_set():
                            proc.kill()
                            cancelled = True
                            break
                        elapsed = time.time() - start_time
                        status.update(f"[bold cyan]RTS > {action_label}...[/bold cyan] [dim]({elapsed:.1f}s | ESC: Stop | Ketik 'gas')[/dim]")
                        time.sleep(0.1)

                if cancelled:
                    console.print("\n[bold yellow]⏹ RTS > Cancelled by user (ESC).[/bold yellow]")
                    return "Eksekusi command dibatalkan oleh pengguna (ESC)."

                stdout, stderr = proc.communicate()
            finally:
                watcher.stop()

            elapsed = time.time() - start_time
            if stdout.strip():
                for line in stdout.strip().splitlines()[:25]:
                    console.print(f"  [dim]{line}[/dim]")
                if len(stdout.strip().splitlines()) > 25:
                    console.print(f"  [dim]...({len(stdout.strip().splitlines()) - 25} baris lainnya)[/dim]")
            if stderr.strip():
                for line in stderr.strip().splitlines()[:15]:
                    console.print(f"  [dim red]{line}[/dim red]")

            if proc.returncode == 0:
                console.print(f"[bold green]✔ RTS > Completed[/bold green] [dim]({elapsed:.1f}s)[/dim]\n")
            else:
                console.print(f"[bold red]✘ RTS > Failed (Exit code: {proc.returncode})[/bold red] [dim]({elapsed:.1f}s)[/dim]\n")

            out = (stdout + "\n" + stderr).strip()
            return f"Returncode: {proc.returncode}\nOutput:\n{out}" if out else f"Returncode: {proc.returncode}\n(No output)"

        elif name == "read_file":
            fp = args.get("filepath")
            if not os.path.exists(fp):
                console.print(f"[bold red]✘ RTS > Failed: File '{fp}' not found[/bold red]")
                return f"Error: File '{fp}' tidak ditemukan."
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            line_count = len(content.splitlines())
            console.print(f"[dim cyan]RTS > Reading {fp}[/dim cyan] [dim]({line_count} baris)[/dim]")
            return content

        elif name == "write_file":
            fp = args.get("filepath")
            content = args.get("content", "")
            os.makedirs(os.path.dirname(os.path.abspath(fp)), exist_ok=True)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)
            line_count = len(content.splitlines())
            console.print(f"[bold green]RTS > Writing {fp}[/bold green] [dim]({line_count} baris, {len(content)} bytes)[/dim]")
            return f"Sukses menulis {fp} ({line_count} baris)"

        elif name == "edit_file":
            fp = args.get("filepath")
            old_c = args.get("old_content")
            new_c = args.get("new_content")
            if not os.path.exists(fp):
                console.print(f"[bold red]✘ RTS > Failed: File '{fp}' not found[/bold red]")
                return f"Error: File '{fp}' tidak ditemukan."
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                data = f.read()
            if old_c not in data:
                console.print(f"[bold red]✘ RTS > Failed: old_content mismatch in {fp}[/bold red]")
                return "Error: old_content tidak cocok dengan isi file."
            data = data.replace(old_c, new_c, 1)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(data)
            console.print(f"[bold green]RTS > Editing {fp}[/bold green]")
            return f"Sukses mengupdate {fp}"

        elif name in ("delete_file", "remove_file"):
            fp = args.get("filepath")
            if os.path.exists(fp):
                if os.path.isdir(fp):
                    import shutil
                    shutil.rmtree(fp)
                else:
                    os.remove(fp)
                console.print(f"[bold red]RTS > Removing {fp}[/bold red]")
                return f"Sukses menghapus {fp}"
            else:
                console.print(f"[bold red]✘ RTS > Failed: File '{fp}' not found[/bold red]")
                return f"Error: File '{fp}' tidak ditemukan."

        elif name == "list_dir":
            d = args.get("directory", ".")
            console.print(f"[dim cyan]RTS > Listing {d}[/dim cyan]")
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
            with console.status(f"[bold cyan]RTS > Searching {q}...[/bold cyan]"):
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            console.print(f"[dim cyan]RTS > Searching {q}[/dim cyan]")
            return res.stdout if res.stdout else "Tidak ditemukan."

        elif name == "fetch_url":
            url = args.get("url")
            import requests
            console.print(f"[dim cyan]RTS > Fetching {url}[/dim cyan]")
            try:
                r = requests.get(url, timeout=15)
                return r.text[:4000]
            except Exception as e:
                console.print(f"[bold red]✘ RTS > Failed: {e}[/bold red]")
                return f"Error fetching {url}: {e}"

        elif name == "remember":
            scope = args.get("scope", "global")
            key, val = args.get("key"), args.get("value")
            if scope == "global":
                save_global_memory(key, val)
            else:
                save_project_memory(key, val)
            console.print(f"[magenta]RTS > Remembering {key} = {val}[/magenta]")
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
                    console.print(f"[bold cyan]RTS > Loading skill {s_name}[/bold cyan]")
                    return f"=== PANDUAN SPESIALISASI SKILL '{s_name}' ===\n{content}"
            console.print(f"[bold red]✘ RTS > Failed: Skill '{s_name}' not found[/bold red]")
            return f"Skill '{s_name}' tidak ditemukan di folder skills rts."

        elif name == "ask_user":
            q = args.get("question", "Pilih salah satu opsi:")
            opts = args.get("options", ["Ya", "Tidak"])
            allow_c = args.get("allow_custom", True)
            return interactive_ask_user(q, opts, allow_custom=allow_c)

    except Exception as e:
        return f"Error tool '{name}': {str(e)}"

    return "Tool tidak dikenal."
