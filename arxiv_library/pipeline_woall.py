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

    failed_on_compile = 0
    failed = 0
    count = 0

    for tar_path in (os.path.join(tar_dir, p) for p in tar_paths):
        with io_pkg.targz.TarExtractor(tar_path) as paths:
            for path in paths:
                count += 1

                try:
                    file_dict = io_pkg.targz.gz_to_file_dict(path)

                    file_dict = preprocessing.comments.remove_comments(file_dict)
                    paper_dict = preprocessing.imports.resolve_imports(file_dict)

                    paper_dict = extraction.preamble.extract_preamble(paper_dict)
                    paper_dict = extraction.sections.extract_sections(paper_dict)
                    paper_dict = extraction.equations.extract_equations(paper_dict)
                    paper_dict = extraction.citations.extract_citations(paper_dict)

                    try:
                        paper_dict = compilation.mathml.compile_paper(paper_dict, paper_dict['arxiv_id'])
                    except:
                        failed_on_compile += 1
                        raise ValueError()

                    cache.append(paper_dict)

                    if len(cache) > 100:
                        paper_dicts = io_pkg.metadata.receive_meta_data(paper_dicts)

                        for pd in paper_dicts:
                            with open(os.path.join(json_dir, '{}.json'.format(paper_dict['arxiv_id'])), 'w') as file:
                                json.dump(pd, file, indent=4)

                        cache = []

                except Exception as exception:
                    logging.warning(exception)
                    traceback.print_exc()
                    failed += 1

    logging.warning('FAILED ON MATHML COMPILATION: {}'.format(failed_on_compile))
    logging.warning('FAILED TOTAL: {}'.format(failed))
    logging.warning('PAPERS TOTAL: {}'.format(count))
