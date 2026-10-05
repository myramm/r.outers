from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

console = Console()

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
    console.print("\n[bold green]r.outers:[/bold green]")
    console.print(Markdown(content))
