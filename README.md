# ⚡ r.outers (rts v1.0.0)

CLI tool ultra-ringan buat **vibe coding langsung di Android (Termux) & Linux**. Mirip sistem **9routers** / LLM router wrapper, dirancang untuk memudahkan coding lewat smartphone tanpa bloatware berat ala OpenCode. Mendukung eksekusi shell otonom, multi-provider routing (NVIDIA NIM 80+ model, custom endpoint), pemilihan model instan, dan konfigurasi manual `~/.routers_config.json`.

---

## 🚀 Cara Install

### 1. One-Line Instant Install (Termux & Linux)
Jalankan perintah ini langsung di terminal Anda:

```bash
curl -fsSL https://raw.githubusercontent.com/myramm/r.outers/main/install.sh | bash
```

> **💡 Tips untuk Pengguna Termux (Jika baru update Python / Error libexpat):**
> Pastikan library sistem sudah ter-update terlebih dahulu:
> ```bash
> pkg update -y && pkg install -y libexpat python-pip git curl
> curl -fsSL https://raw.githubusercontent.com/myramm/r.outers/main/install.sh | bash
> ```

---

### 2. Cara Manual (Git Clone)
Jika ingin menginstall secara manual:

```bash
git clone https://github.com/myramm/r.outers.git ~/r_outers
cd ~/r_outers
pip install -r requirements.txt 2>/dev/null || pip install requests rich
chmod +x main.py
ln -sf ~/r_outers/main.py /data/data/com.termux/files/usr/bin/rts 2>/dev/null || ln -sf ~/r_outers/main.py /usr/local/bin/rts
```

---

## 🎮 Cara Menjalankan

Setelah terinstall, cukup ketik salah satu perintah berikut:

```bash
rts
```
*(atau bisa juga `r.outers` / `routers`)*

---

## 📋 Daftar Perintah Slash (Slash Commands)

Ketik `/` di dalam prompt CLI untuk memunculkan menu bantuan interaktif:

| Perintah | Deskripsi |
| :--- | :--- |
| `/thinking` *(atau `/think`, `/t`)* | **Mode Thinking / Reasoning**: Atur kedalaman berpikir AI (`off`, `low`, `medium`, `high`, `max`, atau custom tokens) |
| `/setup` *(atau `/config`)* | **Pusat Pengaturan**: Kelola API Key, Mode Thinking, Izin Shell, Kelola Skill, Model, Provider, Reset Total |
| `/style` *(atau `/theme`)* | **Terminal Style & Theme (Agy Style)**: Ubah tampilan prompt & palette warna (Agy, Cyber, Powerline, Minimal, Classic) |
| `/skills` | **Pusat Manajemen Skill**: Menu interaktif untuk lihat daftar, tambah dari GitHub, atau hapus skill |
| `/add-skill` *[url]* | **Pasang Skill Baru**: Unduh dan pasang skill langsung dari URL repository GitHub |
| `/model` *(atau `/m`)* | **Interactive Model Selector**: Pilih dan ganti model AI dengan navigasi keyboard yang responsif |
| `/provider` *(atau `/p`)* | **Ganti / Tambah Provider API** (9Router, Atria, NVIDIA NIM, OpenRouter, Custom) |
| `/list` | Tabel daftar lengkap semua Provider & Model yang tersedia |
| `/memory` | Lihat dan kelola memori proyek yang tersimpan |
| `/clear` | Bersihkan riwayat percakapan sesi ini dan refresh konteks AI |
| `/exit` *(atau `/quit`)* | Keluar dari CLI secara bersih (*atau tekan `Ctrl + D`*) |

---

## 🧠 Mode Thinking / Reasoning (Mirip OpenCode / Claude Code)

`rts` mendukung pengaturan budget penalaran (*thinking mode*) yang terintegrasi langsung dengan model-model AI reasoning modern (seperti DeepSeek R1, Claude Sonnet 3.7/5 Thinking, OpenAI o1/o3/o4, QwQ, dll).

### Level Thinking yang Tersedia:
- **`off`**: Tanpa thinking (Respons instan, hemat token, cocok untuk pertanyaan cepat).
- **`low`**: Penalaran ringan (~2k token budget, cepat & efisien).
- **`medium`**: Penalaran menengah (~8k token budget, seimbang untuk tugas harian).
- **`high`** *(Default)*: Penalaran mendalam (~16k token budget, cocok untuk arsitektur & coding kompleks).
- **`max`**: Penalaran maksimal (~32k token budget, untuk deep proof & debugging ekstensif).
- **`custom`**: Alokasikan jumlah token thinking manual sesuai kebutuhan (misal: 4096, 64000).

### Cara Mengubah Mode Thinking:
1. **Perintah Cepat CLI**:
   ```bash
   /thinking high
   /thinking low
   /thinking off
   /thinking 8192
   ```
2. **Menu Visual Interaktif**:
   Ketik `/thinking` (atau `/think` / `/t`) tanpa argumen, atau buka `/setup` dan pilih menu **🧠 Mode Thinking (Reasoning)** untuk membuka selector dengan navigasi panah keyboard (`UP`/`DOWN`/`Enter`/`Esc`).

---

## ⚡ Cara Menambah Skill Baru ke `rts`

`rts` mendukung ekstensi modul keahlian (*skills*) yang berisi instruksi spesialisasi (seperti standar Anti-Slop, TDD, Systematic Debugging, UI/UX, dll).

### Metode 1: Perintah Langsung CLI
Ketik `/add-skill` diikuti link repository GitHub:
```text
r.outers > /add-skill https://github.com/miqdadbadjuber/anti-slop
```
atau:
```text
r.outers > /add-skill https://github.com/obra/superpowers
```

