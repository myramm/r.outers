import os
import sys
import select
import tty
import termios
from ui import console
from config import (
    load_full_config, save_full_config, update_active_model,
    add_new_provider, switch_provider, PRESET_PROVIDERS
)

DEFAULT_MODELS_CATALOG = [   {   'fav': True,
        'id': 'free-model',
        'name': 'Free Router Model',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FREE'},
    {   'fav': True,
        'id': 'coding-high',
        'name': 'Coding High Speed',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'CODE'},
    {   'fav': True,
        'id': 'Atria-Dawn-Preview',
        'name': 'Atria Dawn Preview',
        'provider_id': 'atria',
        'provider_name': 'Atria ASI',
        'tag': 'TOP'},
    {'fav': False, 'id': 'auto', 'name': 'Auto', 'provider_id': 'clouvia', 'provider_name': 'Clouvia', 'tag': 'AI'},
    {   'fav': False,
        'id': 'gemini-3.8-flash-high',
        'name': 'Gemini 3.8 Flash High',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'sonnet-4.5-thinking-agentic',
        'name': 'Sonnet 4.5 Thinking Agentic',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'REASON'},
    {   'fav': False,
        'id': 'qwen-3.8-max-thinking-agentic',
        'name': 'Qwen 3.8 Max Thinking Agentic',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'REASON'},
    {   'fav': False,
        'id': 'qwen-3.8-Flash',
        'name': 'Qwen 3.8 Flash',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': True,
        'id': 'qwen3.7-max',
        'name': 'Qwen3.7 Max',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': False,
        'id': 'qwen3.7-plus',
        'name': 'Qwen3.7 Plus',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'SMART'},
    {   'fav': False,
        'id': 'glm5.3-thinking-agentic',
        'name': 'Glm5.3 Thinking Agentic',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'REASON'},
    {   'fav': False,
        'id': 'glm5.3-flash',
        'name': 'Glm5.3 Flash',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {'fav': False, 'id': 'glm5.2', 'name': 'Glm5.2', 'provider_id': 'clouvia', 'provider_name': 'Clouvia', 'tag': 'AI'},
    {   'fav': True,
        'id': 'deepseek-v4-pro',
        'name': 'Deepseek V4 Pro',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': False,
        'id': 'deepseek-v4-flash',
        'name': 'Deepseek V4 Flash',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'kimi-k3',
        'name': 'Kimi K3',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': True,
        'id': 'kimi-k2.7-coder',
        'name': 'Kimi K2.7 Coder',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'CODE'},
    {   'fav': True,
        'id': 'minimax-m3',
        'name': 'Minimax M3',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': True,
        'id': 'claude-opus-4.8',
        'name': 'Claude Opus 4.8',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': False,
        'id': 'deepseek-4.1',
        'name': 'Deepseek 4.1',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'deepseek-4.1-flash',
        'name': 'Deepseek 4.1 Flash',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {'fav': False, 'id': 'sonus', 'name': 'Sonus', 'provider_id': 'clouvia', 'provider_name': 'Clouvia', 'tag': 'AI'},
    {   'fav': True,
        'id': 'coding-high-flash',
        'name': 'Coding High Flash',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'CODE'},
    {   'fav': False,
        'id': 'claude-sonnet-5-thinking-agentic',
        'name': 'Claude Sonnet 5 Thinking Agentic',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'REASON'},
    {   'fav': False,
        'id': 'claude-haiku-4.5-thinking-agentic',
        'name': 'Claude Haiku 4.5 Thinking Agentic',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'REASON'},
    {   'fav': False,
        'id': 'gemini-3.8-flash-medium',
        'name': 'Gemini 3.8 Flash Medium',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.8-flash-low',
        'name': 'Gemini 3.8 Flash Low',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.8-flash',
        'name': 'Gemini 3.8 Flash',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.7-flash-high',
        'name': 'Gemini 3.7 Flash High',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.7-flash-medium',
        'name': 'Gemini 3.7 Flash Medium',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.7-flash-low',
        'name': 'Gemini 3.7 Flash Low',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.6-flash-high',
        'name': 'Gemini 3.6 Flash High',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.6-flash-medium',
        'name': 'Gemini 3.6 Flash Medium',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.6-flash-low',
        'name': 'Gemini 3.6 Flash Low',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.5-flash-high',
        'name': 'Gemini 3.5 Flash High',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3-flash-agent',
        'name': 'Gemini 3 Flash Agent',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.5-flash-low',
        'name': 'Gemini 3.5 Flash Low',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.5-flash-extra-low',
        'name': 'Gemini 3.5 Flash Extra Low',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-pro-agent',
        'name': 'Gemini Pro Agent',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AGENT'},
    {   'fav': False,
        'id': 'gemini-3.1-pro-low',
        'name': 'Gemini 3.1 Pro Low',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'SMART'},
    {   'fav': False,
        'id': 'gpt-oss-120b-medium(xhigh)',
        'name': 'Gpt Oss 120b Medium(xhigh)',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'gpt-oss-120b-medium',
        'name': 'Gpt Oss 120b Medium',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'gemini-3-flash',
        'name': 'Gemini 3 Flash',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.5-flash-lite',
        'name': 'Gemini 3.5 Flash Lite',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.1-flash-lite',
        'name': 'Gemini 3.1 Flash Lite',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-2.5-flash-thinking',
        'name': 'Gemini 2.5 Flash Thinking',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'REASON'},
    {   'fav': False,
        'id': 'gemini-2.5-flash',
        'name': 'Gemini 2.5 Flash',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-2.5-flash-lite',
        'name': 'Gemini 2.5 Flash Lite',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-2.5-pro',
        'name': 'Gemini 2.5 Pro',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'SMART'},
    {   'fav': False,
        'id': 'gemini-3.8-flash-tiered',
        'name': 'Gemini 3.8 Flash Tiered',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.7-flash-tiered',
        'name': 'Gemini 3.7 Flash Tiered',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.6-flash-tiered',
        'name': 'Gemini 3.6 Flash Tiered',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.7-flash',
        'name': 'Gemini 3.7 Flash',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.6-flash',
        'name': 'Gemini 3.6 Flash',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.5-flash',
        'name': 'Gemini 3.5 Flash',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'gemini-3.1-pro',
        'name': 'Gemini 3.1 Pro',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'SMART'},
    {   'fav': False,
        'id': 'gemini-3.1-pro-high',
        'name': 'Gemini 3.1 Pro High',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'SMART'},
    {   'fav': True,
        'id': 'claude-opus-4.6',
        'name': 'Claude Opus 4.6',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': False,
        'id': 'claude-sonnet-4.6',
        'name': 'Claude Sonnet 4.6',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': True,
        'id': 'deepseek-v4-pro-v2',
        'name': 'Deepseek V4 Pro V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': False,
        'id': 'deepseek-v4-flash-v2',
        'name': 'Deepseek V4 Flash V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'deepseek-v4.1-flash-v2',
        'name': 'Deepseek V4.1 Flash V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'kimi-k3-v2',
        'name': 'Kimi K3 V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'kimi-k2.7-v2',
        'name': 'Kimi K2.7 V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': True,
        'id': 'minimax-m3-v2',
        'name': 'Minimax M3 V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': False,
        'id': 'glm-5.3-v2',
        'name': 'Glm 5.3 V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'glm-5.3-flash-v2',
        'name': 'Glm 5.3 Flash V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'glm-5.2-v2',
        'name': 'Glm 5.2 V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'deepseek-v3.2',
        'name': 'Deepseek V3.2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'SMART'},
    {   'fav': False,
        'id': 'deepseek-v3.2-volc',
        'name': 'Deepseek V3.2 Volc',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'SMART'},
    {   'fav': False,
        'id': 'deepseek-v3',
        'name': 'Deepseek V3',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'SMART'},
    {   'fav': False,
        'id': 'deepseek-r1',
        'name': 'Deepseek R1',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'REASON'},
    {   'fav': False,
        'id': 'deepseek-v3-0324',
        'name': 'Deepseek V3 0324',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'SMART'},
    {   'fav': False,
        'id': 'glm-5.3-flashx',
        'name': 'Glm 5.3 Flashx',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'FAST'},
    {   'fav': False,
        'id': 'glm-5.0-turbo',
        'name': 'Glm 5.0 Turbo',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'glm-5.1',
        'name': 'Glm 5.1',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'glm-5v-turbo',
        'name': 'Glm 5v Turbo',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': True,
        'id': 'minimax-m2.7',
        'name': 'Minimax M2.7',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': True,
        'id': 'minimax-m3-pay',
        'name': 'Minimax M3 Pay',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': False,
        'id': 'kimi-k3-1',
        'name': 'Kimi K3 1',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'kimi-k3-2',
        'name': 'Kimi K3 2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'kimi-k2.8-preview',
        'name': 'Kimi K2.8 Preview',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'kimi-k2.6',
        'name': 'Kimi K2.6',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'kimi-k2.5',
        'name': 'Kimi K2.5',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {'fav': False, 'id': 'hy3', 'name': 'Hy3', 'provider_id': 'clouvia', 'provider_name': 'Clouvia', 'tag': 'AI'},
    {   'fav': False,
        'id': 'hy3-preview',
        'name': 'Hy3 Preview',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {'fav': False, 'id': 'hy3-x', 'name': 'Hy3 X', 'provider_id': 'clouvia', 'provider_name': 'Clouvia', 'tag': 'AI'},
    {   'fav': False,
        'id': 'hy4-preview',
        'name': 'Hy4 Preview',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'hunyuan-chat',
        'name': 'Hunyuan Chat',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'hunyuan-2.0-instruct',
        'name': 'Hunyuan 2.0 Instruct',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': True,
        'id': 'gpt-6.1-sol',
        'name': 'Gpt 6.1 Sol',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': True,
        'id': 'gpt-6-sol',
        'name': 'Gpt 6 Sol',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': True,
        'id': 'claude-opus-5',
        'name': 'Claude Opus 5',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': True,
        'id': 'gpt-6-luna',
        'name': 'Gpt 6 Luna',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': True,
        'id': 'gpt-6-astra',
        'name': 'Gpt 6 Astra',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': False,
        'id': 'gpt-5.6-sol',
        'name': 'Gpt 5.6 Sol',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'gpt-5.6-terra',
        'name': 'Gpt 5.6 Terra',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'gpt-5.6-luna',
        'name': 'Gpt 5.6 Luna',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'gpt-5.5',
        'name': 'Gpt 5.5',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'gpt-5.4',
        'name': 'Gpt 5.4',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'glm-5.0-turbo-v2',
        'name': 'Glm 5.0 Turbo V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': False,
        'id': 'glm-4.7',
        'name': 'Glm 4.7',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': True,
        'id': 'minimax-m2.7-v2',
        'name': 'Minimax M2.7 V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': False,
        'id': 'hy3-preview-v2',
        'name': 'Hy3 Preview V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'AI'},
    {   'fav': True,
        'id': 'deepseek-v4-pro-v3',
        'name': 'Deepseek V4 Pro V3',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'TOP'},
    {   'fav': False,
        'id': 'deepseek-v3.2-volc-v2',
        'name': 'Deepseek V3.2 Volc V2',
        'provider_id': 'clouvia',
        'provider_name': 'Clouvia',
        'tag': 'SMART'}]

def get_all_available_models():
    models = list(DEFAULT_MODELS_CATALOG)
    full_cfg = load_full_config()
    configured_providers = full_cfg.get("providers", {})
    
    existing_ids = {m["id"] for m in models}
    for prov_id, prov_data in configured_providers.items():
        prov_model = prov_data.get("model")
        if prov_model and prov_model not in existing_ids:
            models.append({
                "name": prov_model,
                "id": prov_model,
                "provider_id": prov_id,
                "provider_name": prov_data.get("name", prov_id),
                "tag": "CUSTOM",
                "fav": False
            })
            existing_ids.add(prov_model)
    return models

def read_key_raw_fd(fd):
    try:
        raw = os.read(fd, 4096)
    except Exception:
        return None
    if not raw:
        return None

    if b'\x1b[200~' in raw:
        raw = raw.replace(b'\x1b[200~', b'').replace(b'\x1b[201~', b'')

    if raw == b'\x1b':
        r, _, _ = select.select([fd], [], [], 0.08)
        if r:
            extra = os.read(fd, 31)
            raw = raw + extra

    if raw in (b'\x1b[A', b'\x1bOA', b'\x1b[1;2A', b'\x1b[1;5A'):
        return 'UP'
    if raw in (b'\x1b[B', b'\x1bOB', b'\x1b[1;2B', b'\x1b[1;5B'):
        return 'DOWN'
    if raw in (b'\x1b[C', b'\x1bOC'):
        return 'RIGHT'
    if raw in (b'\x1b[D', b'\x1bOD'):
        return 'LEFT'
    if raw in (b'\x1b[5~', b'\x1b[V'):
        return 'PAGE_UP'
    if raw in (b'\x1b[6~', b'\x1b[U'):
        return 'PAGE_DOWN'
    if raw in (b'\x1b[Z',):
        return 'SHIFT_TAB'
    if raw == b'\t':
        return 'TAB'
    if raw == b'\x0e':  # Ctrl+N
        return 'DOWN'
    if raw == b'\x10':  # Ctrl+P
        return 'UP'
    if raw in (b'\r', b'\n'):
        return 'ENTER'
    if raw in (b'\x7f', b'\x08'):
        return 'BACKSPACE'
    if raw == b'\x1b':
        return 'ESC'
    if raw == b'\x01':  # Ctrl+A
        return 'CTRL_A'
    if raw == b'\x06':  # Ctrl+F
        return 'CTRL_F'
    if raw == b'\x03':  # Ctrl+C
        return 'CTRL_C'
    if raw == b'\x04':  # Ctrl+D
        return 'CTRL_D'
    if raw == b'\x15':  # Ctrl+U
        return 'CTRL_U'

    try:
        decoded = raw.decode('utf-8', errors='ignore')
        printable_text = ''.join(c for c in decoded if c.isprintable() or c == ' ')
        if printable_text:
            return printable_text
    except Exception:
        pass
    return None

def get_tag_color(tag):
    mapping = {
        "FREE": "\033[1;32m",
        "CODE": "\033[1;36m",
        "FAST": "\033[1;33m",
        "SMART": "\033[1;35m",
        "REASON": "\033[1;34m",
        "TOP": "\033[1;31m",
        "SPEED": "\033[1;33m",
        "LOCAL": "\033[1;37m",
        "CUSTOM": "\033[36m"
    }
    return mapping.get(tag, "\033[37m")

def render_frame_lines(query, filtered_items, selected_idx, scroll_offset, max_visible, width, active_model_id):
    lines = []
    
    # Header bar
    title = "⚡ r.outers Model"
    badge = f"[{len(filtered_items)}]"
    esc_label = "[Esc]"
    
    gap = width - len(title) - len(badge) - len(esc_label) - 2
    if gap < 1: gap = 1
    lines.append(f"\033[1;36m{title}\033[0m{' ' * gap}\033[1;33m{badge}\033[0m \033[90m{esc_label}\033[0m")
    lines.append(f"\033[90m{'─' * width}\033[0m")

    # Search query
    cursor = "\033[1;36m▌\033[0m"
    if query:
        lines.append(f" \033[1;33m🔍\033[0m \033[1;37m{query}\033[0m{cursor}")
    else:
        lines.append(f" \033[1;33m🔍\033[0m \033[90m(ketik nama model / filter...)\033[0m {cursor}")
    
    lines.append(f"\033[90m{'─' * width}\033[0m")

    # Visible items
    visible_slice = filtered_items[scroll_offset:scroll_offset + max_visible]
    for idx_in_slice, item in enumerate(visible_slice):
        actual_idx = scroll_offset + idx_in_slice
        is_selected = (actual_idx == selected_idx)
        is_active = (item.get("id") == active_model_id)
        
        name = item["name"]
        prov = item["provider_name"]
        tag = item.get("tag", "AI")
        tag_col = get_tag_color(tag)

        prefix = "▸ " if is_selected else "  "
        active_mark = " ●" if is_active else ""
        
        left_label = f"{name}{active_mark}"
        
        # Show tag only if terminal is wide enough
        if width >= 46:
            right_label = f"{prov} [{tag}]"
            right_colored = f"{prov} {tag_col}[{tag}]\033[0m"
        else:
            right_label = f"{prov}"
            right_colored = f"{prov}"

        avail_w = width - 2
        # Truncate left if needed
        needed_len = len(prefix) + len(left_label) + len(right_label) + 2
        if needed_len > avail_w:
            max_left = avail_w - len(prefix) - len(right_label) - 3
            if max_left > 4:
                left_label = left_label[:max_left - 1] + ".."
            else:
                left_label = left_label[:max_left]
        
        spacing = avail_w - len(prefix) - len(left_label) - len(right_label)
        if spacing < 1: spacing = 1

        if is_selected:
            # Highlight with distinct high-contrast bar
            content_left = f"{prefix}{left_label}"
            row_full = f"{content_left}{' ' * spacing}{right_label}"
            # Render inverted row
            lines.append(f"\033[7m\033[1m {row_full:<{avail_w}} \033[0m")
        else:
            dim_right = f"\033[90m{right_colored}\033[0m"
            lines.append(f"{prefix}\033[37m{left_label}\033[0m{' ' * spacing}{dim_right}")

    # Empty slots
    remaining = max_visible - len(visible_slice)
    for _ in range(remaining):
        lines.append("")

    # Footer
    lines.append(f"\033[90m{'─' * width}\033[0m")
    if width >= 44:
        footer = " \033[1;33m↑↓/Tab\033[0m \033[90mPilih\033[0m  \033[1;32mEnter\033[0m \033[90mPakai\033[0m  \033[1;35mCtrl+A\033[0m \033[90m+API\033[0m"
    else:
        footer = " \033[1;33m↑↓\033[0m \033[90mPilih\033[0m \033[1;32mEnter\033[0m \033[90mPakai\033[0m \033[1;35m^A\033[0m \033[90m+API\033[0m"
    lines.append(footer)
    
    return lines

def select_model_interactive(current_config):
    if not sys.stdin.isatty():
        return current_config

    models = get_all_available_models()
    query = ""
    selected_idx = 0
    scroll_offset = 0
    filter_favorites = False
    active_model_id = current_config.get("model", "")
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    # Masuk ke Alternate Screen Buffer (\033[?1049h) & sembunyikan cursor (\033[?25l)
    sys.stdout.write("\033[?1049h\033[?25l\033[H\033[2J")
    sys.stdout.flush()

    try:
        tty.setraw(fd)

        # Matikan auto-wrap terminal saat modal tampil untuk menghindari glitch
        sys.stdout.write("\033[?7l")
        sys.stdout.flush()

        while True:
            # Ambil ukuran terminal dinamis per frame
            try:
                term_cols = os.get_terminal_size().columns
                term_lines = os.get_terminal_size().lines
            except Exception:
                term_cols, term_lines = 42, 24

            # Batasi lebar agar pas di layar HP / Termux
            modal_width = max(32, min(term_cols - 2, 54))
            max_visible = max(4, min(term_lines - 8, 14))

            # Filter model
            q_clean = query.strip().lower()
            filtered = []
            for m in models:
                if filter_favorites and not m.get("fav"):
                    continue
                if (not q_clean or 
                    q_clean in m["name"].lower() or 
                    q_clean in m["id"].lower() or 
                    q_clean in m["provider_name"].lower() or 
                    q_clean in m.get("tag", "").lower()):
                    filtered.append(m)

            if not filtered:
                filtered = [{
                    "name": f"Gunakan '{query}'",
                    "id": query if query else "custom",
                    "provider_id": current_config.get("provider_id", "clouvia"),
                    "provider_name": "Custom",
                    "tag": "CUSTOM",
                    "fav": False
                }]

            # Bounds check
            if selected_idx >= len(filtered):
                selected_idx = max(0, len(filtered) - 1)
            if selected_idx < 0:
                selected_idx = 0

            # Scroll offset check
            if selected_idx < scroll_offset:
                scroll_offset = selected_idx
            elif selected_idx >= scroll_offset + max_visible:
                scroll_offset = selected_idx - max_visible + 1

            # Render frame ke alternate screen dari posisi Home (\033[H)
            frame_lines = render_frame_lines(query, filtered, selected_idx, scroll_offset, max_visible, modal_width, active_model_id)
            
            output_buffer = ["\033[H"]
            for line in frame_lines:
                output_buffer.append(f"\r\033[2K{line}\r\n")
            
            # Bersihkan baris di bawahnya jika ada sisa
            output_buffer.append("\r\033[J")
            
            sys.stdout.write("".join(output_buffer))
            sys.stdout.flush()

            # Baca input keyboard via raw fd
            k = read_key_raw_fd(fd)

            if k in ('ESC', 'CTRL_C'):
                break

            elif k in ('UP', 'SHIFT_TAB'):
                if selected_idx > 0:
                    selected_idx -= 1
                else:
                    selected_idx = len(filtered) - 1

            elif k in ('DOWN', 'TAB'):
                if selected_idx < len(filtered) - 1:
                    selected_idx += 1
                else:
                    selected_idx = 0

            elif k == 'PAGE_UP':
                selected_idx = max(0, selected_idx - max_visible)

            elif k == 'PAGE_DOWN':
                selected_idx = min(len(filtered) - 1, selected_idx + max_visible)

            elif k == 'BACKSPACE':
                if query:
                    query = query[:-1]
                    selected_idx = 0
                    scroll_offset = 0

            elif k == 'CTRL_U':
                query = ""
                selected_idx = 0
                scroll_offset = 0

            elif k == 'CTRL_F':
                filter_favorites = not filter_favorites
                selected_idx = 0
                scroll_offset = 0

            elif k == 'CTRL_A':
                # Restore terminal sebelum membuka dialog provider
                sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
                sys.stdout.flush()
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return add_new_provider()

            elif k == 'ENTER':
                chosen = filtered[selected_idx]
                target_model_id = chosen["id"]
                target_prov_id = chosen["provider_id"]

                # Restore terminal
                sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
                sys.stdout.flush()
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

                full_cfg = load_full_config()
                providers = full_cfg.get("providers", {})
                
                if target_prov_id not in providers and target_prov_id in PRESET_PROVIDERS:
                    preset = PRESET_PROVIDERS[target_prov_id]
                    providers[target_prov_id] = {
                        "name": preset["name"],
                        "base_url": preset["base_url"],
                        "api_key": "",
                        "model": target_model_id
                    }

                if target_prov_id in providers:
                    prov_entry = providers[target_prov_id]
                    prov_name = prov_entry.get("name", target_prov_id)
                    existing_api_key = prov_entry.get("api_key", "").strip()
                    
                    # Auto-check dari environment variables
                    if not existing_api_key:
                        from config import load_env_keys
                        env_keys = load_env_keys()
                        if target_prov_id == "atria":
                            existing_api_key = env_keys.get("ATRIA_API_KEY", os.environ.get("ATRIA_API_KEY", "")).strip()
                        elif target_prov_id == "clouvia":
                            existing_api_key = env_keys.get("CLOUVIA_API_KEY", os.environ.get("CLOUVIA_API_KEY", "")).strip()

                    # Jika API Key masih kosong dan bukan clouvia bawaan gratis, minta user input sekali saja
                    if not existing_api_key and target_prov_id != "clouvia":
                        from rich.prompt import Prompt
                        console.print(f"\n[bold yellow]🔑 Provider '{prov_name}' belum memiliki API Key.[/bold yellow]")
                        user_api_key = Prompt.ask("[bold cyan]Masukkan API Key[/bold cyan]").strip()
                        if user_api_key:
                            prov_entry["api_key"] = user_api_key
                            existing_api_key = user_api_key
                            console.print("[bold green]✔ API Key tersimpan! Anda tidak perlu memasukkannya lagi saat ganti model berikutnya.[/bold green]\n")

                    full_cfg["active_provider"] = target_prov_id
                    providers[target_prov_id]["model"] = target_model_id
                    if existing_api_key:
                        providers[target_prov_id]["api_key"] = existing_api_key
                    save_full_config(full_cfg)
                    
                    current_config["provider_id"] = target_prov_id
                    current_config["provider_name"] = prov_name
                    current_config["base_url"] = providers[target_prov_id].get("base_url", "")
                    current_config["api_key"] = existing_api_key
                    current_config["model"] = target_model_id
                else:
                    update_active_model(target_model_id)
                    current_config["model"] = target_model_id

                console.print(f"[bold green]✔ Model aktif:[/bold green] [bold yellow]{chosen['name']}[/bold yellow] ([dim]{chosen['provider_name']}[/dim])")
                return current_config

            elif k and isinstance(k, str) and not k.startswith(('UP', 'DOWN', 'LEFT', 'RIGHT', 'ESC', 'TAB', 'ENTER', 'BACKSPACE', 'CTRL_', 'SHIFT_', 'PAGE_')):
                query += k
                selected_idx = 0
                scroll_offset = 0

    finally:
        # Kembalikan terminal ke keadaan normal
        sys.stdout.write("\033[?7h\033[?1049l\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return current_config
