# arxiv_library

## Usage of internal python functions

#### tar-extraction:
You may retrieve all file_dicts for a tar archive with all papers from one month like this:

```python
from io_pkg.targz import process_gz, process_tar 

for compressed_file_dict in process_tar("path/to/tar_archive"):
    file_dict = process_gz(compressed_file_dict)
    # do something with the file dict
``` 

#### tex-extraction
With the tex-extraction process we want extract the formulas from a paper. The paper is provided as a filedict.

During this process we perform the following steps:
1. Remove all comments in all tex-files.
2. Resolve all imports, so that we get one big tex-files that contains all paper content.
3. Extract the preamble of the big tex-file.
4. Split the paper content (anything between \begin{document} and \end{document}) into sections.
5. Search for math-environments within the sections and extract them to the paperdict
6. Extract citation imformation from the paper.

You may implement this pipeline with something like this:

```python
from preprocessing.comments import remove_comments
from preprocessing.imports import resolve_imports 
from extraction.preamble import extract_preamble
from extraction.sections import extract_sections 
from extraction.equations import extract_equations
from extraction.citations import extract_citations

# Initially you need a filedict from the tar-extraction
file_dict = {"..." : "..."}
file_dict = remove_comments(file_dict)
paper_dict = resolve_imports(file_dict)
paper_dict = extract_preamble(paper_dict)
paper_dict = extract_sections(paper_dict)
paper_dict = extract_equations(paper_dict)
paper_dict = extract_citations(paper_dict)
```
## Architecture

(API toplevel)

pipeline

call job 1

call job 2
..

----------
Pipeline modules:

    PREPROCESSING	comments	    filedict -> filedict
                    imports		    filedict -> paperdict {paper: str}

	EXTRACTION      preamble	    paperdict -> paperdict {preamble: str, paper: str}
                    sections	    paperdict -> paperdict {.. sections: [str]}
                    equations	    paperdict -> paperdict {.. equations: [str]}
                    citations	    paperdict -> paperdict {.. citations: [str (bibids)]}
	
	COMPILATION     dict to latex
                    latex to mathml

    IO_PKG          targz               archive -> filedict(s)
                    json-store
	                metadata            paperdict -> paperdict
		

-----------------------
**filedict**: dict() of files in a paper directory with {relative path: filestring}

**paperdict**: dict() with keys [paper, preamble, sections,  citations, metadata] for a single paper

## Dependencies
For a list of required packages you may take a look at [setup.py](setup.py).