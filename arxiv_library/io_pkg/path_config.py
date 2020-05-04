import json
import os


configuarable_paths = ["json_location", "tar_location", "tmp_tar"]

config_json_path = "path_config.json"


def set_path(path_id, actual_path):
    if path_id not in configuarable_paths:
        raise ValueError("You may only configure the following paths: " + " ".join(configuarable_paths))

    config_dict = None
    if os.path.isfile(config_json_path):
        with open(config_json_path) as f:
            config_dict = json.load(f)
    else:
        config_dict = {}

    config_dict[path_id] = actual_path

    with open(config_json_path, "w") as f:
        json.dump(config_dict, f, indent=4, sort_keys=True)


def get_path(path_id):
    if path_id not in configuarable_paths:
        raise ValueError("The configuration can only contain the following paths: " + " ".join(configuarable_paths))
    if not os.path.isfile(config_json_path):
        raise FileNotFoundError("There is no json file for the path configuration yet. Create one by using the set_path function of this module.")
    with open(config_json_path) as f:
        config_dict = json.load(f)
        if path_id not in config_dict:
            raise ValueError("The configuration for the requested path is not set yet. You can set it by using the set_path function of this module.")
        return config_dict[path_id]
