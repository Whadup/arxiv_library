# arxiv_library

##Usage of internal python functions

#### tar-extraction:
You may retrieve all file_dicts for a tar archive with all papers from one month like this:

```
from io_pkg.targz import TarMonthExtractor, gz_to_file_dict
tar = TarMonthExtractor(<path/to/tar_archive>)
with tar as paths:
    for path in paths:
        file_dict = gz_to_file_dict(path)
        # do something with the file dict
``` 
The _with-syntax_ will automatically cleanup all files that were temporarily extracted on disk.

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

**paperdict**: dict() with keys [paper, preamble, sections, equations, citations, metadata] for a single paper