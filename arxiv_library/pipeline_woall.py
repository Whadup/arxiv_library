import json
import os
import logging
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
    logging.basicConfig(filename='/home/jan/arxiv_lib/pipeline.log')
    cache = []

    with io_pkg.targz.TarMonthExtractor(tar_dir) as paths:
        for path in paths:
            try:
                file_dict = io_pkg.targz.gz_to_file_dict(path)

                file_dict = preprocessing.comments.remove_comments(file_dict)
                paper_dict = preprocessing.imports.resolve_imports(file_dict)

                paper_dict = extraction.preamble.extract_preamble(paper_dict)
                paper_dict = extraction.sections.extract_sections(paper_dict)
                paper_dict = extraction.equations.extract_equations(paper_dict)
                paper_dict = extraction.citations.extract_citations(paper_dict)

                paper_dict = compilation.mathml.compile_equations(paper_dict)
                cache.append(paper_dict)

                if len(cache) > 100:
                    arxiv_ids = [pd['arxiv_id'] for pd in paper_dicts]
                    paper_dicts = io_pkg.metadata.recieve_meta_data(arxiv_ids)

                    for pd in paper_dicts:
                        with open(os.path.join(json_dir, '{}.json'.format(paper_dict['arxiv_id'])), 'w') as file:
                            json.dump(pd, file)

                    cache = []

            except Exception as exception:
                logging.warning(exception)
