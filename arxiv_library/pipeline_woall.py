import json
import os
import logging
import traceback
import preprocessing.comments
import preprocessing.imports
import extraction.preamble
import extraction.sections
import extraction.equations
import extraction.citations
import compilation.mathml
import io_pkg.metadata
import io_pkg.targz
import io_pkg.paths


def pipeline(tar_dir, json_dir):
    tar_paths = os.listdir(tar_dir)
    cache = []

    debug = True

    success_on_compile = 0
    failed_on_compile = 0
    failed_on_metadata = 0
    failed_critical = 0
    paper_total = 0

    for tar_path in (os.path.join(tar_dir, p) for p in tar_paths):
        paths = io_pkg.targz.tar_to_file_dict(tar_path)

        for path in paths:
            paper_total += 1

            try:
                file_dict = io_pkg.targz.gz_to_file_dict(path)

                file_dict = preprocessing.comments.remove_comments(file_dict)
                paper_dict = preprocessing.imports.resolve_imports(file_dict)

                paper_dict = extraction.preamble.extract_preamble(paper_dict)
                paper_dict = extraction.sections.extract_sections(paper_dict)
                paper_dict = extraction.equations.extract_equations(paper_dict)
                paper_dict = extraction.citations.extract_citations(paper_dict)

                paper_dict = compilation.mathml.compile_paper(paper_dict, paper_dict['arxiv_id'])

                if debug:
                    for section in paper_dict['sections']:
                        for equation in section['equations']:
                            if not equation['mathml']:
                                failed_on_compile += 1
                            else:
                                success_on_compile += 1

                cache.append(paper_dict)

                if len(cache) > 100:
                    paper_dicts = io_pkg.metadata.receive_meta_data(cache)

                    if debug:
                        for pd in paper_dicts:
                            if 'metadata' not in pd.keys():
                                failed_on_metadata += 1

                    for pd in paper_dicts:
                        with open(os.path.join(json_dir, '{}.json'.format(pd['arxiv_id'])), 'w') as file:
                            json.dump(pd, file, indent=4)

                    cache = []

            except Exception as exception:
                logging.warning(exception)
                failed_critical += 1

    if debug:
        logging.warning('{} equations not compiled to mathml!'.format(failed_on_compile))
        logging.warning('{} equations got compiled to mathml!'.format(success_on_compile))
        logging.warning('{} papers without metadata!'.format(failed_on_metadata))
        logging.warning('{} critical pipeline errors!'.format(failed_critical))
        logging.warning('{} papers processed in total!'.format(paper_total))
