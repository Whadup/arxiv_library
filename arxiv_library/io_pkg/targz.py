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


class TarExtractor:
    """
    Can be used with the ```with obj as p``` syntax. obj is a object of this class and p are the paths to the gzs
    that we extract with the __enter__ method.
    The constructor needs the path to a tar archive with all arxiv_papers of a specific month.
    Via the with-syntax we can extract the gzs within the tar, retrieve the paths to the gzs and this class will cleanup
    the extracted files automatically, when we leave the with block.
    """
    def __init__(self, archive_path):
        self.archive_path = archive_path
        self.tmp_tar = path_config.get_path("tmp_tar")

    def __enter__(self):
        tar = tarfile.open(self.archive_path, mode='r')
        tar.extractall(self.tmp_tar)
        names = tar.getnames()
        self.subdir = os.path.join(self.tmp_tar, names[0])
        paths = [os.path.join(self.tmp_tar, name) for name in names[1:]]
        return paths

    def __exit__(self, exc_type, value, traceback):
        shutil.rmtree(self.subdir)


def tar_to_file_dict(archive_path):
    tar = tarfile.open(archive_path, mode='r')
    mems = tar.getmembers()
    fds = []
    for m in mems[1:]:
        extr = tar.extractfile(m)
        extr_r = extr.read()
        if ".pdf" in m.name:
            continue
        fd = {"arxiv_id": os.path.basename(m.name).replace(".gz", "")}
        print(m.name)
        file_type = magic.from_buffer(extr_r)
        print(file_type)
        match = single_gz_re.search(file_type)
        try:
            if not match:
                print("tar")
                tar_gz = tarfile.open(fileobj=tar.extractfile(m), mode="r")

                gz_names = tar_gz.getnames()

                # Extract every "tex" or "bbl" member of the tar archive
                for gz_name in gz_names:
                    # NICETOHAVE do we need other files?

                    if not gz_name.endswith(".tex") and not gz_name.endswith(".bbl"):
                        continue
                    gz_buffer = tar_gz.extractfile(gz_name)
                    raw_bytes = gz_buffer.read()
                    _decode_n_store(raw_bytes, fd, gz_name, fd["arxiv_id"])
            else:
                print("tex")
                decompressed = gzip.decompress(extr_r)
                _decode_n_store(decompressed, fd, "main.tex", fd["arxiv_id"])
        except gzip.BadGzipFile:
            print("Badgzip")
        fds.append(fd)
    return fds


def gz_to_file_dict(gz_path):
    if gz_path.endswith(".pdf"):
        return {}
    elif gz_path.endswith(".gz"):
        file_dict = _process_paper_gz(gz_path)
        return file_dict
    else:
        logging.warning("Unknown file ending: {}".format(gz_path))


def _process_paper_gz(gz_path):
    """Extract a (tar).gz-file of a paper and return it as a file_dict."""
    paper_gz = os.path.basename(gz_path)
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
            _decode_n_store(raw_bytes, file_dict, "main.tex", gz_path)
    # it is actually a tar.gz...
    else:
        try:
            # Open the tar archive first
            tar_gz = tarfile.open(gz_path)
            gz_names = tar_gz.getnames()

            # Extract every "tex" or "bbl" member of the tar archive
            for gz_name in gz_names:
                # NICETOHAVE do we need other files?

                if not gz_name.endswith(".tex") and not gz_name.endswith(".bbl"):
                    continue
                gz_buffer = tar_gz.extractfile(gz_name)
                raw_bytes = gz_buffer.read()
                _decode_n_store(raw_bytes, file_dict, gz_name, gz_path)
        except tarfile.ReadError:
            logging.error("Could not read tar: {}".format(paper_gz))

    return file_dict


def _decode_n_store(raw_bytes, file_dict, file_path, paper):
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
    
    # if chardet could not detect an encoding (encoding is None), we don't make an entry for this file in the file_dict
    if encoding:
        try:
            decoded = raw_bytes.decode(encoding)
            file_dict[file_path] = decoded 
            file_dict[file_path + "_enc"] = encoding
        except UnicodeDecodeError:
            logging.warning("Decode Error for file {} in paper {}".format(file_path, paper))
