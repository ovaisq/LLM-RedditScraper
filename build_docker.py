#!/usr/bin/env python3
"""Build docker image
    less BASH more Python

    ©2024, Ovais Quraishi
"""

import configparser
import docker
from pathlib import Path

# override option transformation to preserve case
class CaseSensitiveConfigParser(configparser.RawConfigParser):
    def optionxform(self, optionstr):
            return optionstr  

CONFIG_FILE = 'setup.config'

def read_config(file_path):
    """Read setup config file"""

    config_dict = {}

    if Path(str(Path(file_path).resolve())).exists():
        config_obj = CaseSensitiveConfigParser()
        config_obj.read(file_path)
        # Loop through each section in the config file
        for section_name, options in config_obj.items():
            # Loop through each option in the current section
            for option_name, option_value in options.items():
                # Set an environment variable with the option name and value
                config_dict[option_name] = option_value
        return config_dict
    print (f'{CONFIG_FILE} file not found. Assuming ENV VARS are set up using some other method')

def get_config():
    """Returns the parsed configuration object"""
    return read_config(CONFIG_FILE)

def get_ver():
    with open('ver.txt', 'r') as file:
        content = file.read()
    return content.strip()

def build_docker_container(dockerfile_path, image_name, tag="latest", build_args=None):
    """Build docker container
    """

    client = docker.from_env()
    try:
        print(f"Building Docker image {image_name}:{tag} from {dockerfile_path}...")
        _, logs = client.images.build(
            path=dockerfile_path,
            tag=f"{image_name}:{tag}",
            rm=True,
            buildargs=build_args,
            quiet=True
        )

        for log in logs:
            if 'stream' in log:
                print(log['stream'].strip())

        print(f"Docker image {image_name}:{tag} built successfully!")

    except docker.errors.BuildError as e:
        print(f"Failed to build Docker image {image_name}:{tag}: {e}")

    except docker.errors.APIError as e:
        print(f"Docker API error while building image {image_name}:{tag}: {e}")

if __name__ == "__main__":
    dockerfile_path = str(Path().absolute())
    image_name = "rollama"
    tag = get_ver()

    build_docker_container(dockerfile_path, image_name, tag, get_config())
