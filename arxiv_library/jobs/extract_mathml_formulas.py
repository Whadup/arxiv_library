"""Main Job for compiling latex-equations from the json files to mathml-equations that are then
also stored in the respective json-files. """
import os

import argparse
import logging
import traceback

from multiprocessing import Pool
from tqdm import tqdm

import arxiv_lib.mathml_compile as mathml_compile
import arxiv_lib.preprocessing as preprocessing
import arxiv_lib.formula_parser as formula_parser
from arxiv_lib.multiprocessing_logging import install_mp_handler
from arxiv_lib.tempfs import check_tempfs_status, write_tmpfs_to_disk
import arxiv_lib.helpers as h
import config as c


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
