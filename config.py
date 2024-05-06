# config.py
# ©2024, Ovais Quraishi
"""Load setup.config content
"""

import configparser
from pathlib import Path

CONFIG_FILE = '/etc/rollama/setup.config'

def read_config(file_path):
    """Read setup config file"""
    if Path(str(Path(file_path).resolve())).exists():
        config_obj = configparser.RawConfigParser()
        config_obj.read(file_path)
        return config_obj
    raise FileNotFoundError(f"Config file {file_path} not found.")

def get_config():
    """Returns the parsed configuration object"""
    return read_config(CONFIG_FILE)
