#!/usr/bin/env python3
import os
import sys
import json
from rich.prompt import Prompt
from rich.panel import Panel

from ui import console, show_banner, print_markdown
from config import load_config, setup_config
from memory import load_memory
from tools import execute_tool
from client import build_system_prompt, call_ai

def main():
    show_banner()
    config = load_config()
    auto_approve = False

    messages = [{"role": "system", "content": build_system_prompt()}]

    while True:
        try:
            status_tag = "[bold magenta](YOLO)[/bold magenta] " if auto_approve else ""
            user_input = Prompt.ask(f"\n{status_tag}[bold cyan]r.outers >[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Keluar...[/yellow]")
            break

        if not user_input.strip():
            continue

        if user_input.startswith("/"):
            cmd = user_input.strip().lower()
            if cmd in ["/exit", "/quit"]:
                break
            elif cmd == "/clear":
                messages = [{"role": "system", "content": build_system_prompt()}]
                os.system("clear")
                show_banner()
                console.print("[green]Chat history dibersihkan & context direfresh.[/green]")
                continue
            elif cmd == "/yolo":
                auto_approve = not auto_approve
                console.print(f"[bold magenta]YOLO Mode (Auto-Approve): {auto_approve}[/bold magenta]")
                continue
            elif cmd == "/memory":
                console.print(Panel(json.dumps(load_memory(), indent=2), title="🧠 r.outers Memory"))
                continue
            elif cmd == "/config":
                config = setup_config()
                continue
            elif cmd == "/help":
                console.print(Panel("""[bold]Perintah Tersedia:[/bold]
• [bold cyan]/yolo[/bold cyan]    : Mode Auto-Pilot (tanpa konfirmasi manual y/n)
• [bold cyan]/memory[/bold cyan]  : Lihat memori yang tersimpan
• [bold cyan]/clear[/bold cyan]   : Bersihkan sesi chat
• [bold cyan]/config[/bold cyan]  : Atur ulang API Key / Model
• [bold cyan]/exit[/bold cyan]    : Keluar
""", title="Bantuan r.outers"))
                continue

        messages.append({"role": "user", "content": user_input})

        while True:
            with console.status("[bold cyan]r.outers sedang memproses...[/bold cyan]"):
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
