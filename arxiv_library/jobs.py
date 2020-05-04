import os

import argparse
import logging
import traceback

from multiprocessing import Pool
from tqdm import tqdm

import arxiv_library.compilation.mathml as mathml_compile
from arxiv_library.utils.multiprocessing_logging import install_mp_handler
import arxiv_library.utils.utils as h
import arxiv_library.jobs.config as c


def extract_from_equation_file(formula_file):
    """Extract formulas, important packages and macros from tex-sources.
        Then compile pngs of the formulas."""

    formula_file = os.path.join(c.JSON_LOCATION, formula_file)
    try:
        mathml_compile.compile_eqs_in_paper(formula_file)
    except Exception:
        logging.warning(traceback.format_exc() + "in file %s", formula_file)

def main():
    """Main job"""
    parser = argparse.ArgumentParser(description='Extract formulas from arxiv tar archive')
    parser.add_argument("--partition", type=int, default=1)
    parser.add_argument("--total_partitions", type=int, default=1)
    args = parser.parse_args()

    log_file = "mathml-extraction{}-{}.log".format(args.partition, args.total_partitions)
    logging.basicConfig(filename=log_file, level=logging.WARNING, format='%(levelname)s at %(asctime)s: %(message)s')
    install_mp_handler()

    h.assure_dir_exists(c.JSON_LOCATION)
    full_workload = os.listdir(c.JSON_LOCATION)
    workload = full_workload[args.partition-1::args.total_partitions]
    with Pool(c.NUM_WORKERS) as pool:
        results = pool.imap(extract_from_equation_file, workload)
        results = list(tqdm(results))

if __name__ == '__main__':
    main()

import io_pkg.path_config as path_config
from io_pkg.targz import extract_arxiv_month
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


from io_pkg.targz import extract_arxiv_month
import argparse
from datetime import datetime as dt
import json

from io_pkg.targz import extract_arxiv_month
import argparse
from datetime import datetime as dt
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the tar that you want to extract")
    parser.add_argument("--tmp_dir", default="tar_tmp", help="A directory where the tar can temporarily be extracted")
    args = parser.parse_args()
    start = dt.now()
    file_dicts = extract_arxiv_month(args.path, args.tmp_dir)

    print(json.dumps(file_dicts))
    end = dt.now()
    diff = end - start
    print("Time needed: ", diff.total_seconds())

