import io_pkg.path_config as path_config
from io_pkg.archive_extraction import extract_arxiv_month
import json
from tqdm import tqdm
import os

if __name__ == "__main__":
    tar_location = path_config.get_path("tar_location")
    file_dict_location = path_config.get_path("file_dict_location")
    for arxiv_month in tqdm(os.listdir(tar_location)):
        arxiv_month_path = os.path.join(tar_location, arxiv_month)
        file_dicts = extract_arxiv_month(arxiv_month_path)
        file_dicts_out_path = os.path.join(file_dict_location, arxiv_month.replace(".tar", ".json"))
        with open(file_dicts_out_path, 'w') as f:
            json.dump(file_dicts, f)
