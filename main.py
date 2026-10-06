#!/usr/bin/env python3
import os
import sys
import json
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table

from ui import console, show_banner, print_markdown, show_subtle_tip
from config import (
    get_active_config, update_active_model, switch_provider,
    add_new_provider, load_full_config, save_full_config, PRESET_PROVIDERS,
    THINKING_MODES, get_thinking_mode, update_thinking_mode, get_thinking_budget,
    is_thinking_supported
)
from memory import load_memory
from tools import execute_tool
from client import build_system_prompt, call_ai
from selector import select_model_interactive, select_thinking_interactive
from settings import show_settings_hub
from slash_prompt import get_smart_input
from queue_manager import get_next_queued_message, has_queued_messages
from styles import render_prompt_layout, get_current_style_settings
from model_fetcher import fetch_provider_models, get_popular_models_for_provider

def show_all_providers_and_models(active_config):
    table = Table(title="📡 Daftar Lengkap Provider & Model AI (Live)", header_style="bold cyan")
    table.add_column("No", style="dim", width=4)
    table.add_column("Provider ID", style="bold yellow")
    table.add_column("Base URL", style="dim")
    table.add_column("Model Tersedia (API)", style="green")
    table.add_column("Status", style="bold")

    full_cfg = load_full_config()
    providers = full_cfg.get("providers", {})
    active_id = active_config.get("provider_id", "clouvia")

    for idx, (p_id, p_info) in enumerate(providers.items(), 1):
        status = "[bold green]● AKTIF[/bold green]" if p_id == active_id else "[dim]○ Standby[/dim]"
        url = p_info.get("base_url", "")
        models = fetch_provider_models(p_id)
        m_names = [m["id"] for m in models[:6]]
        if len(models) > 6:
            m_names.append(f"... (+{len(models) - 6} model lainnya)")
        models_str = "\n".join([f"• {m}" for m in m_names]) if m_names else "• (Belum ada model)"
        table.add_row(str(idx), p_id, url, models_str, status)

    console.print(table)

def handle_model_menu(config):
    prov_id = config.get("provider_id", "clouvia")
    rec_models = get_popular_models_for_provider(prov_id, limit=10)
    if not rec_models:
        rec_models = ["free-model", "coding-high", "auto"]

    lines = [f"[bold cyan]Provider Aktif:[/bold cyan] [bold green]{config.get('provider_name')}[/bold green] ([dim]{config.get('base_url')}[/dim])"]
    lines.append(f"[bold]Model Saat Ini:[/bold] [bold yellow]{config.get('model')}[/bold yellow]\n")
    lines.append("[bold]Pilihan Model Cepat (Live API):[/bold]")
    for idx, m in enumerate(rec_models, 1):
        lines.append(f"  [bold yellow]{idx}[/bold yellow]. {m}")
    lines.append("  [bold green]s / m[/bold green]. Buka visual model picker interaktif lengkap (100+ model)")
    lines.append("  [bold cyan]c[/bold cyan]. Ketik nama model custom manual")
    lines.append("  [bold magenta]p[/bold magenta]. Ganti / Tambah Provider")
    lines.append("  [bold blue]l[/bold blue]. Lihat tabel lengkap semua Provider & Model")
    lines.append("  [bold red]e / E[/bold red]. Batal / Kembali (Exit menu)")

    console.print(Panel("\n".join(lines), title="🤖 Pengaturan Model & Provider"))

    choice = Prompt.ask("\nPilih opsi (1-{}, s, c, p, l, e)".format(len(rec_models)), default="1").strip()
    
    # Check Exit / Cancel
    if choice.lower() == "e":
        console.print("[yellow]Batal mengubah model.[/yellow]")
        return config

    if choice.lower() in ("s", "m"):
        return select_model_interactive(config)
    elif choice.lower() == "p":
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
        if is_thinking_supported(new_m):
            config = select_thinking_interactive(config, model_name_display=new_m, is_inline=True)
        else:
            console.print(f"[bold green]✔ Model aktif diubah ke:[/bold green] [bold yellow]{new_m}[/bold yellow]")
        return config

    # Check numeric choice strictly
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(rec_models):
            new_m = rec_models[idx]
            update_active_model(new_m)
            config["model"] = new_m
            if is_thinking_supported(new_m):
                config = select_thinking_interactive(config, model_name_display=new_m, is_inline=True)
            else:
                console.print(f"[bold green]✔ Model aktif diubah ke:[/bold green] [bold yellow]{new_m}[/bold yellow]")
            return config
        else:
            console.print(f"[bold red]❌ Input tidak valid! Pilihan nomor harus antara 1 sampai {len(rec_models)}.[/bold red]")
            return config
    except ValueError:
        console.print(f"[bold red]❌ Input '{choice}' tidak valid! Ketik angka 1-{len(rec_models)}, 's', 'c', 'p', 'l', atau 'e'.[/bold red]")
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

