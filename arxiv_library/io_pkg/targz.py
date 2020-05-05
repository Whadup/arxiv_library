import tarfile
import gzip
import magic
import os
import logging
import re
import shutil
import io_pkg.paths as path_config
from chardet.universaldetector import UniversalDetector

# if .gz is actually a gz file with only one tex file in it,
# the file/magic command gives something with : '[...]was "main.tex"[..]'
single_gz_re = re.compile(r"was \".*?\"")


def extract_arxiv_month(tar_archive):
    """ 
    The tars are organised monthwise. E. g. the tar archive arXiv_src_0305_001.tar
    contains all papers of May 2003. In this tar archive is a (tar).gz for every paper.
    This function takes a path to a tar archive and returns its content as a list of file_dicts.
    One file_dict per paper. 
    The arg tmp_dir gives a directory where the tar_archive can be temporarally extracted to.
    """
    tar = tarfile.open(tar_archive, mode="r")
    tar.extractall(path_config.get_path("tmp_tar"))

    # get subdir to that tar was extracted
    names = tar.getnames()
    subdir = os.path.join(path_config.get_path("tmp_tar"), names[0])

    file_dicts = []

    for paper_gz in os.listdir(subdir):

        if paper_gz.endswith(".pdf"):
            continue
        elif paper_gz.endswith(".gz"):
            file_dict = process_paper_gz(paper_gz, subdir)
            file_dicts.append(file_dict)
        else:
            logging.warning("Unknown file ending: {}".format(paper_gz))

    shutil.rmtree(subdir)
    return file_dicts


def process_paper_gz(paper_gz, subdir):
    """Extract a (tar).gz-file of a paper and return it as a file_dict."""
    gz_path = os.path.join(subdir, paper_gz)
    file_dict = {"arxiv_id": paper_gz.replace(".gz", "")}

    # There are .gz files that were a singular tex-file and there are .gz files that were directories
    # with multiple files and tex-directories. In the latter case the .gz is actually a tar.gz and has
    # to be handled differently. We can detect this with the following two lines.
    file_type = magic.from_file(gz_path)
    match = single_gz_re.search(file_type)

    # if gz is really a gz with a single tex-file...
    if match:
        # extract and decode it
        with gzip.open(gz_path, "rb") as gf:
            raw_bytes = gf.read()
            decode_n_store(raw_bytes, file_dict, "main.tex", gz_path)
    # it is actually a tar.gz...
    else:
        try:
            # Open the tar archive first
            tar_gz = tarfile.open(gz_path)
            gz_names = tar_gz.getnames()

            # Extract every "tex" or "bbl" member of the tar archive
            for gz_name in gz_names:
                # TODO do we need other files?

                if not gz_name.endswith(".tex") and not gz_name.endswith(".bbl"):
                    continue
                gz_buffer = tar_gz.extractfile(gz_name)
                raw_bytes = gz_buffer.read()
                decode_n_store(raw_bytes, file_dict, gz_name, gz_path)
        except tarfile.ReadError:
            logging.error("Could not read tar: {}".format(paper_gz))

    return file_dict


def decode_n_store(raw_bytes, file_dict, file_path, paper):
    """
    Try to detect the encoding of the byte_string (raw_bytes), encode it respectively,
    and put the resulting string into the file_dict with file_path as key.
    The arg paper is needed for proper error reports.
    """
    # Detect the encoding
    detector = UniversalDetector()
    for line in raw_bytes.splitlines():
        detector.feed(line)
        if detector.done: break
    detector.close()
    encoding = detector.result['encoding']
    
    # TODO Exception handling when no encoding is found

    if encoding:
        try:
            decoded = raw_bytes.decode(encoding)
            file_dict[file_path] = decoded 
            file_dict[file_path + "_enc"] = encoding
        except UnicodeDecodeError:
            logging.warning("Decode Error for file {} in paper {}".format(file_path, paper))
