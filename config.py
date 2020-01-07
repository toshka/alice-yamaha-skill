import os

import yaml

home_directory = os.getenv("HOME")
config_filename = f"{home_directory}/.alice-yamaha-skill.yml"

yaml_config = {}

if os.path.exists(config_filename):
    with open(config_filename) as yaml_file:
        yaml_config = yaml.load(yaml_file.read(), Loader=yaml.FullLoader)


# TODO: yaml config checker is needed

YAMAHA_INPUT_MAP = yaml_config.get("input_map", {})

USERS = yaml_config.get("users", [])