def format_model_name(model_id):
    if not model_id:
        return "Default Model"
    name = model_id.split("/")[-1]
    custom_map = {
        "nemotron-3-super-120b-a12b": "Nemotron 3 Super 120B",
        "nemotron-3.5-lightning-30b-a3b": "Nemotron 3.5 Lightning 30B",
        "nemotron-3-ultra-550b-a55b": "Nemotron 3 Ultra 550B",
        "nemotron-4-340b-instruct": "Nemotron 4 340B",
        "gpt-oss-20b": "GPT OSS 20B",
        "glm-5.3": "GLM 5.3",
        "deepseek-v4.1-flash": "DeepSeek V4.1 Flash",
        "deepseek-v4-pro": "DeepSeek V4 Pro",
        "deepseek-v4-flash": "DeepSeek V4 Flash",
        "diffusiongemma-26b-a4b-it": "DiffusionGemma 26B",
        "coding-high": "Coding High",
        "coding-high-flash": "Coding High Flash",
        "free-model": "Free Model",
        "claude-opus-4.8": "Claude Opus 4.8",
        "claude-sonnet-5-thinking-agentic": "Claude Sonnet 5 Thinking",
        "gemini-3.8-flash": "Gemini 3.8 Flash",
        "kimi-k3": "Kimi K3",
        "minimax-m3": "Minimax M3"
    }
    if name.lower() in custom_map:
        return custom_map[name.lower()]
    cleaned = name.replace("-", " ").replace("_", " ")
    words = []
    for w in cleaned.split():
        if w.lower() in ("ai", "gpt", "glm", "oss", "it", "ui", "api", "rts", "nim"):
            words.append(w.upper())
        elif w.lower() == "deepseek":
            words.append("DeepSeek")
        else:
            words.append(w.capitalize())
    return " ".join(words)

