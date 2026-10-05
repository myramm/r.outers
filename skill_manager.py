import os
import sys
import shutil
import subprocess
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from ui import console

SKILLS_DEST_DIRS = [
    os.path.join(os.path.dirname(__file__), "skills"),
    os.path.expanduser("~/.agents/skills")
]

def get_installed_skills_info():
    skills_map = {}
    for sdir in SKILLS_DEST_DIRS:
        if os.path.exists(sdir):
            for item in sorted(os.listdir(sdir)):
                item_path = os.path.join(sdir, item)
                skill_md = os.path.join(item_path, "SKILL.md")
                if os.path.isdir(item_path) and os.path.exists(skill_md):
                    if item not in skills_map:
                        desc = ""
                        try:
                            with open(skill_md, "r", encoding="utf-8", errors="ignore") as f:
                                for line in f:
                                    if line.lower().startswith("description:"):
                                        desc = line.split(":", 1)[1].strip()
                                        break
                        except Exception:
                            pass
                        skills_map[item] = {
                            "name": item,
                            "path": item_path,
                            "desc": desc or "Panduan spesialisasi teknis"
                        }
    return skills_map

def install_skill_from_url(repo_input):
    repo_input = repo_input.strip()
    if not repo_input:
        console.print("[yellow]URL atau nama repository tidak boleh kosong.[/yellow]")
        return False

    # Format URL jika user memasukkan "owner/repo"
    if not repo_input.startswith("http://") and not repo_input.startswith("https://") and not repo_input.startswith("git@"):
        if "/" in repo_input:
            url = f"https://github.com/{repo_input}.git"
        else:
            url = f"https://github.com/{repo_input}"
    else:
        url = repo_input

    temp_dir = "/tmp/_skill_clone_tmp"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)

    console.print(f"\n[bold cyan]⏳ Mengunduh skill dari:[/bold cyan] [yellow]{url}[/yellow]...")
    
    with console.status("[bold cyan]Cloning repository...[/bold cyan]"):
        res = subprocess.run(f"git clone --depth 1 {url} {temp_dir}", shell=True, capture_output=True, text=True)

    if res.returncode != 0:
        console.print(f"[bold red]❌ Gagal mengunduh repository![/bold red]\n[dim]{res.stderr.strip()}[/dim]")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    installed_count = 0
    installed_names = []

    # Pastikan direktori tujuan tersedia
    for dest in SKILLS_DEST_DIRS:
        os.makedirs(dest, exist_ok=True)

    # 1. Cek jika repository memiliki folder `skills/`
    skills_subdir = os.path.join(temp_dir, "skills")
    if os.path.exists(skills_subdir) and os.path.isdir(skills_subdir):
        for sub in os.listdir(skills_subdir):
            sub_path = os.path.join(skills_subdir, sub)
            if os.path.isdir(sub_path):
                for dest in SKILLS_DEST_DIRS:
                    target = os.path.join(dest, sub)
                    if os.path.exists(target):
                        shutil.rmtree(target, ignore_errors=True)
                    shutil.copytree(sub_path, target)
                installed_count += 1
                installed_names.append(sub)

    # 2. Cek jika root repo memiliki SKILL.md
    elif os.path.exists(os.path.join(temp_dir, "SKILL.md")):
        repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
        for dest in SKILLS_DEST_DIRS:
            target = os.path.join(dest, repo_name)
            if os.path.exists(target):
                shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(temp_dir, target, ignore=shutil.ignore_patterns(".git"))
        installed_count += 1
        installed_names.append(repo_name)

    # 3. Cek jika root repo memiliki antislop.md atau README.md yang bisa dijadikan skill
    else:
        repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
        for dest in SKILLS_DEST_DIRS:
            target = os.path.join(dest, repo_name)
            os.makedirs(target, exist_ok=True)
            skill_target = os.path.join(target, "SKILL.md")
            
            src_md = None
            for cand in ["antislop.md", "README.md", "guide.md", "GUIDE.md"]:
                cand_path = os.path.join(temp_dir, cand)
                if os.path.exists(cand_path):
                    src_md = cand_path
                    break
            
            if src_md:
                shutil.copy(src_md, skill_target)
            else:
                with open(skill_target, "w", encoding="utf-8") as f:
                    f.write(f"---\nname: {repo_name}\ndescription: Skill imported from {url}\n---\n\n# {repo_name}\n")
        installed_count += 1
        installed_names.append(repo_name)

    # Bersihkan folder sementara
    shutil.rmtree(temp_dir, ignore_errors=True)

    if installed_count > 0:
        console.print(f"\n[bold green]✔ Berhasil memasang {installed_count} skill baru:[/bold green]")
        for n in installed_names:
            console.print(f"  • [bold yellow]{n}[/bold yellow]")
        console.print("[dim]Skill siap digunakan secara otomatis oleh r.outers.[/dim]\n")
        return True
    else:
        console.print("[yellow]Tidak ditemukan file skill yang valid di repository tersebut.[/yellow]")
        return False

