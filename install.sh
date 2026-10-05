#!/bin/bash
set -e

echo -e "\033[1;36m==========================================\033[0m"
echo -e "\033[1;36m   ⚡ Installing r.outers AI Agent...    \033[0m"
echo -e "\033[1;36m==========================================\033[0m"

# 1. Update & Install Packages
echo -e "\n\033[1;33m[1/4] Menginstall dependencies...\033[0m"
pkg update -y || apt-get update -y
pkg install -y python git curl || apt-get install -y python3 python3-pip git curl

# 2. Install Python Libraries
echo -e "\n\033[1;33m[2/4] Menginstall pustaka Python (requests, rich)...\033[0m"
pip install --upgrade requests rich || pip3 install --upgrade requests rich

# 3. Clone / Update Repository
echo -e "\n\033[1;33m[3/4] Mengunduh r.outers dari GitHub...\033[0m"
INSTALL_DIR="$HOME/r_outers"

if [ -d "$INSTALL_DIR" ]; then
    echo "Folder $INSTALL_DIR sudah ada, memperbarui..."
    cd "$INSTALL_DIR" && git pull origin main
else
    git clone https://github.com/myramm/r.outers.git "$INSTALL_DIR"
fi

# 4. Buat Shortcut Executable di Termux / Linux
echo -e "\n\033[1;33m[4/4] Memasang shortcut global (r.outers, rts)...\033[0m"
BIN_DIR="${PREFIX:-/usr/local}/bin"
mkdir -p "$BIN_DIR"

cat << 'SCRIPT' > "$BIN_DIR/r.outers"
#!/bin/bash
python3 "$HOME/r_outers/main.py" "$@"
SCRIPT

chmod +x "$BIN_DIR/r.outers"
ln -sf "$BIN_DIR/r.outers" "$BIN_DIR/routers"
ln -sf "$BIN_DIR/r.outers" "$BIN_DIR/rts"

echo -e "\n\033[1;32m==========================================\033[0m"
echo -e "\033[1;32m       ✔ INSTALASI BERHASIL!             \033[0m"
echo -e "\033[1;32m==========================================\033[0m"
echo -e "\nJalankan AI agent kapan saja dengan mengetik:\n"
echo -e "   \033[1;36mrts\033[0m  atau  \033[1;36mr.outers\033[0m\n"
