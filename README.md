# ⚡ r.outers (CLI AI Coding Agent for Termux & Linux)

Autonomous AI Coding Agent designed for Android Termux and Linux environments.

---

## 🚀 Cara Install

### 1. One-Line Instant Install (Termux & Linux)
Jalankan perintah ini langsung di terminal Anda:

```bash
curl -fsSL https://raw.githubusercontent.com/myramm/r.outers/main/install.sh | bash
```

> **💡 Tips untuk Pengguna Termux (Jika baru update Python / Error expat):**
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

## 🔑 Pengaturan & Cara Menghapus API Key

### A. Melalui Menu Interaktif CLI
1. Buka CLI dengan perintah `rts`
2. Ketik `/setup` (atau `/config`)
3. Pilih **🔑 Kelola API Key**
4. Masukkan API Key baru Anda atau kosongkan untuk menghapusnya.

### B. Melalui File Konfigurasi (Manual)
Konfigurasi API Key tersimpan secara lokal di file `~/.routers_config.json`.
Untuk mengedit atau menghapus API key secara manual:

```bash
nano ~/.routers_config.json
```
Cari bagian `"api_key": "..."` dan ubah menjadi `"api_key": ""`.

### C. Melalui File `.env` / Environment Variable
Anda juga dapat memasukkan API Key di file `~/.env`:
```env
CLOUVIA_API_KEY=your_clouvia_api_key_here
ATRIA_API_KEY=your_atria_api_key_here
```

---

## 📋 Daftar Perintah Slash (Slash Commands)

Ketik `/` di dalam prompt CLI untuk memunculkan menu bantuan interaktif:

| Perintah | Deskripsi |
| :--- | :--- |
| `/setup` *(atau `/config`)* | **Pusat Pengaturan**: Kelola API Key, Izin Shell (Auto-Approve / Tanya y/n), Model, Provider, Reset |
| `/model` *(atau `/m`)* | **Interactive Model Selector**: Pilih dan ganti model AI dengan navigasi keyboard |
| `/provider` *(atau `/p`)* | **Ganti / Tambah Provider API** (Clouvia, Atria, Custom Provider) |
| `/list` | Tabel daftar lengkap semua Provider & Model yang tersedia |
| `/memory` | Lihat dan kelola memori proyek yang tersimpan |
| `/clear` | Bersihkan riwayat chat dan context sesi aktif |
| `/exit` *(atau `/quit`)* | Keluar dari CLI secara bersih (*atau tekan `Ctrl + D`*) |

---

## 🗑️ Cara Menghapus / Uninstall `rts`

Jika Anda ingin menghapus total `rts` beserta semua konfigurasinya dari Termux / Linux:

```bash
# 1. Hapus folder aplikasi
rm -rf ~/r_outers

# 2. Hapus shortcut eksekusi global
rm -f /data/data/com.termux/files/usr/bin/rts /data/data/com.termux/files/usr/bin/r.outers /data/data/com.termux/files/usr/bin/routers 2>/dev/null
sudo rm -f /usr/local/bin/rts /usr/local/bin/r.outers /usr/local/bin/routers 2>/dev/null

# 3. Hapus file konfigurasi & memori lokal (opsional)
rm -f ~/.routers_config.json ~/.routers_memory.json ~/.routers_project_memory.json
```

---

## ✨ Fitur Unggulan
- **Full Autonomous Shell**: Eksekusi perintah bash (`pkg`, `npm`, `pip`, `git`, `python`, `node`, dll) disertai *Live Progress Loading Spinner*.
- **Smart Keyboard Navigation**: Dukungan tombol panah, Tab autocomplete, ESC cancel, dan shortcut cepat.
- **Autonomous Code Editor**: Membaca, membuat, mencari, dan mengedit file secara presisi.
- **Long-term Memory**: Mengingat preferensi Anda dan struktur proyek lintas sesi.
- **Auto-Healing**: Mendeteksi error eksekusi dan memperbaikinya secara otonom.

---

## 📄 Lisensi
MIT License © 2026 [myramm](https://github.com/myramm)
