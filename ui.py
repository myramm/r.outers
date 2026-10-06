import random
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

console = Console()

RTS_TIPS = [
    # Vibe Coding & AI Workflow
    "Vibe Coding: Berikan deskripsi fitur yang spesifik, RTS akan menyusun arsitektur dan file kodenya",
    "Vibe Coding: Minta RTS menjalankan test otomatis (e.g. 'buat API login dan jalankan unit testnya')",
    "Vibe Coding: Jika ada error, cukup paste log errornya ke chat, RTS akan inspect dan perbaiki kodenya",
    "Vibe Coding: Gunakan mode thinking 'high' untuk problem solving algoritma & arsitektur kompleks",
    "Vibe Coding: Gunakan /thinking off untuk respon kilat saat membuat boilerplate atau editing ringan",
    "Vibe Coding: Minta RTS audit kode dengan 'review performa dan celah keamanan file ini'",
    "Vibe Coding: Minta RTS buatkan file config (.env.example, Dockerfile, tsconfig.json) otomatis",

    # Node.js & JavaScript / TypeScript
    "Node.js: Gunakan 'node --watch server.js' (Node 18+) untuk auto-reload server tanpa nodemon",
    "Node.js: Jalankan 'npm init -y && npm i express dotenv' untuk setup REST API instan",
    "TypeScript: Gunakan 'npx tsx index.ts' untuk langsung run file TypeScript tanpa build manual",
    "Frontend: Setup project kilat dengan 'npm create vite@latest my-app -- --template react-ts'",
    "Node.js: Pakai 'pnpm' atau 'bun' untuk instalasi dependency yang jauh lebih cepat dan hemat storage",
    "Express: Selalu pasang middleware 'express.json()' sebelum route POST/PUT agar request body terbaca",

    # Go (Golang)
    "Go: Awali proyek baru dengan 'go mod init <nama_modul>' sebelum membuat file .go",
    "Go: Jalankan 'go mod tidy' untuk sinkronisasi dependency dan hapus package yang tidak terpakai",
    "Go: Eksekusi seluruh kode di folder proyek saat ini dengan 'go run .'",
    "Go: Rapikan format kode otomatis sesuai standar Go dengan 'go fmt ./...'",
    "Go: Jalankan unit test dengan 'go test -v ./...' untuk melihat log pengujian lengkap",
    "Go: Gunakan 'sync.WaitGroup' atau channel untuk sinkronisasi goroutine dengan aman",

    # Python & Backend
    "Python: Buat virtual environment dengan 'python3 -m venv .venv && source .venv/bin/activate'",
    "Python: Gunakan 'FastAPI' + 'uvicorn main:app --reload' untuk REST API modern + auto docs",
    "Python: Pakai tool 'uv' (alternatif pip) untuk install dependency Python secepat kilat",
    "Python: Jalankan 'pytest -v' untuk automated testing yang bersih dan terstruktur",

    # Git, DevOps & Terminal
    "Git: Buat checkpoint sebelum refactor dengan 'git add . && git commit -m \"checkpoint\"'",
    "Git: Cek ringkasan perubahan file dengan 'git status -s' atau 'git diff --stat'",
    "Docker: Jalankan 'docker compose up -d' untuk menyalakan database (PostgreSQL/Redis) lokal instan",
    "Database: Gunakan ORM seperti Prisma (Node) atau GORM (Go) untuk type-safety database",

    # RTS Shortcuts & Features
    "RTS: Tekan Tab saat mengetik '/' untuk melihat rekomendasi autocomplete perintah",
    "RTS: Tekan ESC untuk menghentikan proses generasi AI atau eksekusi tool seketika",
    "RTS: Ketik /skills untuk melihat atau memasang skill AI baru dari GitHub (/add-skill)",
    "RTS: Gunakan /model untuk berganti model AI (Nemotron, Claude, DeepSeek, GLM, dll)"
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


