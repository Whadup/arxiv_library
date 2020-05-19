import ray
import json
import os
import logging
import argparse
import psutil
import tqdm
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

        except io_pkg.targz.EmptyFileDictException as exception:
            logging.debug(exception)

        except Exception as exception:
            logging.warning(exception)

    return processed


@ray.remote(num_cpus=1)
def _pipeline(file_dicts, json_dir, fulltext):
    paper_dicts = []

    for file_dict in file_dicts:
        try:
            file_dict = preprocessing.comments.remove_comments(file_dict)
            paper_dict = preprocessing.imports.resolve_imports(file_dict)

            paper_dict = extraction.preamble.extract_preamble(paper_dict)
            paper_dict = extraction.sections.extract_sections(paper_dict)
            paper_dict = extraction.equations.extract_equations(paper_dict)
            paper_dict = extraction.citations.extract_citations(paper_dict)

            if not fulltext:
                for section in paper_dict['sections']:
                    del section['latex']
                del paper_dict['paper']

            paper_dict = compilation.mathml.compile_paper(paper_dict, paper_dict['arxiv_id'])
            paper_dicts.append(paper_dict)

        except preprocessing.imports.NoMainFileException as exception:
            logging.debug(exception)

        except Exception as exception:
            logging.warning(exception)

    try:
        paper_dicts = io_pkg.metadata.receive_meta_data(paper_dicts)

        for paper_dict in paper_dicts:
            with open(os.path.join(json_dir, '{}.json'.format(paper_dict['arxiv_id'])), 'w') as file:
                json.dump(paper_dict, file, indent=4)

    except Exception as exception:
        logging.warning(exception)


def pipeline(tar_dir, json_dir, fulltext=False):
    ray.init(log_to_driver=True)
    tar_paths = os.listdir(tar_dir)
    total_papers = 0

    with tqdm.tqdm(total=len(tar_paths), desc='0 papers in total | tar progress') as progress:
        for tar_path in (os.path.join(tar_dir, p) for p in tar_paths):
            targzs = io_pkg.targz.process_tar(tar_path)
            chunk_size = max(len(targzs) // (psutil.cpu_count()), 1)

            remaining_chunk_ids = []

            for chunk in (targzs[i:i + chunk_size] for i in range(0, len(targzs), chunk_size)):
                remaining_chunk_ids.append(_extract.remote(chunk))

            pipeline_ids = []

            while remaining_chunk_ids:
                ready_chunk_ids, remaining_chunk_ids = ray.wait(remaining_chunk_ids, num_returns=1)

                for chunk_id in ready_chunk_ids:
                    pipeline_ids.append(_pipeline.remote(chunk_id, json_dir, fulltext))
                    total_papers += chunk_size
                    progress.set_description_str('{} papers in total | tar progress'.format(total_papers))

            ray.wait(pipeline_ids, num_returns=len(pipeline_ids))
            progress.update(1)

    ray.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')  # TODO description

    parser.add_argument(
        'tar_path',
        help='the folder where the tar files are located',
        type=str)
    parser.add_argument(
        'json_path',
        help='the folder where the results will be stored',
        type=str)
    parser.add_argument(
        '-fulltext',
        help='iff flag is set, the paper will be stored in the paperdict with key "paper"',
        action='store_true')

    args = parser.parse_args()
    pipeline(args.tar_path, args.json_path, args.fulltext)
