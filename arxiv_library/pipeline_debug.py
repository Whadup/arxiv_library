import json
import os
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


def pipeline(tar_dir, json_dir):
    tar_paths = os.listdir(tar_dir)
    cache = []

    success_on_compile = 0
    failed_on_compile = 0
    failed_on_metadata = 0
    failed_critical = 0
    paper_total = 0

    for tar_path in (os.path.join(tar_dir, p) for p in tar_paths):
        targzs = io_targz.process_tar(tar_path)

        for i, targz in enumerate(targzs):
            paper_total += 1

            try:
                file_dict = io_targz.process_gz(targz)

                file_dict = comments.remove_comments(file_dict)
                paper_dict = imports.resolve_imports(file_dict)

                paper_dict = preamble.extract_preamble(paper_dict)
                paper_dict = sections.extract_sections(paper_dict)
                paper_dict = equations.extract_equations(paper_dict)
                paper_dict = citations.extract_citations(paper_dict)

                paper_dict = mathml.compile_paper(paper_dict, paper_dict['arxiv_id'])

                # debug start
                for section in paper_dict['sections']:
                    for equation in section['equations']:
                        if not equation['mathml']:
                            failed_on_compile += 1
                        else:
                            success_on_compile += 1
                # debug end

                cache.append(paper_dict)

                if len(cache) > 100 or i == len(targzs) - 1:
                    paper_dicts = io_metadata.receive_meta_data(cache)

                    # debug start
                    for pd in paper_dicts:
                        if 'metadata' not in pd.keys():
                            failed_on_metadata += 1
                    # debug end

                    for pd in paper_dicts:
                        with open(os.path.join(json_dir, '{}.json'.format(pd['arxiv_id'])), 'w') as file:
                            json.dump(pd, file, indent=4)

                    cache = []

            except Exception as exception:
                logging.warning(exception)
                failed_critical += 1

    logging.warning('{} equations not compiled to mathml!'.format(failed_on_compile))
    logging.warning('{} equations got compiled to mathml!'.format(success_on_compile))
    logging.warning('{} papers without metadata!'.format(failed_on_metadata))
    logging.warning('{} critical pipeline errors!'.format(failed_critical))
    logging.warning('{} papers processed in total!'.format(paper_total))
