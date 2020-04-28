"""Main Job for compiling latex-equations from the json files to mathml-equations that are then
also stored in the respective json-files. """
import os

import argparse
import logging
import traceback
import json

from multiprocessing import Pool
from tqdm import tqdm

import arxiv_library.jobs.compilation.mathml_compile as mathml_compile
from arxiv_library.io.multiprocessing_logging import install_mp_handler
import arxiv_library.utils.utils as h
import arxiv_library.jobs.config as c


def extract_from_equation_file(formula_file):
    """Extract formulas, important packages and macros from tex-sources.
        Then compile pngs of the formulas."""

    formula_file = os.path.join(c.JSON_LOCATION, formula_file)
    try:
        with open(formula_file, 'r') as f:
            paper_dict = json.load(f)
            paper_id = os.path.basename(formula_file).replace(".json", "")
            paper_dict = mathml_compile.compile_paper(paper_dict, paper_id=paper_id)
        with open(formula_file, "w") as f:
            json.dump(paper_dict, f, indent=4, sort_keys=True)
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
