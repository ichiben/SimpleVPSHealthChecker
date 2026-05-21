import yaml
import os
from pathlib import Path

CONFIG_FILE = "config.yaml"

DEFAULT_CONFIG = {
    "telegram_token": "",
    "telegram_chat_id": "",
    "log_file": "vps_health.log",
    "targets": [] # List of dicts: {hostname, port, check_interval, max_retries}
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG.copy())
        return DEFAULT_CONFIG.copy()
    
    with open(CONFIG_FILE, 'r') as f:
        try:
            config = yaml.safe_load(f)
            if not isinstance(config, dict):
                return DEFAULT_CONFIG.copy()
            # Ensure default keys exist if missing
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
        except yaml.YAMLError:
            return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f, default_flow_style=False)
    try:
        if os.name != "nt":
            os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass

def add_target(hostname, port, check_interval, max_retries):
    config = load_config()
    target = {
        "hostname": hostname,
        "port": port,
        "check_interval": check_interval,
        "max_retries": max_retries
    }
    config['targets'].append(target)
    save_config(config)

def remove_target(index):
    config = load_config()
    if 0 <= index < len(config['targets']):
        del config['targets'][index]
        save_config(config)

def update_telegram_settings(token, chat_id):
    config = load_config()
    config['telegram_token'] = token
    config['telegram_chat_id'] = chat_id
    save_config(config)
