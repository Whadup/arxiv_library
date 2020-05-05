import ray
import json
import os
import io_pkg.targz
import io_pkg.metadata
import io_pkg.paths
import preprocessing.comments
import preprocessing.imports
import extraction.preamble
import extraction.sections
import extraction.equations
import extraction.citations
import compilation.mathml
from multiprocessing import Queue


_file_dict_queue = Queue()
_paper_dict_queue = Queue()


@ray.remote
def _extract(tar_path):
    try:
        return io_pkg.targz.extract_arxiv_month(tar_path)

    except Exception as exception:
        pass  # log exception


@ray.remote
def _pipe(file_dict):
    try:
        file_dict = preprocessing.comments.remove_comments(file_dict)
        paper_dict = preprocessing.imports.resolve_imports(file_dict)

        paper_dict = extraction.preamble.extract_preamble(paper_dict)
        paper_dict = extraction.sections.extract_sections(paper_dict)
        paper_dict = extraction.equations.extract_equations(paper_dict)
        paper_dict = extraction.citations.extract_citations(paper_dict)

        return paper_dict

    except Exception as exception:
        pass  # log exception


@ray.remote
def _compile(paper_dict):
    try:



@ray.remote
def _save(paper_dict, json_dir):
    try:
        with open(os.path.join(json_dir, '{}.json'.format(paper_dict['arxiv_id'])), 'w') as file:
            json.dump(paper_dict, file)

    except Exception as exception:
        pass  # log exception


def pipeline(tar_dir, json_dir):
    ray.init()

    while True:
        ready_file_dict_ids, remaining_file_dict_ids = ray.wait(file_dict_ids, num_returns=32)

        paper_dict_ids = [_pipe.remote(file_dict_id) for file_dict_id in ready_file_dict_ids]

        ready_paper_dict_ids, remaining_paper_dict_ids =


        if not remaining_file_dict_ids:
            break

    ray.shutdown()
