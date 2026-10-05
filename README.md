# ⚡ r.outers (CLI AI Coding Agent for Termux)

Autonomous AI Coding Agent designed for Termux Android Linux environment.

## 🚀 Features
- **Full Shell Execution**: Run bash commands (`pkg`, `npm`, `pip`, `git`, `python`, `node`, etc.)
- **Autonomous File Manipulation**: Read, write, and patch code automatically.
- **Long-term Memory**: Persists user preferences and project context across sessions.
- **Auto-Healing**: Catches execution errors, inspects logs, and self-repairs code.
- **YOLO Mode (`/yolo`)**: Auto-pilot mode without manual confirmations.

## 📦 Installation in Termux

```bash
pkg update && pkg install python git -y
pip install requests rich

git clone https://github.com/myramm/r.outers.git ~/r_outers
cd ~/r_outers

cat << 'SCRIPT' > $PREFIX/bin/r.outers
#!/bin/bash
python ~/r_outers/main.py "$@"
SCRIPT
chmod +x $PREFIX/bin/r.outers
ln -sf $PREFIX/bin/r.outers $PREFIX/bin/rts
```

## 🎮 Usage
Cukup jalankan:
```bash
rts
```
