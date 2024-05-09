# config.py
# ©2024, Ovais Quraishi
"""Load setup.config content
"""

import configparser
import os
from pathlib import Path

# override option transformation to preserve case
class CaseSensitiveConfigParser(configparser.RawConfigParser):
    def optionxform(self, optionstr):
                return optionstr

CONFIG_FILE = 'setup.config'

def read_config(file_path):
    """Read setup config file"""
    if Path(str(Path(file_path).resolve())).exists():
        config_obj = CaseSensitiveConfigParser()
        config_obj.read(file_path)
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
