import ray
import json
import os
import logging
import traceback
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


@ray.remote
def _extract(targz):
    try:
        return io_pkg.targz.process_gz(targz)

    except Exception as exception:
        logging.warning(exception)


@ray.remote
def _save(paper_dict, json_dir):
    try:
        with open(os.path.join(json_dir, '{}.json'.format(paper_dict['arxiv_id'])), 'w') as file:
            json.dump(paper_dict, file, indent=4)

    except Exception as exception:
        logging.warning(exception)


def pipeline(tar_dir, json_dir):
    ray.init()

    tar_paths = os.listdir(tar_dir)
    file_dict_ids = []
    cache = []

    for tar_path in (os.path.join(tar_dir, p) for p in tar_paths):
        for targz in io_pkg.targz.process_tar(tar_path):
            file_dict_ids.append(_extract.remote(targz))

    remaining_file_dict_ids = True

    while remaining_file_dict_ids:
        ready_file_dict_ids, remaining_file_dict_ids = ray.wait(file_dict_ids, num_returns=1)

        for file_dict_id in ready_file_dict_ids:
            try:
                file_dict = ray.get(file_dict_id)

                file_dict = preprocessing.comments.remove_comments(file_dict)
                paper_dict = preprocessing.imports.resolve_imports(file_dict)

                paper_dict = extraction.preamble.extract_preamble(paper_dict)
                paper_dict = extraction.sections.extract_sections(paper_dict)
                paper_dict = extraction.equations.extract_equations(paper_dict)
                paper_dict = extraction.citations.extract_citations(paper_dict)

                paper_dict = compilation.mathml.compile_paper(paper_dict, paper_dict['arxiv_id'])

                cache.append(paper_dict)

                if len(cache) > 100 or not remaining_file_dict_ids:
                    paper_dicts = io_pkg.metadata.receive_meta_data(cache)

                    for pd in paper_dicts:
                        _save.remote(pd, json_dir)

            except Exception as exception:
                logging.warning(exception)

    ray.shutdown()