def handle_command(user_input, config, messages, auto_approve):
    cmd_raw = user_input.strip().lower()

    # Status Command
    if cmd_raw in ["status", "/status"]:
        from queue_manager import has_queued_messages
        active_prov = config.get("provider_id", "clouvia")
        curr_model = config.get('model', 'free-model')
        supports_th = is_thinking_supported(curr_model)
        if supports_th:
            th_mode = str(config.get("thinking_mode", "high")).lower()
            th_budget = get_thinking_budget(th_mode)
            th_str = f"{th_mode.upper()} (~{th_budget:,} token budget)" if th_mode != "off" else "OFF (Tanpa Reasoning)"
        else:
            th_str = f"[dim]N/A (Model '{curr_model}' adalah non-reasoning)[/dim]"
        queue_status = "[bold green]1+ pesan antrean menunggu[/bold green]" if has_queued_messages() else "[dim]Kosong (Ready)[/dim]"
        console.print(Panel(f"""[bold]Informasi Status RTS Agent:[/bold]
• Model Aktif    : [bold yellow]{curr_model}[/bold yellow]
• Provider API   : [bold cyan]{active_prov}[/bold cyan]
• Mode Thinking  : [bold magenta]{th_str}[/bold magenta]
• Mode Izin      : [{'green' if auto_approve else 'yellow'}]{'Always Allow (Auto)' if auto_approve else 'Ask Approval'}[/]
• Antrean Pesan  : {queue_status}
• Status Eksekusi: [bold green]Ready / Standby[/bold green]
""", title="⚡ RTS Status"))
        return config, auto_approve

    # Stop / Cancel Command
    elif cmd_raw in ["stop", "cancel", "batal", "/stop", "/cancel"]:
        console.print("\n[bold yellow]⚡ RTS > Task stopped / reset.[/bold yellow]\n")
        return config, auto_approve

    # Slash Commands
    elif user_input.startswith("/"):
        parts = user_input.strip().split(maxsplit=1)
        cmd_lower = parts[0].lower()
        curr_model = config.get('model', 'free-model')
        supports_th = is_thinking_supported(curr_model)
        
        if cmd_lower in ["/clear", "/cls"]:
            th_mode = config.get("thinking_mode", "high")
            messages.clear()
            messages.append({"role": "system", "content": build_system_prompt(thinking_mode=th_mode, model_id=curr_model)})
            sys.stdout.write("\033[H\033[2J\033[3J")
            sys.stdout.flush()
            os.system("clear")
            show_banner()
            console.print("[bold green]✔ Riwayat percakapan & layar dibersihkan. Konteks AI telah direfresh.[/bold green]\n")
            return config, auto_approve
        elif cmd_lower in ["/thinking", "/think", "/t", "/reasoning"]:
            if len(parts) > 1 and parts[1].strip():
                arg = parts[1].strip().lower()
                if arg in THINKING_MODES or (arg.isdigit() and int(arg) > 0):
                    update_thinking_mode(arg)
                    config["thinking_mode"] = arg
                    for m in messages:
                        if m.get("role") == "system":
                            m["content"] = build_system_prompt(thinking_mode=arg, model_id=curr_model)
                    console.print(f"[bold green]✔ Mode Thinking diubah ke:[/bold green] [bold yellow]{arg.upper()}[/bold yellow]")
                    if not supports_th:
                        console.print(f"[dim]ℹ Catatan: Model aktif ('{curr_model}') tidak memiliki native reasoning. Mode thinking akan aktif otomatis saat menggunakan model reasoning (DeepSeek R1, Claude Thinking, o1/o3/o4, QwQ, dll).[/dim]\n")
                    else:
                        console.print("")
                else:
                    console.print(f"[bold red]❌ Mode thinking '{arg}' tidak valid. Pilihan: off, low, medium, high, max, atau angka token (misal: 4096).[/bold red]\n")
            else:
                config = select_thinking_interactive(config)
                th_mode = config.get("thinking_mode", "high")
                for m in messages:
                    if m.get("role") == "system":
                        m["content"] = build_system_prompt(thinking_mode=th_mode, model_id=curr_model)
            return config, auto_approve
        elif cmd_lower in ["/style", "/styles", "/theme", "/themes", "/prompt-style"]:
            from styles import select_style_and_theme_interactive
            select_style_and_theme_interactive()
            return config, auto_approve
        elif cmd_lower in ["/model", "/m"]:
            if len(parts) > 1 and parts[1].strip():
                new_m = parts[1].strip()
                update_active_model(new_m)
                config["model"] = new_m
                if is_thinking_supported(new_m):
                    config = select_thinking_interactive(config, model_name_display=new_m, is_inline=True)
                else:
                    console.print(f"[bold green]✔ Model diubah ke:[/bold green] [bold yellow]{new_m}[/bold yellow]\n")
            else:
                config = select_model_interactive(config)
            return config, auto_approve
        elif cmd_lower in ["/provider", "/providers", "/p"]:
            config = switch_provider()
            return config, auto_approve
        elif cmd_lower in ["/list", "/models"]:
            show_all_providers_and_models(config)
            return config, auto_approve
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
            return config, auto_approve
        elif cmd_lower in ["/add-skill", "/addskill"]:
            from skill_manager import install_skill_from_url
            if len(parts) > 1 and parts[1].strip():
                install_skill_from_url(parts[1].strip())
            else:
                url = Prompt.ask("\n[bold cyan]Masukkan URL GitHub / repo skill (contoh: https://github.com/owner/repo)[/bold cyan]").strip()
                if url:
                    install_skill_from_url(url)
            return config, auto_approve
        elif cmd_lower in ["/setup", "/config", "/pengaturan", "/settings"]:
            auto_ref = [auto_approve]
            config = show_settings_hub(config, auto_ref)
            auto_approve = auto_ref[0]
            return config, auto_approve
        elif cmd_lower == "/memory":
            console.print(Panel(json.dumps(load_memory(), indent=2), title="🧠 r.outers Memory"))
            return config, auto_approve
        elif cmd_lower == "/help":
            console.print(Panel("""[bold]Perintah Tersedia:[/bold]
• [bold cyan]status[/bold cyan] [dim](atau /status)[/dim]   : Cek status agent aktif, mode thinking, & antrean pesan
• [bold cyan]stop[/bold cyan] [dim](atau /stop, cancel)[/dim]: Hentikan atau batalkan task aktif
• [bold cyan]/thinking[/bold cyan] [mode]     : Mode Thinking (off, low, medium, high, max, custom) (/think, /t)
• [bold cyan]/setup[/bold cyan] [dim](atau /config)[/dim]   : Pusat Pengaturan (API Key, Izin Shell, Skill, Model, Provider, Reset)
• [bold cyan]/style[/bold cyan] [dim](atau /theme)[/dim]    : Ubah Style Terminal & Tema Warna (Agy, Cyber, Powerline, Minimal)
• [bold cyan]/model[/bold cyan] [nama]         : Pilih / ganti model AI (atau ketik /m)
• [bold cyan]/provider[/bold cyan]             : Pindah / Tambah Provider API (atau /p)
• [bold cyan]/skills[/bold cyan]               : Pusat Manajemen Skill (Lihat, Tambah dari GitHub, Hapus)
• [bold cyan]/add-skill[/bold cyan] [url]       : Download & pasang skill langsung dari URL GitHub
• [bold cyan]/list[/bold cyan]                 : Tabel daftar Provider & Model AI
• [bold cyan]/memory[/bold cyan]               : Lihat memori agent
• [bold cyan]/clear[/bold cyan]                : Bersihkan riwayat chat sesi ini
• [bold cyan]/exit[/bold cyan]                 : Keluar
""", title="Bantuan r.outers"))
            return config, auto_approve

    messages.append({"role": "user", "content": user_input})

    # Task Execution Lifecycle (RUNNING -> DONE / CANCELLED / ERROR -> IDLE)
    turn_count = 0
    max_tool_turns = 15

    while turn_count < max_tool_turns:
        turn_count += 1
        reply = None
        try:
            reply = call_ai(messages, config)
        except Exception as e:
            console.print(f"[bold red]✘ Error calling AI:[/bold red] {e}\n")
            break

        if not reply or reply.get("cancelled"):
            break

        choices = reply.get("choices")
        if not choices or not isinstance(choices, list) or len(choices) == 0:
            break

        msg = choices[0].get("message", {})
        if not msg:
            break

        messages.append(msg)

        # 1. Extract reasoning / thinking if available
        reasoning = (msg.get("reasoning_content") or msg.get("reasoning") or "").strip()
        content = (msg.get("content") or "").strip()

        if not reasoning and "<think>" in content and "</think>" in content:
            import re
            m = re.search(r"<think>(.*?)</think>", content, flags=re.DOTALL)
            if m:
                reasoning = m.group(1).strip()
                content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

        # Render thinking process if present and thinking mode is not OFF
        th_mode_str = str(config.get("thinking_mode", "high")).lower()
        if reasoning and th_mode_str != "off":
            th_mode_display = th_mode_str.upper()
            console.print(Panel(
                f"[dim italic]{reasoning}[/dim italic]",
                title=f"🧠 Thinking Process ({th_mode_display})",
                title_align="left",
                border_style="cyan dim",
                padding=(0, 1)
            ))

        if msg.get("tool_calls"):
            for tool in msg["tool_calls"]:
                fn_name = tool.get("function", {}).get("name", "")
                try:
                    fn_args = json.loads(tool.get("function", {}).get("arguments", "{}"))
                except Exception:
                    fn_args = {}

                try:
                    tool_res = execute_tool(fn_name, fn_args, auto_approve=auto_approve)
                except Exception as e:
                    tool_res = f"Tool execution error: {e}"
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool.get("id", ""),
                    "name": fn_name,
                    "content": str(tool_res)
                })
            continue
        else:
            if content:
                print_markdown(content)
                show_subtle_tip()
            elif not reasoning:
                pass
            break

    return config, auto_approve