def create_manual_skill():
    console.print(Panel("""[bold cyan]Buat Skill Kustom Baru[/bold cyan]
Skill adalah panduan aturan/spesialisasi yang akan dibaca oleh AI saat bekerja.""", title="🛠 Tambah Skill Manual"))
    
    name = Prompt.ask("[bold yellow]Nama Skill (contoh: laravel-pro, react-tailwind, security-audit)[/bold yellow]").strip().lower()
    if not name:
        console.print("[yellow]Batal membuat skill.[/yellow]")
        return False
    name = name.replace(" ", "-")

    desc = Prompt.ask("[bold cyan]Deskripsi singkat skill[/bold cyan]", default="Panduan spesialisasi kustom").strip()
    
    console.print("\n[dim]Tuliskan poin aturan atau instruksi utama (tekan Enter 2x jika sudah selesai):[/dim]")
    lines = []
    while True:
        try:
            line = input()
            if not line and lines and not lines[-1]:
                break
            lines.append(line)
        except EOFError:
            break

    body = "\n".join(lines).strip()
    if not body:
        body = f"# Panduan {name}\n\n1. Tulis kode bersih dan terstruktur.\n2. Lakukan pengujian sebelum selesai."

    content = f"""---
name: {name}
description: {desc}
---

# {name.replace('-', ' ').title()}

{body}
"""

    for dest in SKILLS_DEST_DIRS:
        target_dir = os.path.join(dest, name)
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(content)

    console.print(f"\n[bold green]✔ Skill '{name}' berhasil dibuat dan disimpan![/bold green]\n")
    return True

def delete_installed_skill():
    skills = get_installed_skills_info()
    if not skills:
        console.print("[yellow]Tidak ada skill yang terpasang.[/yellow]")
        return False

    s_list = sorted(list(skills.keys()))
    console.print("\n[bold red]Pilih skill yang ingin dihapus:[/bold red]")
    for idx, s in enumerate(s_list, 1):
        console.print(f"  [bold yellow]{idx}[/bold yellow]. {s}")

    choice = Prompt.ask("\nNomor skill (atau 'e' untuk batal)", default="e").strip()
    if choice.lower() == "e":
        console.print("[yellow]Batal menghapus skill.[/yellow]")
        return False

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(s_list):
            target_name = s_list[idx]
            if Confirm.ask(f"[bold red]Yakin ingin menghapus skill '{target_name}'?[/bold red]"):
                for dest in SKILLS_DEST_DIRS:
                    t = os.path.join(dest, target_name)
                    if os.path.exists(t):
                        shutil.rmtree(t, ignore_errors=True)
                console.print(f"[bold green]✔ Skill '{target_name}' berhasil dihapus![/bold green]\n")
                return True
        else:
            console.print("[red]Nomor tidak valid.[/red]")
    except ValueError:
        console.print("[red]Input tidak valid.[/red]")
    return False

def show_skills_interactive_menu():
    while True:
        skills = get_installed_skills_info()
        console.print(Panel(f"""[bold cyan]Pusat Manajemen Skill r.outers[/bold cyan] ({len(skills)} Skill Terpasang)

[bold yellow]1[/bold yellow]. 📋 Lihat Daftar Lengkap Skill
[bold yellow]2[/bold yellow]. 📥 Pasang Skill dari URL GitHub (contoh: https://github.com/owner/repo)
[bold yellow]3[/bold yellow]. ✍️  Buat Skill Kustom Baru Secara Manual
[bold yellow]4[/bold yellow]. 🗑️  Hapus Skill
[bold red]e / 0[/bold red]. ⬅️ Kembali ke Menu Utama
""", title="⚡ Kelola & Tambah Skill"))

        choice = Prompt.ask("Pilih aksi (1-4, e)", default="1").strip().lower()

        if choice in ("e", "0", "exit", "batal"):
            break
        elif choice == "1":
            from main import show_skills_table
            show_skills_table()
            Prompt.ask("\n[dim]Tekan Enter untuk kembali[/dim]", default="")
        elif choice == "2":
            url_in = Prompt.ask("\n[bold cyan]Masukkan URL GitHub / repo (contoh: https://github.com/obra/superpowers)[/bold cyan]").strip()
            if url_in:
                install_skill_from_url(url_in)
        elif choice == "3":
            create_manual_skill()
        elif choice == "4":
            delete_installed_skill()
