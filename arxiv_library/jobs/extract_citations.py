"""Process the Arxiv Dumps"""
import os
import argparse
import logging
import traceback
from multiprocessing import Pool

from tqdm import tqdm
import arxiv_library.preprocessing.preprocessing as preprocessing
import arxiv_library.preprocessing.citation_parser as citation_parser
import arxiv_library.utils.utils as h
from arxiv_library.utils.tempfs import write_tmpfs_to_disk, check_tempfs_status
from arxiv_library.utils.multiprocessing_logging import install_mp_handler

import arxiv_library.jobs.config as c


def extract_gzs(tar_archive):
    """Extract all gz archives and rm comments in tex-sources"""
    for gzip, name in preprocessing.iterate_tar(tar_archive):
        preprocessing.extract_gz(gzip, name)


def extract_from_arxiv_dir(arxiv_dir):
    """Extract formulas, important packages and macros from tex-sources.
    Then compile pngs of the formulas."""

    #critical section start
    check_tempfs_status(citations=True)
    #critical section end

    try:
        arxiv_dir = os.path.join(c.TEX_LOCATION, arxiv_dir)
        main_file = preprocessing.find_main(arxiv_dir)

        if main_file is None:
            return

        resolved = preprocessing.resolve(main_file, arxiv_dir, arxiv_dir)
        citations = citation_parser.parse(resolved)
        if citations:
            output_file_path = os.path.join(c.CITATION_LOCATION, os.path.basename(arxiv_dir) + ".cite")
            with open(output_file_path, 'w') as output_file:
                for cite in citations:
                    output_file.write(cite+"\n")
    except Exception:
        logging.warning(traceback.format_exc() + "in file {}".format(main_file))

def main():
    """main job"""
    parser = argparse.ArgumentParser(description='Extract formulas from arxiv tar archive')
    # Number of the run
    parser.add_argument('no', type=int)
    args = parser.parse_args()
    log_file = "routine" + str(args.no) + ".log"
    logging.basicConfig(filename=log_file, level=logging.WARNING)
    h.assure_dir_exists(c.FORMULA_LOCATION)
    h.assure_dir_exists(c.CITATION_LOCATION)
    h.assure_dir_exists(c.PNG_LOCATION)
    h.assure_dir_exists(c.TEX_LOCATION)
    install_mp_handler()
    with Pool(c.NUM_WORKERS) as pool:
        results = pool.imap(extract_from_arxiv_dir, os.listdir(c.TEX_LOCATION))
        results = list(tqdm(results))
    write_tmpfs_to_disk(citations=True)


if __name__ == '__main__':
    main()
