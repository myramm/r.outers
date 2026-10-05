#!/bin/bash
set -e

echo -e "\033[1;31m==========================================\033[0m"
echo -e "\033[1;31m   🗑️  Uninstalling r.outers (rts)...     \033[0m"
echo -e "\033[1;31m==========================================\033[0m"

# 1. Hapus Shortcut Global
echo -e "\n\033[1;33m[1/3] Menghapus shortcut global...\033[0m"
if [ -n "$PREFIX" ]; then
    rm -f "$PREFIX/bin/rts" "$PREFIX/bin/r.outers" "$PREFIX/bin/routers" 2>/dev/null || true
else
    if [ "$EUID" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
        sudo rm -f /usr/local/bin/rts /usr/local/bin/r.outers /usr/local/bin/routers 2>/dev/null || true
    else
        rm -f /usr/local/bin/rts /usr/local/bin/r.outers /usr/local/bin/routers 2>/dev/null || true
    fi
fi
echo "✔ Shortcut global berhasil dihapus."

# 2. Hapus Folder Program
echo -e "\n\033[1;33m[2/3] Menghapus folder program r.outers...\033[0m"
INSTALL_DIR="$HOME/r_outers"
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "✔ Folder $INSTALL_DIR berhasil dihapus."
else
    echo "ℹ Folder $INSTALL_DIR tidak ditemukan."
fi

# 3. Hapus Konfigurasi & Memori Lokal
echo -e "\n\033[1;33m[3/3] Membersihkan file konfigurasi & cache...\033[0m"
rm -f "$HOME/.routers_config.json" "$HOME/.routers_memory.json" "$HOME/.routers_project_memory.json" 2>/dev/null || true
echo "✔ File konfigurasi & cache berhasil dibersihkan."

echo -e "\n\033[1;32m==========================================\033[0m"
echo -e "\033[1;32m   ✔ r.outers (rts) Berhasil Dihapus!    \033[0m"
echo -e "\033[1;32m==========================================\033[0m\n"
