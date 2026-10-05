from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def show_banner():
    console.print(Panel.fit(
        "[bold cyan]⚡ r.outers AI AGENT (TERMUX) ⚡[/bold cyan]\n"
        "[dim]Full Autonomous Coding • NPM / PKG / PIP • Memory • Auto-Fix[/dim]\n"
        "Perintah: [bold green]/help[/bold green] [dim]|[/dim] [bold yellow]/yolo[/bold yellow] [dim]|[/dim] [bold cyan]/memory[/bold cyan] [dim]|[/dim] [bold red]/exit[/bold red]",
        border_style="cyan"
    ))

def print_markdown(content):
    console.print("\n[bold green]r.outers:[/bold green]")
    console.print(Markdown(content))
