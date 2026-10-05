#!/usr/bin/env python3
import os
import sys
import json
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table

from ui import console, show_banner, print_markdown
from config import (
    get_active_config, update_active_model, switch_provider,
    add_new_provider, load_full_config, save_full_config, PRESET_PROVIDERS
)
from memory import load_memory
from tools import execute_tool
from client import build_system_prompt, call_ai
from selector import select_model_interactive
from settings import show_settings_hub
from slash_prompt import get_smart_input

PROVIDER_MODELS = {
    "clouvia": {
        "name": "Clouvia Router (https://router.clouvia.id/v1)",
        "models": [
            "free-model",
            "coding-high",
            "claude-opus-5",
            "claude-sonnet-5-thinking-agentic",
            "gpt-6.1-sol",
            "gpt-6-sol",
            "gemini-3.8-flash-high",
            "deepseek-v4-pro",
            "qwen-3.8-max-thinking-agentic",
            "kimi-k3",
            "glm5.3-thinking-agentic"
        ]
    },
    "atria": {
        "name": "Atria ASI (https://api.atria-asi.ai/v1)",
        "models": [
            "Atria-Dawn-Preview"
        ]
    },
    "nvidia": {
        "name": "NVIDIA NIM (https://integrate.api.nvidia.com/v1)",
        "models": [
            "nvidia/nemotron-3-super-120b-a12b",
            "openai/gpt-oss-20b",
            "nvidia/nemotron-3.5-lightning-30b-a3b",
            "nvidia/nemotron-3-ultra-550b-a55b",
            "google/diffusiongemma-26b-a4b-it",
            "meta/muse-glimmer-30b",
            "z-ai/glm-5.3",
            "deepseek-ai/deepseek-v4.1-flash"
        ]
    }
}

def show_all_providers_and_models(active_config):
    table = Table(title="📡 Daftar Lengkap Provider & Model AI", header_style="bold cyan")
    table.add_column("No", style="dim", width=4)
    table.add_column("Provider ID", style="bold yellow")
    table.add_column("Base URL", style="dim")
    table.add_column("Pilihan Model", style="green")
    table.add_column("Status", style="bold")

    active_id = active_config.get("provider_id")
    for idx, (p_id, info) in enumerate(PROVIDER_MODELS.items(), 1):
        status = "[bold green]● AKTIF[/bold green]" if p_id == active_id else "[dim]○ Standby[/dim]"
        url = info["name"].split("(")[-1].rstrip(")")
        models_str = "\n".join([f"• {m}" for m in info["models"]])
        table.add_row(str(idx), p_id, url, models_str, status)

    console.print(table)