### Metode 2: Menu Interaktif `/skills`
1. Buka CLI dengan `rts`
2. Ketik `/skills`
3. Pilih opsi **➕ Tambah Skill Baru (dari URL GitHub)**
4. Tempel (*paste*) URL repository GitHub skill yang Anda inginkan.

### Metode 3: Pemasangan Manual (Folder)
Anda juga dapat meletakkan folder skill (yang berisi file `SKILL.md`) secara langsung ke salah satu direktori berikut:
- Direktori lokal: `~/r_outers/skills/<nama-skill>/SKILL.md`
- Direktori global: `~/.agents/skills/<nama-skill>/SKILL.md`

> Semua skill yang terpasang akan otomatis dideteksi dan dapat dipanggil oleh AI secara mandiri saat dibutuhkan!

---

## 🔑 Pengaturan & Cara Kelola Konfigurasi (Manual JSON)

Semua konfigurasi model, provider, API key, timeout, dan preferensi CLI tersimpan rapi dan dapat diedit secara manual di file `~/.routers_config.json`.

### Format Lengkap `~/.routers_config.json`:

```json
{
  "active_provider": "nvidia",
  "providers": {
    "9router": {
      "name": "9Router",
      "base_url": "https://your-9router.up.railway.app/v1",
      "api_key": "sk-your-9router-key",
      "model": "ag/gemini-3.7-flash-high",
      "timeout": 180
    },
    "nvidia": {
      "name": "NVIDIA NIM",
      "base_url": "https://integrate.api.nvidia.com/v1",
      "api_key": "nvapi-your-key-here",
      "model": "nvidia/nemotron-3-super-120b-a12b",
      "timeout": 180,
      "temperature": 0.2,
      "max_tokens": 8192
    },
    "atria": {
      "name": "Atria ASI",
      "base_url": "https://api.atria-asi.ai/v1",
      "api_key": "your-atria-key",
      "model": "Atria-Dawn-Preview",
      "timeout": 120
    },
    "custom_openai": {
      "name": "Custom Endpoint / Ollama / Local",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "model": "qwen2.5-coder:32b",
      "timeout": 180
    }
  },
  "settings": {
    "theme": "tokyonight",
    "prompt_style": "double_line",
    "history_file": "~/.routers_history",
    "skills_dir": "~/.agents/skills"
  }
}
```

### Cara Mengedit File Konfigurasi:
```bash
nano ~/.routers_config.json
```

### Alternatif via File `.env` / Environment Variable:
Anda juga dapat memasukkan API Key di file `.env`:
```env
NINEROUTER_API_KEY=sk-your_9router_key_here
NVIDIA_API_KEY=nvapi-your_nvidia_api_key_here
ATRIA_API_KEY=your_atria_api_key_here
```

---

## 🗑️ Cara Menghapus / Uninstall `rts`

Jika Anda ingin menghapus `rts` dari Termux atau Linux, tersedia beberapa cara:

### Cara 1: One-Line Uninstall Command (Paling Praktis)
Jalankan satu baris perintah ini di terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/myramm/r.outers/main/uninstall.sh | bash
```

---

### Cara 2: Menghapus Secara Manual via Terminal
Jalankan baris perintah berikut untuk menghapus folder program, shortcut global, dan file konfigurasinya:

```bash
# 1. Hapus folder program r.outers
rm -rf ~/r_outers

# 2. Hapus shortcut eksekusi global di Termux / Linux
rm -f /data/data/com.termux/files/usr/bin/rts /data/data/com.termux/files/usr/bin/r.outers /data/data/com.termux/files/usr/bin/routers 2>/dev/null
sudo rm -f /usr/local/bin/rts /usr/local/bin/r.outers /usr/local/bin/routers 2>/dev/null

# 3. Hapus cache konfigurasi & memori lokal
rm -f ~/.routers_config.json ~/.routers_memory.json ~/.routers_project_memory.json
```

---

### Cara 3: Dari Dalam CLI (`/setup`)
1. Jalankan `rts`
2. Ketik `/setup`
3. Pilih **🗑️ Reset Total & Hapus Instalasi**

---

## ✨ Fitur Unggulan
- **Full Autonomous Shell**: Eksekusi perintah bash (`pkg`, `npm`, `pip`, `git`, `python`, `node`, dll) disertai *Live Progress Loading Spinner* & pembatalan cepat (<kbd>ESC</kbd>).
- **Integrated Anti-Slop & Superpowers**: Didukung standar Anti-Slop (anti kode template murahan) dan Superpowers (TDD, Systematic Debugging, Pre-flight Verification).
- **Dynamic Skill Loader (`/skills` & `/add-skill`)**: Otomatis mendeteksi dan mengunduh modul skill dari GitHub langsung ke perangkat.
- **Support 80+ Model NVIDIA NIM, 9Router, OpenRouter & Atria**: Akses model unggulan seperti Gemini 3.7 Flash High, Nemotron 120B/340B, GPT-OSS 20B, DeepSeek, GLM, dll.
- **Smart Keyboard Navigation**: Dukungan tombol panah, Tab autocomplete, ESC cancel, pencarian filter cepat, dan input sensitif yang nyaman di HP.
- **Autonomous Code Editor**: Membaca, membuat, mencari, dan mengedit file secara presisi.
- **Long-term Memory**: Mengingat preferensi Anda dan struktur proyek lintas sesi.
- **Auto-Healing**: Mendeteksi error eksekusi dan memperbaikinya secara otonom.

---

## 📄 Lisensi
MIT License © 2026 [myramm](https://github.com/myramm)
