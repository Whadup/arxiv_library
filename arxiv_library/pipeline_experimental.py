import ray
import json
import os
import threading
import queue
import logging
import arxiv_library.io_pkg.targz as io_targz
import arxiv_library.io_pkg.metadata as io_metadata
import arxiv_library.extraction.comments as comments
import arxiv_library.extraction.imports as imports
import arxiv_library.extraction.preamble as preamble
import arxiv_library.extraction.sections as sections
import arxiv_library.extraction.equations as equations
import arxiv_library.extraction.citations as citations
import arxiv_library.compilation.mathml as mathml


_pipeline_input_queue = queue.Queue(maxsize=200)
_saving_input_queue = queue.Queue(maxsize=200)

_extraction_finished = threading.Event()
_pipeline_finished = threading.Event()


@ray.remote
def _extraction_process(targz):
    try:
        return targz.process_gz(targz)
    except targz.EmptyFileDictException as exception:
        logging.debug(exception)
    except Exception as exception:
        logging.warning(exception)


@ray.remote
def _pipeline_process(file_dict_id):
    try:
        file_dict = comments.remove_comments(file_dict_id)
        paper_dict = imports.resolve_imports(file_dict)

        paper_dict = preamble.extract_preamble(paper_dict)
        paper_dict = sections.extract_sections(paper_dict)
        paper_dict = equations.extract_equations(paper_dict)
        paper_dict = citations.extract_citations(paper_dict)

        paper_dict = mathml.compile_paper(paper_dict, paper_dict['arxiv_id'])

        return paper_dict
    except imports.NoMainFileException as exception:
        logging.debug(exception)
    except Exception as exception:
        logging.warning(exception)


@ray.remote
def _saving_process(paper_dict, json_dir):
    try:
        with open(os.path.join(json_dir, '{}.json'.format(paper_dict['arxiv_id'])), 'w') as file:
            json.dump(paper_dict, file, indent=4)

    except Exception as exception:
        logging.warning(exception)


def _extraction_thread(tar_dir):
    tar_paths = os.listdir(tar_dir)
    remaining_file_dict_ids = []

    for tar_path in (os.path.join(tar_dir, p) for p in tar_paths):
        for targz in io_targz.process_tar(tar_path):
            remaining_file_dict_ids.append(_extraction_process.remote(targz))

    while remaining_file_dict_ids:
        ready_file_dict_ids, remaining_file_dict_ids = ray.wait(remaining_file_dict_ids, num_returns=1)

        for file_dict_id in ready_file_dict_ids:
            _pipeline_input_queue.put(file_dict_id)

    _extraction_finished.set()


def _pipeline_thread():
    while not _extraction_finished.is_set() or not _pipeline_input_queue.empty():
        file_dict_id = _pipeline_input_queue.get()
        paper_dict_id = _pipeline_process.remote(file_dict_id)
        _saving_input_queue.put(paper_dict_id)

    _pipeline_finished.set()


def _saving_thread(json_dir):
    while not _pipeline_finished.is_set() or not _saving_input_queue.empty():
        paper_dict_id = _saving_input_queue.get()
        result_id = _saving_process.remote(paper_dict_id, json_dir)
        ray.get(result_id)


def pipeline(tar_dir, json_dir):
    ray.init(log_to_driver=False)

    _extraction = threading.Thread(target=_extraction_thread, args=(tar_dir,))
    _pipeline = threading.Thread(target=_pipeline_thread)
    _saving = threading.Thread(target=_saving_thread, args=(json_dir,))

    _extraction.start()
    _pipeline.start()
    _saving.start()

    _extraction.join()
    _pipeline.join()
    _saving.join()

    ray.shutdown()
