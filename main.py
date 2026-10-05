#!/usr/bin/env python3
import os
import sys
import json
from rich.prompt import Prompt
from rich.panel import Panel

from ui import console, show_banner, print_markdown
from config import get_active_config, update_active_model, switch_provider, add_new_provider
from memory import load_memory
from tools import execute_tool
from client import build_system_prompt, call_ai

POPULAR_MODELS = {
    "clouvia": [
        "free-model",
        "coding-high"
    ],
    "openrouter": [
        "deepseek/deepseek-chat",
        "deepseek/deepseek-r1",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "meta-llama/llama-3.3-70b-instruct",
        "google/gemini-2.0-flash-exp:free"
    ],
    "groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "deepseek-r1-distill-llama-70b"
    ],
    "deepseek": [
        "deepseek-chat",
        "deepseek-reasoner"
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "o1-preview",
        "o3-mini"
    ]
}

def handle_model_menu(config):
    prov_id = config.get("provider_id", "clouvia")
    rec_models = POPULAR_MODELS.get(prov_id, [
        "free-model",
        "coding-high",
        "deepseek/deepseek-chat",
        "openai/gpt-4o"
    ])

    lines = [f"[bold cyan]Provider Aktif:[/bold cyan] [bold green]{config.get('provider_name')}[/bold green]"]
    lines.append(f"[bold]Model Saat Ini:[/bold] [bold yellow]{config.get('model')}[/bold yellow]\n")
    lines.append("[bold]Pilihan Model Cepat:[/bold]")
    for idx, m in enumerate(rec_models, 1):
        lines.append(f"  [bold yellow]{idx}[/bold yellow]. {m}")
    lines.append("  [bold cyan]c[/bold cyan]. Ketik nama model custom manual")
    lines.append("  [bold magenta]p[/bold magenta]. Ganti / Tambah Provider")

    console.print(Panel("\n".join(lines), title="🤖 Pengaturan Model & Provider"))

    choice = Prompt.ask("\nPilih opsi", default="1")
    if choice.lower() == "p":
        return switch_provider()
    elif choice.lower() == "c":
        new_m = Prompt.ask("Masukkan nama model custom")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(rec_models):
                new_m = rec_models[idx]
            else:
                new_m = choice
        except ValueError:
            new_m = choice

    if new_m.strip():
        update_active_model(new_m.strip())
        config["model"] = new_m.strip()
        console.print(f"[bold green]✔ Model aktif diubah ke:[/bold green] [bold yellow]{new_m.strip()}[/bold yellow]")
    return config

def main():
    show_banner()
    config = get_active_config()
    auto_approve = False

    messages = [{"role": "system", "content": build_system_prompt()}]

    while True:
        try:
            status_tag = "[bold magenta](YOLO)[/bold magenta] " if auto_approve else ""
            prov_name = config.get('provider_id', 'ai')
            curr_model = config.get('model', 'model')
            model_tag = f"[dim]({prov_name}:{curr_model})[/dim] "
            user_input = Prompt.ask(f"\n{status_tag}{model_tag}[bold cyan]r.outers >[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Keluar...[/yellow]")
            break

        if not user_input.strip():
            continue

        # Slash Commands
        if user_input.startswith("/"):
            parts = user_input.strip().split(maxsplit=1)
            cmd_lower = parts[0].lower()
            
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
            elif cmd_lower == "/model":
                if len(parts) > 1 and parts[1].strip():
                    new_m = parts[1].strip()
                    update_active_model(new_m)
                    config["model"] = new_m
                    console.print(f"[bold green]✔ Model diubah ke:[/bold green] [bold yellow]{new_m}[/bold yellow]")
                else:
                    config = handle_model_menu(config)
                continue
            elif cmd_lower in ["/provider", "/providers"]:
                config = switch_provider()
                continue
            elif cmd_lower == "/memory":
                console.print(Panel(json.dumps(load_memory(), indent=2), title="🧠 r.outers Memory"))
                continue
            elif cmd_lower == "/help":
                console.print(Panel("""[bold]Perintah Tersedia:[/bold]
• [bold cyan]/model[/bold cyan] [nama]       : Pilih / ganti model AI (atau /model coding-high)
• [bold cyan]/provider[/bold cyan]           : Ganti / Tambah Provider (Clouvia, OpenRouter, Groq, DeepSeek, dll)
• [bold cyan]/yolo[/bold cyan]               : Toggle Mode Auto-Pilot (tanpa konfirmasi manual y/n)
• [bold cyan]/memory[/bold cyan]             : Lihat memori yang tersimpan
• [bold cyan]/clear[/bold cyan]              : Bersihkan riwayat chat sesi ini
• [bold cyan]/exit[/bold cyan]               : Keluar dari aplikasi
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
