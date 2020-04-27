"""Main Job for identifying all equations and storing them in a nicely structured json file."""
import os
import json
import argparse
import logging
import traceback
from multiprocessing import Pool

import arxiv_library.preprocessing.preprocessing as preprocessing
import arxiv_library.jobs.config as c
import arxiv_library.preprocessing.env_parser as env_parser
import arxiv_library.utils.utils as h
from arxiv_library.utils.multiprocessing_logging import install_mp_handler



def extract_gzs(tar_archive):
    """Extract all gz archives and rm comments in tex-sources"""
    for gzip, name in preprocessing.iterate_tar(tar_archive):
        preprocessing.extract_gz(gzip, name)


def extract_from_arxiv_dir(arxiv_dir, overwrite=False, test_indir=None, test_outdir=None):
    """Extract formulas, important packages and macros from tex-sources.
    Then compile pngs of the formulas."""
    paper_id = arxiv_dir
    try:
        if test_indir:
            test_indir = os.path.abspath(test_indir)
            arxiv_dir = os.path.join(test_indir, arxiv_dir)
        else:
            arxiv_dir = os.path.join(c.TEX_LOCATION, arxiv_dir)

        main_file = preprocessing.find_main(arxiv_dir)

        if main_file is None:
            return False

        resolved = preprocessing.resolve(main_file, arxiv_dir, arxiv_dir)
        preamble = preprocessing.extract_preamble(resolved)
        sections = preprocessing.sectionize(resolved)
        if test_outdir:
            output_file_path = os.path.join(test_outdir, os.path.basename(arxiv_dir) + ".json")
        else:
            output_file_path = os.path.join(c.JSON_LOCATION, os.path.basename(arxiv_dir) + ".json")

        # Check if there is already a file for this paper.
        # If so do only proceed when the respective file has entries for "preamble" and "equations"
        # and the overwrite option is set to true
        if os.path.isfile(output_file_path) and not overwrite:
            with open(output_file_path, "r") as f:
                stored_dict = json.load(f)
                stored_equations = stored_dict["equations"]
                stored_preamble = stored_dict["preamble"]
                if stored_equations is None and stored_preamble is None:
                    logging.info("The file {} already exists with the respective entries. Overwrite option is off. Skipping...".format(output_file_path))
                    return False

        # count all extracted in this paper. Counter is NOT reset for every section.
        formula_counter = 0

        formulas = []
        for section_name, section_content in sections.items():

            section_eqs = {
                'section_name': section_name,
                'equations': []
            }

            eqs = list(env_parser.extract_envs(section_content))
            for eq in eqs:
                # rm newlines and carriage returns
                eq = eq.replace('\n', ' ').replace('\r', '')

                formula_item = {
                    'no': formula_counter,
                    'latex': eq
                }
                section_eqs['equations'].append(formula_item)
                formula_counter += 1

            if len(eqs) > 0:
                formulas.append(section_eqs)

        # the file is not needed if no equations were extracted
        if formula_counter > 0:
            paper_dict = {
                'preamble': preamble,
                'sections': formulas
            }
            with open(output_file_path, "w") as f:
                json.dump(paper_dict, f, indent=4, sort_keys=True)

    except Exception:
        logging.warning("Exception for paper {} in file {}:\n\t".format(paper_id, main_file) + traceback.format_exc())

def main():
    """Main job"""
    parser = argparse.ArgumentParser(description='Extract formulas from arxiv tar archive')
    parser.add_argument("--partition", type=int, default=1)
    parser.add_argument("--total_partitions", type=int, default=1)
    args = parser.parse_args()

    log_file = "latex-extraction{}-{}.log".format(args.partition, args.total_partitions)
    logging.basicConfig(filename=log_file, level=logging.WARNING, format='%(levelname)s at %(asctime)s: %(message)s')
    install_mp_handler()

    h.assure_dir_exists(c.TEX_LOCATION)
    h.assure_dir_exists(c.JSON_LOCATION)
    full_workload = os.listdir(c.TEX_LOCATION)
    workload = full_workload[args.partition-1::args.total_partitions]
    with Pool(c.NUM_WORKERS) as pool:
        results = pool.imap(extract_from_arxiv_dir, workload)
        results = list(results)

if __name__ == '__main__':
    main()
