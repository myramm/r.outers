import os
import json

GLOBAL_MEMORY_FILE = os.path.expanduser("~/.routers_memory.json")
LOCAL_MEMORY_FILE = ".routers_project_memory.json"

def load_memory():
    mem = {"global": {}, "project": {}}
    if os.path.exists(GLOBAL_MEMORY_FILE):
        try:
            with open(GLOBAL_MEMORY_FILE, "r") as f:
                mem["global"] = json.load(f)
        except Exception:
            pass
    if os.path.exists(LOCAL_MEMORY_FILE):
        try:
            with open(LOCAL_MEMORY_FILE, "r") as f:
                mem["project"] = json.load(f)
        except Exception:
            pass
    return mem

def save_global_memory(key, value):
    mem = {}
    if os.path.exists(GLOBAL_MEMORY_FILE):
        try:
            with open(GLOBAL_MEMORY_FILE, "r") as f:
                mem = json.load(f)
        except Exception:
            pass
    mem[key] = value
    with open(GLOBAL_MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)

def save_project_memory(key, value):
    mem = {}
    if os.path.exists(LOCAL_MEMORY_FILE):
        try:
            with open(LOCAL_MEMORY_FILE, "r") as f:
                mem = json.load(f)
        except Exception:
            pass
    mem[key] = value
    with open(LOCAL_MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)
