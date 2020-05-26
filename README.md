# arxiv_library

A library for extracting formulas from arXiv publications.

## Installation

Download the repository from https://github.com/Whadup/arxiv_library. Set your current working directory to the
root path of the repository folder where the setup.py file is located. Install the module with 

```bash
pip install .
```

Additionally the library requires Node.js and the node module katex to be installed. You can download Node.js at 
https://nodejs.org/en/download/ and choose the respective installer for your os. The command

 ```bash
npm install -g yargs katex
```

installs the katex module, once Node.js is installed.

## Usage
If the module has been installed with pip, you can import the module like any other python module. Also 
this shell command can be called from anywhere:

```bash
equation-extractor </path/to/tar-archives> </path/to/output_dir>
```
</path/to/tar-archives> should contain the tar-archives with the raw data. A tar-archive is organized as follows:
One tar arxiv (e. g. "arXiv_src_1503_007.tar") contains the sources for multiple papers from March 2015.
One member of the tar-archive represents one publication and can be of three different types:

- A single gzip compressed tex-file 
- A tar.gz archive
- A gzip compressed pdf
   
The pipeline extracts the archives and continues to process the retrieved papers.
At the end of the pipeline we get a dictionary (paper-dict) for each paper that contains the formulas that could be extracted (in LaTeX and in MathML format),
and some meta data like author, arXiv-category etc. The extracted formulas are organized section wise.

The paper-dicts are stored in json-files in the </path/to/output_dir>. 

## Architecture

Pipeline modules:

	EXTRACTION      comments	    filedict -> filedict
                    imports		    filedict -> paperdict {paper: str}
                    preamble	    paperdict -> paperdict {preamble: str, paper: str}
                    sections	    paperdict -> paperdict {.. sections: list}
                    equations	    paperdict -> paperdict {.. sections: {latex: str, equations: [equation: {no: int, latex: str}]}}
                    citations	    paperdict -> paperdict {.. citations: [str (arxiv id)]}
	
	COMPILATION     mathml              paperdict -> paperdict {.. sections: {latex: str, equations: [equation: {.. mathml: str}]}}

    IO_PKG          targz               archive -> filedict(s)
	                metadata            paperdict -> paperdict {.. metadata: dict}
		

-----------------------
**filedict**: dict() of files in a paper directory with {relative path: filestring, arxiv_id: str}

**paperdict**: dict() with keys [paper, preamble, sections,  citations, metadata] for a single paper

## Usage of internal python functions

#### Extract tar
You may retrieve all file_dicts for a tar archive with all papers from one month like this:

```python
from io_pkg.targz import process_gz, process_tar 

for compressed_file_dict in process_tar("path/to/tar_archive"):
    file_dict = process_gz(compressed_file_dict)
    # do something with the file dict
``` 

#### Extract tex
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
from extraction.comments import remove_comments
from extraction.imports import resolve_imports 
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
# do something with the paper_dict
```

#### Compile to MathML
To compile the extracted LaTeX-formulas to MathML you may use this code:
```python
import compilation 
# Initially you will need the paper dict with the LaTeX-formulas that you want to compile.
paper_dict = {"...": "..."} 
paper_dict = compilation.mathml.compile_paper(paper_dict, paper_dict['arxiv_id'])
# do something with the paper_dict
```

#### Retrieve meta data
To retrieve the meta data for the publications by querying the arXiv-API you may use this code:
```python
import io_pkg
# Initially you will need a list with all paper dicts for that you want to retrieve meta data
paper_dicts = [...] 
paper_dicts = io_pkg.metadata.receive_meta_data(paper_dicts)
# do something with the paper_dicts
```

## Dependencies
For a list of required packages you may take a look at [setup.py](setup.py) or the [requirements.txt](requirements.txt).