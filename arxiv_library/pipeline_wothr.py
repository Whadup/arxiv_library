import ray
import json
import os
import logging
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
def _extract(tar_path):
    try:
        return io_pkg.targz.gz_to_file_dict(tar_path)

    except Exception as exception:
        logging.warning(exception)


@ray.remote
def _save(paper_dict_id, json_dir):
    try:
        paper_dict = ray.get(paper_dict_id)

        with open(os.path.join(json_dir, '{}.json'.format(paper_dict['arxiv_id'])), 'w') as file:
            json.dump(paper_dict, file)

    except Exception as exception:
        logging.warning(exception)


def pipeline(tar_dir, json_dir):
    ray.init()

    tar_paths = os.listdir(tar_dir)
    file_dict_ids = []

    for tar_path in tar_paths:
        with io_pkg.targz.TarMonthExtractor(tar_path) as targz_paths:
            for path in targz_paths:
                file_dict_ids.append(_extract.remote(path))

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

                paper_dict = compilation.mathml.compile_equations(paper_dict)
                paper_dict = io_pkg.metadata.recieve_meta_data([paper_dict['arxiv_id']])

                _save.remote(paper_dict, json_dir)

            except Exception as exception:
                logging.warning(exception)

    ray.shutdown()
