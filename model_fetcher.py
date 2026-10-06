import os
import sys
import json
import time
import requests
from config import load_full_config, load_env_keys

CACHE_FILE = os.path.expanduser("~/.routers_models_cache.json")
CACHE_TTL_SECONDS = 3600  # 1 hour cache validity

FALLBACK_DEFAULT_MODELS = [
    {"id": "auto", "name": "Auto Router", "provider_id": "clouvia", "provider_name": "Clouvia", "tag": "AUTO", "fav": True},
    {"id": "coding-high", "name": "Coding High Speed", "provider_id": "clouvia", "provider_name": "Clouvia", "tag": "CODE", "fav": True},
    {"id": "free-model", "name": "Free Router Model", "provider_id": "clouvia", "provider_name": "Clouvia", "tag": "FREE", "fav": True},
    {"id": "gemini-3.8-flash-high", "name": "Gemini 3.8 Flash High", "provider_id": "clouvia", "provider_name": "Clouvia", "tag": "FAST", "fav": True},
    {"id": "claude-sonnet-5-thinking-agentic", "name": "Claude Sonnet 5 Thinking Agentic", "provider_id": "clouvia", "provider_name": "Clouvia", "tag": "REASON", "fav": True},
    {"id": "deepseek-v4-pro", "name": "DeepSeek V4 Pro", "provider_id": "clouvia", "provider_name": "Clouvia", "tag": "TOP", "fav": True},
    {"id": "qwen-3.8-max-thinking-agentic", "name": "Qwen 3.8 Max Thinking Agentic", "provider_id": "clouvia", "provider_name": "Clouvia", "tag": "REASON", "fav": True},
    {"id": "kimi-k3", "name": "Kimi K3", "provider_id": "clouvia", "provider_name": "Clouvia", "tag": "AI", "fav": False},
    {"id": "glm5.3-thinking-agentic", "name": "GLM 5.3 Thinking Agentic", "provider_id": "clouvia", "provider_name": "Clouvia", "tag": "REASON", "fav": True},
    {"id": "Atria-Dawn-Preview", "name": "Atria Dawn Preview", "provider_id": "atria", "provider_name": "Atria ASI", "tag": "TOP", "fav": True},
    {"id": "nvidia/nemotron-3-super-120b-a12b", "name": "Nemotron 3 Super 120B", "provider_id": "nvidia", "provider_name": "NVIDIA NIM", "tag": "TOP", "fav": True},
]

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache_data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except Exception:
        pass

def format_model_entry(raw_model_obj, provider_id="clouvia", provider_name="Clouvia"):
    if isinstance(raw_model_obj, str):
        model_id = raw_model_obj
        context_len = None
        pricing = None
    elif isinstance(raw_model_obj, dict):
        model_id = raw_model_obj.get("id", "")
        context_len = raw_model_obj.get("context_length")
        pricing = raw_model_obj.get("pricing")
    else:
        model_id = str(raw_model_obj)
        context_len = None
        pricing = None

    id_lower = model_id.lower()
    parts = model_id.split("/")[-1]

    # Format human-friendly name
    from styles import MODEL_CLEAN_MAP
    name = MODEL_CLEAN_MAP.get(parts.lower())
    if not name:
        cleaned = parts.replace("-", " ").replace("_", " ")
        words = []
        for w in cleaned.split():
            if w.lower() in ("ai", "gpt", "glm", "oss", "it", "ui", "api", "rts", "nim", "v4", "v3", "v2", "m3", "k3"):
                words.append(w.upper())
            elif w.lower() == "deepseek":
                words.append("DeepSeek")
            elif w.lower() == "claude":
                words.append("Claude")
            elif w.lower() == "gemini":
                words.append("Gemini")
            elif w.lower() == "qwen":
                words.append("Qwen")
            elif w.lower() == "kimi":
                words.append("Kimi")
            elif w.lower() == "minimax":
                words.append("Minimax")
            else:
                words.append(w.capitalize())
        name = " ".join(words)

    # Intelligent tagging and favoritism
    tag = "AI"
    fav = False

    if model_id in ("free-model", "auto"):
        tag = "FREE" if model_id == "free-model" else "AUTO"
        fav = True
    elif "coder" in id_lower or "coding" in id_lower:
        tag = "CODE"
        fav = True
    elif any(k in id_lower for k in ["thinking", "agentic", "reason", "r1"]):
        tag = "REASON"
        if any(k in id_lower for k in ["sonnet", "qwen", "glm", "deepseek", "opus"]):
            fav = True
    elif any(k in id_lower for k in ["flash", "lightning", "lite", "turbo"]):
        tag = "FAST"
        if "flash-high" in id_lower or "lightning" in id_lower:
            fav = True
    elif any(k in id_lower for k in ["pro", "super", "ultra", "opus", "max", "sol", "high"]):
        tag = "TOP"
        fav = True
    elif any(k in id_lower for k in ["plus", "medium"]):
        tag = "SMART"

    return {
        "id": model_id,
        "name": name,
        "provider_id": provider_id,
        "provider_name": provider_name,
        "tag": tag,
        "fav": fav,
        "context": context_len,
        "pricing": pricing
    }

