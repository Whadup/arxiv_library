import ray
import json
import os
import logging
import traceback
import psutil
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
def _extract(targzs):
    processed = []

    for gz in targzs:
        try:
            processed.append(io_pkg.targz.process_gz(gz))

        except Exception as exception:
            logging.warning(exception)

    return processed


def pipeline(tar_dir, json_dir):
    ray.init(num_cpus=1)

    tar_paths = os.listdir(tar_dir)
    file_dict_chunk_ids = []
    cache = []

    for tar_path in (os.path.join(tar_dir, p) for p in tar_paths):
        targzs = list(io_pkg.targz.process_tar(tar_path))
        chunk_size = len(targzs) // psutil.cpu_count()

        for chunk in (targzs[i:i + chunk_size] for i in range(0, len(targzs), chunk_size)):
            file_dict_chunk_ids.append(_extract.remote(chunk))

    remaining_chunk_ids = True

    while remaining_chunk_ids:
        ready_chunk_ids, remaining_chunk_ids = ray.wait(file_dict_chunk_ids, num_returns=1)

        for file_dict in (fd for chunk_id in ready_chunk_ids for fd in ray.get(chunk_id)):
            try:
                file_dict = preprocessing.comments.remove_comments(file_dict)
                paper_dict = preprocessing.imports.resolve_imports(file_dict)

                paper_dict = extraction.preamble.extract_preamble(paper_dict)
                paper_dict = extraction.sections.extract_sections(paper_dict)
                paper_dict = extraction.equations.extract_equations(paper_dict)
                paper_dict = extraction.citations.extract_citations(paper_dict)

                paper_dict = compilation.mathml.compile_paper(paper_dict, paper_dict['arxiv_id'])

                cache.append(paper_dict)

                print(len(cache))

                if len(cache) > 100 or not remaining_chunk_ids:
                    paper_dicts = io_pkg.metadata.receive_meta_data(cache)

                    # for pd in paper_dicts:
                    #     _save.remote(pd, json_dir)

                    for pd in paper_dicts:
                        with open(os.path.join(json_dir, '{}.json'.format(pd['arxiv_id'])), 'w') as file:
                            json.dump(pd, file, indent=4)

            except Exception as exception:
                logging.warning(exception)

    ray.shutdown()
