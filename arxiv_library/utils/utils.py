"""
Some helper functions for convenience
"""
import logging
import os
import config as c

TEX_ENDING = ".tex"

VALID_FILE_EXTENSIONS = [".tex", ".bbl", ".def"]


def flatten_list(l):
    """returns a flattened list of lists"""
    flat_list = [item for sublist in l for item in sublist]
    return flat_list


def indices(soup, query):
    """
    Searches for occurences of query in soup.
    :param soup: A TexSoup object.
    :param query: The string you are searching for in soup.
    :returns: All indices at which query occurs in soup
    """
    inds = [i for i, item in enumerate(soup) if str(item) == query]
    return inds


def read_tar_file(raw, root):
    """ Tries to open the tar (or gz?) file given by raw"""

    for encoding in c.ENCODINGS:
        try:
            file_string = raw.decode(encoding)
            return file_string
        except ValueError:
            root_dir = os.path.commonprefix(root.getnames())
            logging.warning("In folder %s: Wrong encoding: %s",
                str(root_dir), encoding)

def assure_tex_ending(file_path):
    """Appends a .tex to the file_path if neccessary"""
    if TEX_ENDING not in file_path:
        file_path += TEX_ENDING
    return file_path


def assure_valid_extension(file_path):
    """Checks if file_path has a valid file extension and
    appends a tex-ending if there is no file extension. """
    _, file_ext = os.path.splitext(file_path)

    if file_ext in VALID_FILE_EXTENSIONS:
        return file_path
    if not file_ext:
        return file_path + TEX_ENDING
    logging.warning("Unkown file ending: %s in path: %s", file_ext, file_path)
    return file_path


def format_err_lines(err_lines):
    """condense error messages into a single line"""
    output = ""
    for line in err_lines:
        line = line.replace("\n", "")
        output += line
        output += "\n"
    return output


def rm_duplicates(seq):
    """remove duplicates from 'seq'"""
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def assure_dir_exists(directory):
    """ Checks if given dir exists. Makes dir if it does not exist."""
    if not os.path.isdir(directory):
        os.mkdir(directory)


def identify_persistent_disk():
    c.PERSISTENT_DISKS = [d for d in c.PERSISTENT_DISKS if os.path.isdir(d)]
    if not c.PERSISTENT_DISKS:
        raise RuntimeError("arxiv_processed not found. Exiting.")
