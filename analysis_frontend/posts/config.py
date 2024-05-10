# config.py
# ©2024, Ovais Quraishi
"""Load setup.config content
"""

import configparser
import os
from pathlib import Path
from django.apps import apps

# override option transformation to preserve case
class CaseSensitiveConfigParser(configparser.RawConfigParser):
    def optionxform(self, optionstr):
                return optionstr

APP_DIR = apps.get_app_config('posts').path
CONFIG_FILE = 'setup.config'

def read_config(file_path):
    """Read setup config file"""

    config_path = Path(APP_DIR) / file_path

    if config_path.exists():
        config_obj = CaseSensitiveConfigParser()
        config_obj.read(config_path)
        # Loop through each section in the config file
        for section_name, options in config_obj.items():
            # Loop through each option in the current section
            for option_name, option_value in options.items():
                # Set an environment variable with the option name and value
                os.environ[option_name] = option_value
        return config_obj
    print (f'{CONFIG_FILE} file not found. Assuming ENV VARS are set up using some other method')

def get_config():
    """Returns the parsed configuration object"""
    return read_config(CONFIG_FILE)
