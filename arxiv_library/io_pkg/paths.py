import json
import os


configuarable_paths = ["json_location", "tar_location",  "file_dict_location", "log_path"]

config_json_path = "io_pkg/path_config.json"

# After first call of get_path we store the dict here, so that we dont need IO for every following cool. This variable
# is reset to None if set_path is called.
cached = None


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

    cached = None


def get_path(path_id):
    global cached
    if path_id not in configuarable_paths:
        raise ValueError("The configuration can only contain the following paths: " + " ".join(configuarable_paths))
    if not os.path.isfile(config_json_path):
        raise FileNotFoundError("There is no json file for the path configuration yet. Create one by using the set_path function of this module.")

    if cached:
        if path_id not in cached:
            raise ValueError("The configuration for the requested path is not set yet. You can set it by using the set_path function of this module.")
        return cached[path_id]
    else:
        with open(config_json_path) as f:
            config_dict = json.load(f)
            if path_id not in config_dict:
                raise ValueError("The configuration for the requested path is not set yet. You can set it by using the set_path function of this module.")
            cached = config_dict
            return config_dict[path_id]