def fetch_provider_models(provider_id="clouvia", base_url=None, api_key=None, force_refresh=False):
    """
    Fetch models automatically from the provider's /v1/models endpoint (or fallback https://router.clouvia.id/v1/models).
    Caches the results locally to guarantee fast offline startup.
    """
    cache = load_cache()
    now = time.time()
    cache_entry = cache.get(provider_id, {})

    if not force_refresh and cache_entry:
        cached_time = cache_entry.get("timestamp", 0)
        cached_models = cache_entry.get("models", [])
        if cached_models and (now - cached_time) < CACHE_TTL_SECONDS:
            return cached_models

    full_cfg = load_full_config()
    providers = full_cfg.get("providers", {})
    prov_cfg = providers.get(provider_id, {})

    if not base_url:
        base_url = prov_cfg.get("base_url") or "https://router.clouvia.id/v1"
    if not api_key:
        api_key = prov_cfg.get("api_key") or ""
        if not api_key:
            env_keys = load_env_keys()
            if provider_id == "clouvia":
                api_key = env_keys.get("CLOUVIA_API_KEY", os.environ.get("CLOUVIA_API_KEY", ""))
            elif provider_id == "atria":
                api_key = env_keys.get("ATRIA_API_KEY", os.environ.get("ATRIA_API_KEY", ""))
            elif provider_id == "nvidia":
                api_key = env_keys.get("NVIDIA_API_KEY", os.environ.get("NVIDIA_API_KEY", os.environ.get("NVAPI_KEY", "")))
            else:
                api_key = env_keys.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))

    prov_name = prov_cfg.get("name", provider_id.capitalize())

    # Determine endpoint URLs to try
    urls_to_try = []
    clean_base = base_url.rstrip("/")
    if clean_base.endswith("/v1"):
        urls_to_try.append(f"{clean_base}/models")
    else:
        urls_to_try.append(f"{clean_base}/v1/models")
        urls_to_try.append(f"{clean_base}/models")

    if provider_id == "clouvia":
        urls_to_try.insert(0, "https://router.clouvia.id/v1/models")

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    fetched_models = []
    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                raw_items = data.get("data", [])
                if isinstance(raw_items, list) and raw_items:
                    for item in raw_items:
                        entry = format_model_entry(item, provider_id=provider_id, provider_name=prov_name)
                        fetched_models.append(entry)
                    break
        except Exception:
            continue

    if fetched_models:
        # Cache successful fetch
        cache[provider_id] = {
            "timestamp": now,
            "models": fetched_models
        }
        save_cache(cache)
        return fetched_models

    # If fetch failed, return existing cached models if available
    if cache_entry.get("models"):
        return cache_entry["models"]

    # Fallback to defaults filtered by provider
    defaults = [m for m in FALLBACK_DEFAULT_MODELS if m["provider_id"] == provider_id]
    if defaults:
        return defaults
    return [format_model_entry(prov_cfg.get("model", "default-model"), provider_id=provider_id, provider_name=prov_name)]

def get_all_available_models(current_config=None, force_refresh=False):
    """
    Get all models across active and configured providers, with active provider models first.
    """
    full_cfg = load_full_config()
    active_prov = full_cfg.get("active_provider", "clouvia")
    providers = full_cfg.get("providers", {})

    all_models = []
    seen_ids = set()

    # 1. Fetch live models for active provider
    active_models = fetch_provider_models(active_prov, force_refresh=force_refresh)
    for m in active_models:
        all_models.append(m)
        seen_ids.add((m["provider_id"], m["id"]))

    # 2. Fetch models for other configured providers
    for p_id, p_info in providers.items():
        if p_id != active_prov:
            p_models = fetch_provider_models(p_id, force_refresh=force_refresh)
            for m in p_models:
                key = (m["provider_id"], m["id"])
                if key not in seen_ids:
                    all_models.append(m)
                    seen_ids.add(key)

    # 3. Add default presets if not already present
    for m in FALLBACK_DEFAULT_MODELS:
        key = (m["provider_id"], m["id"])
        if key not in seen_ids:
            all_models.append(m)
            seen_ids.add(key)

    return all_models

def get_popular_models_for_provider(provider_id="clouvia", limit=10):
    models = fetch_provider_models(provider_id)
    # Put favorites first, then by tag
    favs = [m for m in models if m.get("fav")]
    others = [m for m in models if not m.get("fav")]
    combined = favs + others
    return [m["id"] for m in combined[:limit]]