def handle_model_menu(config):
    prov_id = config.get("provider_id", "clouvia")
    p_info = PROVIDER_MODELS.get(prov_id, {"name": prov_id, "models": ["free-model", "coding-high"]})
    rec_models = p_info["models"]

    lines = [f"[bold cyan]Provider Aktif:[/bold cyan] [bold green]{config.get('provider_name')}[/bold green] ([dim]{config.get('base_url')}[/dim])"]
    lines.append(f"[bold]Model Saat Ini:[/bold] [bold yellow]{config.get('model')}[/bold yellow]\n")
    lines.append("[bold]Pilihan Model Cepat:[/bold]")
    for idx, m in enumerate(rec_models, 1):
        lines.append(f"  [bold yellow]{idx}[/bold yellow]. {m}")
    lines.append("  [bold cyan]c[/bold cyan]. Ketik nama model custom manual")
    lines.append("  [bold magenta]p[/bold magenta]. Ganti / Tambah Provider")
    lines.append("  [bold blue]l[/bold blue]. Lihat tabel lengkap semua Provider & Model")
    lines.append("  [bold red]e / E[/bold red]. Batal / Kembali (Exit menu)")

    console.print(Panel("\n".join(lines), title="🤖 Pengaturan Model & Provider"))

    choice = Prompt.ask("\nPilih opsi (1-{}, c, p, l, e)".format(len(rec_models)), default="1").strip()
    
    # Check Exit / Cancel
    if choice.lower() == "e":
        console.print("[yellow]Batal mengubah model.[/yellow]")
        return config

    if choice.lower() == "p":
        return switch_provider()
    elif choice.lower() == "l":
        show_all_providers_and_models(config)
        return config
    elif choice.lower() == "c":
        new_m = Prompt.ask("Masukkan nama model custom (atau 'e' untuk batal)").strip()
        if new_m.lower() == "e" or not new_m:
            console.print("[yellow]Batal mengubah model.[/yellow]")
            return config
        update_active_model(new_m)
        config["model"] = new_m
        console.print(f"[bold green]✔ Model aktif diubah ke:[/bold green] [bold yellow]{new_m}[/bold yellow]")
        return config

    # Check numeric choice strictly
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(rec_models):
            new_m = rec_models[idx]
            update_active_model(new_m)
            config["model"] = new_m
            console.print(f"[bold green]✔ Model aktif diubah ke:[/bold green] [bold yellow]{new_m}[/bold yellow]")
            return config
        else:
            console.print(f"[bold red]❌ Input tidak valid! Pilihan nomor harus antara 1 sampai {len(rec_models)}.[/bold red]")
            return config
    except ValueError:
        console.print(f"[bold red]❌ Input '{choice}' tidak valid! Ketik angka 1-{len(rec_models)}, 'c', 'p', 'l', atau 'e'.[/bold red]")
        return config

def show_skills_table():
    from client import get_available_skills_list
    skills = get_available_skills_list()
    if not skills:
        console.print("[yellow]Belum ada skill yang terpasang di ~/.agents/skills.[/yellow]")
        return
    
    table = Table(title=f"⚡ Daftar Skill Spesialisasi ({len(skills)} Terpasang)", header_style="bold cyan")
    table.add_column("No", style="dim", width=4)
    table.add_column("Nama Skill", style="bold yellow")
    table.add_column("Kategori / Tipe", style="green")
    
    for idx, s in enumerate(skills, 1):
        if s.startswith("antislop"):
            cat = "Anti-Slop Standard"
        elif s in ["test-driven-development", "systematic-debugging", "brainstorming", "writing-plans", "executing-plans", "using-superpowers", "verification-before-completion", "using-git-worktrees", "subagent-driven-development", "receiving-code-review", "requesting-code-review", "diagnosing-superpowers", "finishing-a-development-branch", "dispatching-parallel-agents", "writing-skills"]:
            cat = "Superpowers Core"
        else:
            cat = "Specialist Skill"
        table.add_row(str(idx), s, cat)
    
    console.print(table)

