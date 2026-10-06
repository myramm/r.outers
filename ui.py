import random
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

console = Console()

RTS_TIPS = [
    "Ketik /model untuk ganti model AI kapan saja",
    "Gunakan /thinking untuk mengatur level penalaran (off, low, med, high, max)",
    "Ketik /setup untuk mengelola API Key, provider, dan izin otomatis",
    "Gunakan /skills untuk melihat daftar skill dan kemampuan RTS",
    "Jalankan /status untuk melihat status model, thinking, dan agent aktif",
    "Ketik /theme untuk memilih tema warna tampilan terminal",
    "Gunakan /clear untuk membersihkan riwayat percakapan",
    "Tekan Tab saat mengetik / untuk autocomplete perintah",
    "Gunakan /add-skill <url> untuk memasang skill langsung dari GitHub",
    "Gunakan /memory untuk melihat memori jangka panjang yang tersimpan",
    "Tekan ESC untuk menghentikan proses generasi AI seketika",
    "Ketik /stop untuk membatalkan eksekusi task yang sedang berjalan",
    "RTS otomatis menjalankan tool coding dan pengeditan file saat diminta"
]

def show_banner():
    art_text = """  ____  _____ ____ 
 |  _ \|_   _/ ___|
 | |_) | | | \___ \\
 |  _ <  | |  ___) |
 |_| \_\ |_| |____/ """

    t = Text(art_text, style="bold cyan")
    console.print(t)
    console.print("\n  [bold white]RTS • AI CODING CLI[/bold white]\n  [bold green]TERMUX[/bold green]  [dim]v1.0.0[/dim]")
    console.print("  [dim]Ketik [bold cyan]/[/bold cyan] untuk menu perintah • [bold cyan]/setup[/bold cyan] pengaturan • [bold green]/model[/bold green] ganti model[/dim]\n")

def print_markdown(content):
    console.print("")
    console.print(Markdown(content))

def show_subtle_tip():
    tip = random.choice(RTS_TIPS)
    console.print(f"\n[dim italic]Tips: {tip}[/dim italic]")


