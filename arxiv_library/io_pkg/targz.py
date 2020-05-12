import tarfile
import gzip
import magic
import os
import logging
import re
from chardet.universaldetector import UniversalDetector
from io import BytesIO

# A extracted monthly-tar contains files with the endings ".gz" or ".pdf".
# We don't care for ".pdf".
# A ".gz" file can actually contain two different things: A single gzip compressed tex-file or another tar.gz archive.
# We can determine via the file/magic command.
# For singular files the file/magic command gives something like: '[...]was "main.tex"[..]'
# 'gzip compressed data, was "TMFpubl.tex", last modified: Wed Mar 11 16:46:13 2015, max speed, from Unix'
# For tar.gz archives it gives either
# 'gzip compressed data, last modified: Fri May  6 00:12:00 2016, from Unix'
# or
# 'gzip compressed data, was "9301220.tar", last modified: Thu Nov 25 19:34:37 1999, max compression, from Unix'
# the latter is common for older archives.
# So, we detect different types with these RegEx's:
single_gz_re = re.compile(r"was \".*?\.tex\"")
tar_gz_re = re.compile(r"(was \".*?\.tar\")|(gzip compressed data, last modified:)")


def process_tar(archive_path):
    """
    Take a path to a tar archive (archive_path) that contains all arXiv-papers from one month.
    Extract all members, omit the pdf members and for the remaining members:
    create a file_dict with the arxiv_id and the bytes of the member.
    """
    tar = tarfile.open(archive_path, mode='r')
    members = tar.getmembers()
    compressed_fd = lambda m: dict(compressed=tar.extractfile(m).read(),
                                   arxiv_id=os.path.basename(m.name).replace(".gz", ""))
    return [compressed_fd(member) for member in members[1:] if ".pdf" not in member.name]


def process_gz(file_dict):
    """
    Take a file dict created by process_tar.
    Determine which type of ".gz"-file is in the "compressed" entry of the file_dict.
    Extract/decompress/decode the file(s) in the "gz" and store them to the file dict.
    """
    member_bytes = file_dict["compressed"]
    # tarfile.open() cannot deal with bytes, therefore we recreate a buffered reader.
    member_buffer = BytesIO(member_bytes)
    del file_dict["compressed"]
    file_type = magic.from_buffer(member_bytes)
    gz_match = single_gz_re.search(file_type)
    tar_gz_match = tar_gz_re.search(file_type)
    if gz_match:
        decompressed = gzip.decompress(member_bytes)
        _decode_n_store(decompressed, file_dict, "main.tex", file_dict["arxiv_id"])
    elif tar_gz_match:
        _extract_tar_gz(member_buffer, file_dict)
    else:
        logging.warning("Unexpected output of file/magic command: {}".format(file_type))

    if len(file_dict.keys()) <= 1:
        raise ValueError("File dict for {} is empty.".format(file_dict["arxiv_id"]))

    return file_dict


def _extract_tar_gz(member_buffer, file_dict):
    """
    Takes a buffered reader (member_buffer) that represents a tar.gz archive.
    The tex-files and bbl-files in this archive are extracted, decoded and stored in the file_dict.
    """
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
