import ray
import preprocessing.comments
import preprocessing.imports
import extraction.preample
import extraction.sections
import extraction.equations
import extraction.citations


@ray.remote
def _pipe(file_dict):
    file_dict = preprocessing.comments.remove_comments(file_dict)
    paper_dict = preprocessing.imports.resolve_imports(file_dict)

    paper_dict = extraction.preample.extract_preamble(paper_dict)
    paper_dict = extraction.sections.extract_sections(paper_dict)
    paper_dict = extraction.equations.extract_equations(paper_dict)
    paper_dict = extraction.citations.extract_citations(paper_dict)

    return paper_dict


def pipeline():
    ray.init()



    ray.shutdown()
