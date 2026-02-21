import yaml
import os
from pathlib import Path

def load_config():
    # Priority: ENV check -> Local file
    config_path = os.getenv("CONFIG_PATH", "config/settings.yaml")
    
    if not Path(config_path).exists():
        # Fallback for local development if running from subdirectories
        config_path = "../config/settings.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

# Load once as a singleton-like object
settings = load_config()
