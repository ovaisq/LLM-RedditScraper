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
        for section_name, options in config_obj.items():
            for option_name, option_value in options.items():
                config_dict[option_name] = option_value
        return config_dict
    print(f'{CONFIG_FILE} file not found. Assuming ENV VARS are set up using some other method')

def get_config():
    """Returns the parsed configuration object"""
    return read_config(CONFIG_FILE)

def get_ver():
    with open('ver.txt', 'r') as file:
        content = file.read()
    return content.strip()

def create_docker_client(engine, remote_host=None, remote_port=22):
    """Create Docker client for local or remote engine"""
    if engine == "remote":
        if not remote_host:
            raise ValueError("remote_host must be specified when engine is 'remote'")
        docker_host_str = f"ssh://{remote_host}:{remote_port}"
        print(f"Connecting to remote Docker engine at {docker_host_str}")
        client = docker.DockerClient(base_url=docker_host_str)
    else:
        print("Connecting to local Docker engine")
        client = docker.from_env()
    return client

def build_docker_container(client, dockerfile_path, image_name, tag="latest", build_args=None):
    """Build docker container"""
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
        get_this_image = client.images.get(f"{image_name}:{tag}")
        get_this_image.tag(f"{image_name}:latest")

    except docker.errors.BuildError as e:
        print(f"Failed to build Docker image {image_name}:{tag}: {e}")

    except docker.errors.APIError as e:
        print(f"Docker API error while building image {image_name}:{tag}: {e}")

if __name__ == "__main__":
    dockerfile_path = str(Path().absolute())
    image_name = "rollama"
    tag = get_ver()
    build_args = get_config()

    # === Engine selection ===
    # Set these values as needed:
    engine = "remote"  # or "local"
    remote_host = "<user>@<ip-or-fqdn>"  # e.g. ec2-user@1.2.3.4
    remote_port = 22  # default SSH port, change if needed

    client = create_docker_client(engine, remote_host, remote_port)
    build_docker_container(client, dockerfile_path, image_name, tag, build_args)

