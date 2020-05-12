import tarfile
import gzip
import magic
import os
import logging
import re
from chardet.universaldetector import UniversalDetector

# if .gz is actually a gz file with only one tex file in it,
# the file/magic command gives something with : '[...]was "main.tex"[..]'
single_gz_re = re.compile(r"was \".*?\"")


def process_tar(archive_path):
    tar = tarfile.open(archive_path, mode='r')
    members = tar.getmembers()
    compressed_fd = lambda m: {"compressed": tar.extractfile(m), "arxiv_id": os.path.basename(m.name).replace(".gz", "")}
    return (compressed_fd(member) for member in members[1:] if ".pdf" not in member.name)


def process_gz(file_dict):
    member_buffer = file_dict["compressed"]
    del file_dict["compressed"]
    member_bytes = member_buffer.read()
    member_buffer.seek(0)
    file_type = magic.from_buffer(member_bytes)
    match = single_gz_re.search(file_type)
    if match:
        if ".tex" in file_type:
            decompressed = gzip.decompress(member_bytes)
            _decode_n_store(decompressed, file_dict, "main.tex", file_dict["arxiv_id"])
        elif ".tar" in file_type:
            _extract_n_store(member_buffer, file_dict)
        else:
            logging.warning("The file command detected an unknown file type: " + file_type)
    else:
        _extract_n_store(member_buffer, file_dict)

    if len(file_dict.keys()) <= 1:
        raise ValueError("File dict for {} is empty.".format(file_dict["arxiv_id"]))

    return file_dict


def _extract_n_store(member_buffer, file_dict):
    tar_gz = tarfile.open(fileobj=member_buffer, mode="r")
    gz_names = tar_gz.getnames()
    for gz_name in gz_names:
        # NICETOHAVE do we need other files?
        if not gz_name.endswith(".tex") and not gz_name.endswith(".bbl"):
            continue
        gz_buffer = tar_gz.extractfile(gz_name)
        raw_bytes = gz_buffer.read()
        _decode_n_store(raw_bytes, file_dict, gz_name, file_dict["arxiv_id"])


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
