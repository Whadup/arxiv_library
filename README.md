# arxiv_library

A library for extracting formulas from arXiv publications.

## Usage
To start the extraction you may call:

```bash
python pipeline.py </path/to/tar-archives> </path/to/output_dir>
```
</path/to/tar-archives> should contain the tar-archives with the raw data. A tar-archive is organized as follows:
One tar arxiv (e. g. "arXiv_src_1503_007.tar") contains the sources for multiple papers from March 2015.
The members of the tar-archive represents one publication and can be of three different types:

- A single gzip compressed tex-file 
- A tar.gz archive
- A gzip compressed pdf
   
The pipeline extracts the archives and continues to process the retrieved papers.
At the end of the pipeline we get a dictionary (paper-dict) for each paper that contains the formulas that could be extracted (in LaTeX and in MathML format),
and some meta data like author, arXiv-category etc. The extracted formulas are organized section wise.

The paper-dicts are stored in json-files in the </path/to/output_dir>. 

## Architecture

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

## Dependencies
For a list of required packages you may take a look at [setup.py](setup.py).