def main():
    show_banner()
    full_cfg = load_full_config()
    config = get_active_config()
    auto_approve = (full_cfg.get("permission_mode") == "always_allow") or full_cfg.get("auto_approve", False)
    curr_model = config.get('model', 'free-model')
    thinking_mode = config.get("thinking_mode", "high")
    messages = [{"role": "system", "content": build_system_prompt(thinking_mode=thinking_mode, model_id=curr_model)}]

    while True:
        full_cfg = load_full_config()
        config = get_active_config()
        auto_approve = (full_cfg.get("permission_mode") == "always_allow") or full_cfg.get("auto_approve", False)
        active_prov = full_cfg.get("active_provider", "clouvia")
        curr_model = config.get('model', 'free-model')
        thinking_mode = config.get("thinking_mode", "high")

        # 1. IDLE: Check queued message or get interactive input
        queued_msg = get_next_queued_message()
        if queued_msg:
            user_input = queued_msg
            _, cur_theme = get_current_style_settings()
            layout = render_prompt_layout("box", cur_theme, provider_name=active_prov, model_name=curr_model, auto_approve=auto_approve, thinking_mode=thinking_mode, current_input=user_input, cursor_col=len(user_input))
            prefix_disp = layout.get('prefix_rendered', '> ')
            sys.stdout.write(f"\033[2K{prefix_disp}\033[1;37m{user_input}\033[0m\r\n\033[2K{layout['divider']}\r\n")
            sys.stdout.flush()
        else:
            try:
                user_input = get_smart_input(provider_name=active_prov, model_name=curr_model, auto_approve=auto_approve, thinking_mode=thinking_mode)
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Keluar...[/yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]Input Error:[/bold red] {e}\n")
                continue

        if not user_input or not user_input.strip():
            continue

        if user_input.strip().lower() in ["/exit", "/quit"]:
            break

        # 2. RUNNING: Execute command or AI turn safely
        try:
            config, auto_approve = handle_command(user_input, config, messages, auto_approve)
        except Exception as e:
            console.print(f"[bold red]Execution Error:[/bold red] {e}\n")

if __name__ == "__main__":
    main()
