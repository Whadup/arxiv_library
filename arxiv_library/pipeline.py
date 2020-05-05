import ray
import json
import os
import threading
import queue
import logging
import io_pkg.targz
import io_pkg.metadata
import io_pkg.paths
import preprocessing.comments
import preprocessing.imports
import extraction.preample
import extraction.sections
import extraction.equations
import extraction.citations
import compilation.mathml


# TODO eine pipeline ohne multithreading und eine ohne multithreading und multiprocessing schreiben und evaluieren


_file_dict_queue = queue.Queue()
_paper_dict_queue = queue.Queue()

_extraction_finished = threading.Event()
_pipeline_finished = threading.Event()


@ray.remote
def _extract(tar_path):
    try:
        return io_pkg.targz.gz_to_file_dict(tar_path)

    except Exception as exception:
        logging.warning(exception)


@ray.remote
def _pipe(file_dict_id):
    try:
        file_dict = ray.get(file_dict_id)  # TODO muss ich das hier getten oder nicht?

        file_dict = preprocessing.comments.remove_comments(file_dict)
        paper_dict = preprocessing.imports.resolve_imports(file_dict)

        paper_dict = extraction.preample.extract_preamble(paper_dict)
        paper_dict = extraction.sections.extract_sections(paper_dict)
        paper_dict = extraction.equations.extract_equations(paper_dict)
        paper_dict = extraction.citations.extract_citations(paper_dict)

        # paper_dict = compilation.mathml.bla(paper_dict)  # TODO hier einmal eine entsprechende Methode schreiben

        return paper_dict

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


def _extraction_thread(tar_dir):
    tar_paths = os.listdir(tar_dir)
    file_dict_ids = []

    for tar_path in tar_paths:
        with io_pkg.targz.TarMonthExtractor(tar_path) as targz_paths:
            for path in targz_paths:
                file_dict_ids.append(_extract.remote(path))

    remaining_file_dict_ids = True

    while remaining_file_dict_ids:
        ready_file_dict_ids, remaining_file_dict_ids = ray.wait(file_dict_ids, num_returns=32)

        for id in ready_file_dict_ids:
            _file_dict_queue.put(id)

    _extraction_finished.set()


def _pipeline_thread():
    while not _extraction_finished.is_set() or not _file_dict_queue.empty():
        file_dict_id = _file_dict_queue.get()
        paper_dict_id = _pipe.remote(file_dict_id)
        _paper_dict_queue.put(paper_dict_id)

    _pipeline_finished.set()


def _saving_thread(json_dir):
    while _pipeline_finished.is_set() or not _paper_dict_queue.empty():
        paper_dict_id = _paper_dict_queue.get()
        result_id = _save.remote(paper_dict_id, json_dir)


def pipeline(tar_dir, json_dir):
    ray.init()

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