def main():
    show_banner()
    full_cfg = load_full_config()
    config = get_active_config()
    auto_approve = (full_cfg.get("permission_mode") == "always_allow") or full_cfg.get("auto_approve", False)

    messages = [{"role": "system", "content": build_system_prompt()}]

    while True:
        try:
            full_cfg = load_full_config()
            auto_approve = (full_cfg.get("permission_mode") == "always_allow") or full_cfg.get("auto_approve", False)
            
            prov_name = config.get('provider_id', 'ai')
            curr_model = config.get('model', 'model')
            perm_label = "Auto-Approve" if auto_approve else "Ask Permission"
            
            sub_info = f"{prov_name}:{curr_model} • {perm_label}"
            prompt_str = "\033[1;36mr.outers >\033[0m"
            console.print("")
            user_input = get_smart_input(prompt_str, sub_info=sub_info)
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
            elif cmd_lower in ["/clear", "/cls"]:
                messages = [{"role": "system", "content": build_system_prompt()}]
                sys.stdout.write("\033[H\033[2J\033[3J")
                sys.stdout.flush()
                os.system("clear")
                show_banner()
                console.print("[bold green]✔ Riwayat percakapan & layar dibersihkan. Konteks AI telah direfresh.[/bold green]")
                continue
            elif cmd_lower in ["/model", "/m"]:
                if len(parts) > 1 and parts[1].strip():
                    new_m = parts[1].strip()
                    update_active_model(new_m)
                    config["model"] = new_m
                    console.print(f"[bold green]✔ Model diubah ke:[/bold green] [bold yellow]{new_m}[/bold yellow]")
                else:
                    config = select_model_interactive(config)
                continue
            elif cmd_lower in ["/provider", "/providers", "/p"]:
                config = switch_provider()
                continue
            elif cmd_lower in ["/list", "/models"]:
                show_all_providers_and_models(config)
                continue
            elif cmd_lower in ["/skills", "/skill"]:
                from skill_manager import show_skills_interactive_menu, install_skill_from_url
                if len(parts) > 1 and parts[1].strip():
                    sub = parts[1].strip()
                    if sub.lower().startswith("add "):
                        install_skill_from_url(sub[4:].strip())
                    elif sub.lower() == "list":
                        show_skills_table()
                    else:
                        install_skill_from_url(sub)
                else:
                    show_skills_interactive_menu()
                continue
            elif cmd_lower in ["/add-skill", "/addskill"]:
                from skill_manager import install_skill_from_url
                if len(parts) > 1 and parts[1].strip():
                    install_skill_from_url(parts[1].strip())
                else:
                    url = Prompt.ask("\n[bold cyan]Masukkan URL GitHub / repo skill (contoh: https://github.com/owner/repo)[/bold cyan]").strip()
                    if url:
                        install_skill_from_url(url)
                continue
            elif cmd_lower in ["/setup", "/config", "/pengaturan", "/settings"]:
                auto_ref = [auto_approve]
                config = show_settings_hub(config, auto_ref)
                auto_approve = auto_ref[0]
                continue
            elif cmd_lower == "/memory":
                console.print(Panel(json.dumps(load_memory(), indent=2), title="🧠 r.outers Memory"))
                continue
            elif cmd_lower == "/help":
                console.print(Panel("""[bold]Perintah Tersedia:[/bold]
• [bold cyan]/setup[/bold cyan] [dim](atau /config)[/dim] : Pusat Pengaturan (API Key, Izin Shell, Skill, Model, Provider, Reset)
• [bold cyan]/model[/bold cyan] [nama]       : Pilih / ganti model AI (atau ketik /m)
• [bold cyan]/provider[/bold cyan]           : Pindah / Tambah Provider API (atau /p)
• [bold cyan]/skills[/bold cyan]             : Pusat Manajemen Skill (Lihat, Tambah dari GitHub, Hapus)
• [bold cyan]/add-skill[/bold cyan] [url]     : Download & pasang skill langsung dari URL GitHub
• [bold cyan]/list[/bold cyan]               : Tabel daftar Provider & Model AI
• [bold cyan]/memory[/bold cyan]             : Lihat memori agent
• [bold cyan]/clear[/bold cyan]              : Bersihkan riwayat chat sesi ini
• [bold cyan]/exit[/bold cyan]               : Keluar
""", title="Bantuan r.outers"))
                continue

        messages.append({"role": "user", "content": user_input})

        while True:
            with console.status(f"[bold cyan]RTS > Thinking...[/bold cyan] [dim](ESC: Stop)[/dim]"):
                reply = call_ai(messages, config)

            if not reply or reply.get("cancelled"):
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
                content = msg.get("content") or ""
                reasoning = msg.get("reasoning_content") or ""
                if content:
                    print_markdown(content)
                elif reasoning:
                    print_markdown(f"*[dim]Alur Berpikir AI / Reasoning:[/dim]*\n\n{reasoning}")
                break

if __name__ == "__main__":
    main()
