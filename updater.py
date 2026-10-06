import os
import sys
import subprocess
import shutil
from ui import console
from rich.panel import Panel
from rich.table import Table

def get_repo_dir():
    """
    Locates the r.outers repository directory.
    """
    candidates = [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.expanduser("~/r_outers"),
        os.path.expanduser("~/r.outers"),
        os.getcwd()
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, ".git")):
            return c
    return os.path.dirname(os.path.abspath(__file__))

def get_current_commit_hash(repo_dir):
    try:
        res = subprocess.run(
            ["git", "-C", repo_dir, "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True
        )
        return res.stdout.strip()
    except Exception:
        return "unknown"

def get_version_info():
    repo_dir = get_repo_dir()
    commit = get_current_commit_hash(repo_dir)
    try:
        branch = subprocess.run(
            ["git", "-C", repo_dir, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True
        ).stdout.strip()
    except Exception:
        branch = "main"

    try:
        last_log = subprocess.run(
            ["git", "-C", repo_dir, "log", "-1", "--pretty=format:%s (%cr)"],
            capture_output=True, text=True
        ).stdout.strip()
    except Exception:
        last_log = ""

    return Panel(f"""[bold cyan]RTS (r.outers AI Agent)[/bold cyan]
• [bold]Commit Hash[/bold] : [bold yellow]{commit}[/bold yellow] ({branch})
• [bold]Lokasi Repo[/bold] : [dim]{repo_dir}[/dim]
• [bold]Update Terakhir[/bold]: [dim]{last_log}[/dim]
""", title="⚡ Versi RTS")

def run_update(interactive_mode=False):
    """
    Checks for updates from GitHub remote origin and pulls the latest changes.
    """
    repo_dir = get_repo_dir()

    if not shutil.which("git"):
        console.print("[bold red]❌ Perintah 'git' tidak ditemukan di sistem.[/bold red]")
        console.print("[yellow]Silakan install git terlebih dahulu: [cyan]pkg install git[/cyan] atau [cyan]apt install git[/cyan][/yellow]\n")
        return False

    if not os.path.exists(os.path.join(repo_dir, ".git")):
        console.print(f"[bold red]❌ Direktori '{repo_dir}' bukan merupakan repositori git yang valid.[/bold red]\n")
        return False

    console.print(f"\n[bold cyan]🚀 Memeriksa Pembaruan RTS dari GitHub...[/bold cyan]")
    console.print(f"[dim]Lokasi direktori: {repo_dir}[/dim]\n")

    old_commit = get_current_commit_hash(repo_dir)

    # 1. Git fetch
    with console.status("[bold cyan]⏳ Menghubungi remote origin...[/bold cyan]"):
        try:
            fetch_res = subprocess.run(
                ["git", "-C", repo_dir, "fetch", "origin", "main"],
                capture_output=True, text=True, timeout=20
            )
        except subprocess.TimeoutExpired:
            console.print("[bold red]❌ Gagal menghubungi GitHub (Koneksi Timeout). Periksa koneksi internet Anda.[/bold red]\n")
            return False
        except Exception as e:
            console.print(f"[bold red]❌ Gagal fetch: {e}[/bold red]\n")
            return False

    # 2. Check difference
    try:
        diff_res = subprocess.run(
            ["git", "-C", repo_dir, "rev-list", "HEAD..origin/main", "--count"],
            capture_output=True, text=True
        )
        behind_count = int(diff_res.stdout.strip()) if diff_res.stdout.strip().isdigit() else 0
    except Exception:
        behind_count = 0

    if behind_count == 0:
        console.print(Panel(f"""[bold green]✔ RTS SUDAH DALAM VERSI TERBARU![/bold green]

• [bold]Commit Aktif[/bold] : [bold yellow]{old_commit}[/bold yellow]
• [bold]Status[/bold]       : Sinkron dengan [cyan]origin/main[/cyan]
• [dim]Tidak ada pembaruan baru yang tertunda di GitHub.[/dim]
""", title="⚡ RTS Update Status", border_style="green"))
        return True

    console.print(f"[bold yellow]📦 Terdeteksi {behind_count} commit pembaruan baru di GitHub! Mengunduh...[/bold yellow]\n")

    # 3. Pull latest changes
    with console.status("[bold cyan]⏳ Menjalankan git pull origin main...[/bold cyan]"):
        pull_res = subprocess.run(
            ["git", "-C", repo_dir, "pull", "origin", "main"],
            capture_output=True, text=True, timeout=30
        )

    if pull_res.returncode != 0:
        console.print(f"[bold red]❌ Gagal memperbarui RTS:[/bold red]\n{pull_res.stderr or pull_res.stdout}\n")
        console.print("[yellow]💡 Saran:[/yellow] Jika Anda memiliki modifikasi file lokal, jalankan:")
        console.print(f"   [cyan]git -C {repo_dir} stash[/cyan]")
        console.print(f"   [cyan]git -C {repo_dir} pull origin main[/cyan]\n")
        return False

    new_commit = get_current_commit_hash(repo_dir)

    # 4. Clean cache
    try:
        pycache_dir = os.path.join(repo_dir, "__pycache__")
        if os.path.exists(pycache_dir):
            shutil.rmtree(pycache_dir, ignore_errors=True)
    except Exception:
        pass

    # 5. Fetch change log summary
    try:
        log_res = subprocess.run(
            ["git", "-C", repo_dir, "log", f"{old_commit}..{new_commit}", "--oneline"],
            capture_output=True, text=True
        )
        changelog_lines = log_res.stdout.strip().splitlines()
        changelog_str = "\n".join([f"  • [yellow]{line.split()[0]}[/yellow] {' '.join(line.split()[1:])}" for line in changelog_lines[:8]])
        if len(changelog_lines) > 8:
            changelog_str += f"\n  • [dim]... dan {len(changelog_lines) - 8} commit lainnya[/dim]"
    except Exception:
        changelog_str = f"  • Dari [dim]{old_commit}[/dim] ke [bold yellow]{new_commit}[/bold yellow]"

    panel_body = f"""[bold green]✔ RTS BERHASIL DIPERBARUI KE VERSI TERBARU![/bold green]

• [bold]Versi Sebelumnya[/bold] : [dim]{old_commit}[/dim]
• [bold]Versi Sekarang[/bold]   : [bold yellow]{new_commit}[/bold yellow]

[bold cyan]Daftar Pembaruan Terbaru:[/bold cyan]
{changelog_str}
"""
    if interactive_mode:
        panel_body += "\n[bold magenta]💡 Info:[/bold magenta] [dim]Silakan ketik [bold cyan]/clear[/bold cyan] atau restart sesi ([bold cyan]/exit[/bold cyan]) untuk memuat perubahan terbaru secara penuh.[/dim]"
    else:
        panel_body += "\n[bold green]✔ Update selesai! Ketik [bold cyan]rts[/bold cyan] untuk mulai menggunakan versi terbaru.[/bold green]"

    console.print(Panel(panel_body, title="🚀 RTS Updater", border_style="bold cyan"))
    return True
