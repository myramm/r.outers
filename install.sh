#!/bin/bash
set -e

echo -e "\033[1;36m==========================================\033[0m"
echo -e "\033[1;36m   ⚡ Installing r.outers AI Agent...    \033[0m"
echo -e "\033[1;36m==========================================\033[0m"

# 1. Update & Install Packages
echo -e "\n\033[1;33m[1/4] Memeriksa & menginstall dependencies...\033[0m"
if command -v pkg >/dev/null 2>&1; then
    pkg update -y
    pkg install -y python git curl
elif command -v apt-get >/dev/null 2>&1; then
    apt-get update -y
    apt-get install -y python3 python3-pip git curl
elif command -v dnf >/dev/null 2>&1; then
    dnf install -y python3 python3-pip git curl
elif command -v pacman >/dev/null 2>&1; then
    pacman -Sy --noconfirm python python-pip git curl
fi

# 2. Install Python Libraries
echo -e "\n\033[1;33m[2/4] Menginstall pustaka Python (requests, rich)...\033[0m"
pip install --upgrade requests rich --break-system-packages 2>/dev/null || \
pip3 install --upgrade requests rich --break-system-packages 2>/dev/null || \
pip install --upgrade requests rich || \
pip3 install --upgrade requests rich

# 3. Clone / Update Repository
echo -e "\n\033[1;33m[3/4] Mengunduh r.outers dari GitHub...\033[0m"
INSTALL_DIR="$HOME/r_outers"

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Folder $INSTALL_DIR sudah ada, memperbarui kode..."
    git -C "$INSTALL_DIR" pull origin main
elif [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    git clone https://github.com/myramm/r.outers.git "$INSTALL_DIR"
else
    git clone https://github.com/myramm/r.outers.git "$INSTALL_DIR"
fi

# 4. Buat Shortcut Executable di Termux / Linux
echo -e "\n\033[1;33m[4/4] Memasang shortcut global (r.outers, rts)...\033[0m"
if [ -n "$PREFIX" ]; then
    BIN_DIR="$PREFIX/bin"
else
    BIN_DIR="/usr/local/bin"
fi
mkdir -p "$BIN_DIR"

cat << 'SCRIPT' > "$BIN_DIR/r.outers"
#!/bin/bash
if command -v python3 >/dev/null 2>&1; then
    python3 "$HOME/r_outers/main.py" "$@"
else
    python "$HOME/r_outers/main.py" "$@"
fi
SCRIPT

chmod +x "$BIN_DIR/r.outers"
ln -sf "$BIN_DIR/r.outers" "$BIN_DIR/routers"
ln -sf "$BIN_DIR/r.outers" "$BIN_DIR/rts"

echo -e "\n\033[1;32m==========================================\033[0m"
echo -e "\033[1;32m       ✔ INSTALASI BERHASIL!             \033[0m"
echo -e "\033[1;32m==========================================\033[0m"
echo -e "\nJalankan AI agent kapan saja dengan mengetik:\n"
echo -e "   \033[1;36mrts\033[0m  atau  \033[1;36mr.outers\033[0m\n"
