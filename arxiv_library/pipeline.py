import ray
import json
import os
import logging
import traceback
import argparse
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


@ray.remote(num_cpus=1)
def _extract(targzs):
    processed = []

    for gz in targzs:
        try:
            processed.append(io_pkg.targz.process_gz(gz))

        except Exception as exception:
            logging.warning(exception)

    return processed


@ray.remote(num_cpus=1)
def _pipeline(file_dicts, json_dir):
    paper_dicts = []

    for file_dict in file_dicts:
        try:
            file_dict = preprocessing.comments.remove_comments(file_dict)
            paper_dict = preprocessing.imports.resolve_imports(file_dict)

            paper_dict = extraction.preamble.extract_preamble(paper_dict)
            paper_dict = extraction.sections.extract_sections(paper_dict)
            paper_dict = extraction.equations.extract_equations(paper_dict)
            paper_dict = extraction.citations.extract_citations(paper_dict)

            paper_dict = compilation.mathml.compile_paper(paper_dict, paper_dict['arxiv_id'])

            paper_dicts.append(paper_dict)

        except Exception as exception:
            logging.warning(exception)

    try:
        paper_dicts = io_pkg.metadata.receive_meta_data(paper_dicts)

        for paper_dict in paper_dicts:
            with open(os.path.join(json_dir, '{}.json'.format(paper_dict['arxiv_id'])), 'w') as file:
                json.dump(paper_dict, file, indent=4)

    except Exception as exception:
        logging.warning(exception)


def pipeline(tar_dir, json_dir):
    ray.init(log_to_driver=False)
    tar_paths = os.listdir(tar_dir)

    for tar_path in (os.path.join(tar_dir, p) for p in tar_paths):
        targzs = io_pkg.targz.process_tar(tar_path)
        chunk_size = len(targzs) // (psutil.cpu_count() // 2)  # TODO evlt andere ausprobieren? scheint aber gut

        remaining_chunk_ids = []

        for chunk in (targzs[i:i + chunk_size] for i in range(0, len(targzs), chunk_size)):
            remaining_chunk_ids.append(_extract.remote(chunk))

        pipeline_ids = []

        while remaining_chunk_ids:
            ready_chunk_ids, remaining_chunk_ids = ray.wait(remaining_chunk_ids, num_returns=1)

            for chunk_id in ready_chunk_ids:
                pipeline_ids.append(_pipeline.remote(chunk_id, json_dir))

        ray.wait(pipeline_ids, num_returns=len(pipeline_ids))

    ray.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')  # TODO description

    parser.add_argument('tar-path', help='the folder where the tar files are located', type=str)
    parser.add_argument('json-path', help='the folder where the results will be stored', type=str)

    args = parser.parse_args()
    pipeline(args.tar_path, args.json_path)
