#!/usr/bin/env python3
import os
import sys
import json
from rich.prompt import Prompt
from rich.panel import Panel

from ui import console, show_banner, print_markdown
from config import load_config, setup_config, CONFIG_FILE
from memory import load_memory
from tools import execute_tool
from client import build_system_prompt, call_ai

POPULAR_MODELS = [
    "deepseek/deepseek-chat",
    "deepseek/deepseek-r1",
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "meta-llama/llama-3.3-70b-instruct",
    "google/gemini-2.0-flash-exp:free"
]

def handle_model_command(config, user_input):
    parts = user_input.strip().split(maxsplit=1)
    if len(parts) > 1 and parts[1].strip():
        new_model = parts[1].strip()
    else:
        console.print(Panel(
            "[bold cyan]Model Populer Rekomendasi (OpenRouter):[/bold cyan]\n" +
            "\n".join([f" • [yellow]{m}[/yellow]" for m in POPULAR_MODELS]) +
            f"\n\n[bold]Model saat ini:[/bold] [green]{config.get('model', 'Unknown')}[/green]",
            title="Ganti Model AI"
        ))
        new_model = Prompt.ask("Masukkan nama model baru", default=config.get("model", "deepseek/deepseek-chat"))
    
    config["model"] = new_model
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        console.print(f"[bold green]✔ Model aktif berhasil diubah ke:[/bold green] [bold yellow]{new_model}[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Gagal menyimpan konfigurasi model:[/bold red] {str(e)}")
    return config

def main():
    show_banner()
    config = load_config()
    auto_approve = False

    messages = [{"role": "system", "content": build_system_prompt()}]

    while True:
        try:
            status_tag = "[bold magenta](YOLO)[/bold magenta] " if auto_approve else ""
            model_tag = f"[dim]({config.get('model', 'ai')})[/dim] "
            user_input = Prompt.ask(f"\n{status_tag}{model_tag}[bold cyan]r.outers >[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Keluar...[/yellow]")
            break

        if not user_input.strip():
            continue

        # Slash Commands
        if user_input.startswith("/"):
            cmd_lower = user_input.strip().lower()
            if cmd_lower in ["/exit", "/quit"]:
                break
            elif cmd_lower == "/clear":
                messages = [{"role": "system", "content": build_system_prompt()}]
                os.system("clear")
                show_banner()
                console.print("[green]Chat history dibersihkan & context direfresh.[/green]")
                continue
            elif cmd_lower == "/yolo":
                auto_approve = not auto_approve
                console.print(f"[bold magenta]YOLO Mode (Auto-Approve): {auto_approve}[/bold magenta]")
                continue
            elif cmd_lower.startswith("/model"):
                config = handle_model_command(config, user_input)
                continue
            elif cmd_lower == "/memory":
                console.print(Panel(json.dumps(load_memory(), indent=2), title="🧠 r.outers Memory"))
                continue
            elif cmd_lower == "/config":
                config = setup_config()
                continue
            elif cmd_lower == "/help":
                console.print(Panel("""[bold]Perintah Tersedia:[/bold]
• [bold cyan]/model [nama_model][/bold cyan] : Ganti model AI kapan saja (e.g. /model gpt-4o)
• [bold cyan]/yolo[/bold cyan]                : Toggle Mode Auto-Pilot (tanpa konfirmasi manual y/n)
• [bold cyan]/memory[/bold cyan]              : Lihat memori yang tersimpan
• [bold cyan]/clear[/bold cyan]               : Bersihkan riwayat chat sesi ini
• [bold cyan]/config[/bold cyan]              : Atur ulang API Key / Provider
• [bold cyan]/exit[/bold cyan]                : Keluar dari aplikasi
""", title="Bantuan r.outers"))
                continue

        messages.append({"role": "user", "content": user_input})

        while True:
            with console.status(f"[bold cyan]r.outers ({config.get('model')}) sedang memproses...[/bold cyan]"):
                reply = call_ai(messages, config)

            if not reply:
                break

            msg = reply["choices"][0]["message"]
            messages.append(msg)

            if msg.get("tool_calls"):
                for tool in msg["tool_calls"]:
                    fn_name = tool["function"]["name"]
                    try:
                        fn_args = json.loads(tool["function"].get("arguments", "{}"))
                    except Exception:
                        fn_args = {}

                    tool_res = execute_tool(fn_name, fn_args, auto_approve=auto_approve)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool["id"],
                        "name": fn_name,
                        "content": str(tool_res)
                    })
                continue
            else:
                content = msg.get("content", "")
                if content:
                    print_markdown(content)
                break

if __name__ == "__main__":
    main()
