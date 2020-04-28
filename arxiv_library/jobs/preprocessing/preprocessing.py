"""Functions for Processing Tex Documents, including identifying the main source,
resolving imports and iterating over tar archives"""
import tarfile
import re
import logging
import os
from os import path

import arxiv_library.utils.utils as h

SUBIMPORT_RE = re.compile(r"\\subimport\*?(\{.*?\})(\{.*?\})")
IMPORT_RE = re.compile(r"\\import\*?(\{.*\})(\{.*?\})")
INPUT_RE = re.compile(r"\\input(\{.*?\})")
INCLUDE_RE = re.compile(r"\\include(\{.*?\})")
SECTION_RE = re.compile(r"\\section\{(.*?)\}")
USEPACKAGE_RE = re.compile(r"\\usepackage(\[.*?\])?\w?\{(.*?)\}", re.DOTALL)
MACRO_RE = re.compile(r'\\(newcommand|def|let|renewcommand)[ *\{\\].*')
BEGIN_RE = re.compile(r'\\begin.*')
LATEX_BRACES_L = re.compile(r"(\\\{|\{)")
LATEX_BRACES_R = re.compile(r"(\\\}|\})")

USEPACKAGE_HULL = r"\\usepackage\[.*?\]{}"

TEX_ENDING = ".tex"
TIKZ_ENDING = ".tikz"
BBL_ENDING = ".bbl"
DEF_ENDING = ".def"

EXTENSIONS_TO_EXTRACT = [TEX_ENDING, DEF_ENDING, BBL_ENDING]

BEGIN_DOC = "\\begin{document}"

FILE_EXISTS_TEMPLATE = "\\IfFileExists{{{package}.sty}}{{\\usepackage{{{package}}}}}{{}}"


############################
# Functions for tar Extraction
############################
def iterate_tar(tar_archive):
    """Iterator over all gzips in a .tar archive"""
    if not tar_archive.endswith(".tar"):
        yield 0
        return
    try:
        tar = tarfile.open(os.path.join(c.TAR_LOCATION, tar_archive), mode="r")
        # try if getnames will work
        names = tar.getnames()
    except tarfile.TarError as error:
        logging.warning("In archive {tar}: corrupted (TarError): {error}",
                        tar=tar_archive, error=error)
        yield 0
        return
    except EOFError:
        yield 0
        return

    for name in names:
        if name.endswith("gz"):
            try:
                gzip = tarfile.open(fileobj=tar.extractfile(tar.getmember(name)), mode="r")
                yield gzip, name
            except tarfile.TarError as error:
                # pylint: disable=logging-format-interpolation
                logging.warning("In archive {tar}/{gz}: corrupted (GZipError): {error}".format(
                        tar=tar_archive, gz=name, error=error))

def extract_gz(gzip, name, target=None):
    """Copies all tex-files in the source tar-archive to a
    respective directory in c.TAR_EXTRACT_OUTPUT.
    It also calls rm_comms for all extractet files.
    :param source: a string denoting the path to the tar
    :return: 1 if succesfull, 0 if not.
    """
    import config as c
    arxiv_id = os.path.basename(name).replace(".gz", "")
    if target is None:
        target = os.path.join(c.TEX_LOCATION, arxiv_id)
        os.mkdir(target)

    for file_name in gzip.getnames():
        _, file_ext = os.path.splitext(file_name)
        if file_ext in EXTENSIONS_TO_EXTRACT:

            member = gzip.getmember(file_name)
            # f is a bufferedreader
            f = gzip.extractfile(member)

            if f is None:
                logging.warning("The extraction of the file " + name + " returned a NoneType object.")
                continue

            raw = f.read()

            # encode with diffrent encodings
            file_string = None
            for encoding in c.ENCODINGS:
                try:
                    file_string = raw.decode(encoding)
                    break
                except ValueError:
                    pass

            # if file could be encoded write it to target
            if file_string is not None:
                file_string = rm_comms(file_string)
                target_file = path.join(target, file_name)
                # the path "target_file" might contain
                # subdirectories that have not been
                # created yet. However they will be
                # created in the except block.
                try:
                    with open(target_file, 'w') as t:
                        t.write(file_string)
                except FileNotFoundError:
                    os.makedirs(path.dirname(target_file))
                    with open(target_file, 'w') as t:
                        t.write(file_string)

    # check if created directory is empty
    # and delete empty dirs.
    if os.listdir(target):
        return 1
    os.rmdir(target)
    return 0


###############################
# Functions for removing comments
###############################


def rm_comms(tex_string):
    """ Remove all commented statements from tex_string."""
    lines = tex_string.split("\n")
    resulting_lines = ""
    for line in lines:
        res_line = rm_comm_in_line(line)
        resulting_lines += res_line + "\n"

    return resulting_lines


def rm_comm_in_line(line):
    """remove comments in line"""
    escaped = False
    resulting_line = ""

    for ch in line:
        if escaped:
            escaped = False
            resulting_line += ch
        elif ch == '\\':
            escaped = True
            resulting_line += ch
        elif ch == '%':
            return resulting_line
        else:
            resulting_line += ch

    return resulting_line


###############################
# Functions for resolving imports
###############################


def find_main(root):
    """ Find main tex-file in dir and return its path """
    for file_path in os.listdir(root):

        if file_path.endswith(TEX_ENDING):

            file_path = os.path.join(root, file_path)
            with open(file_path) as f:
                file_string = f.read()

                if file_string is None:
                    return None

                if BEGIN_DOC in file_string:
                    return os.path.basename(file_path)
    return None


def resolve(file_name, root_dir, curr_dir, maxdepth=3):
    """Resolve all imports in a given latex file.
    :param file_name: A string denoting the name of the file
    that should be resolved.
    :param root_dir: A string denoting the absolute directory
    root, in which the main file of the paper is located.
    :param curr_dir: A string denoting the relative directory
    in which the current file is located. root_dir and curr_dir should
    be equal for the first call on the main file.
    :returns: A string with all importing latex commands recursively
    resolved.
    """
    file_path = path.join(curr_dir, file_name)
    try:
        with open(file_path) as tex_file:
            tex = tex_file.read()
            root_dir = path.dirname(file_path)

            if tex is None:
                return None
            if maxdepth == 0:
                return tex

            # resolve input commands
            for match in INPUT_RE.finditer(tex):
                in_file = match.groups()[0]
                in_file = in_file.strip("{}")

                # ignore tikz input
                if TIKZ_ENDING in in_file:
                    tex = tex.replace(match.group(), "")
                    continue

                in_file = path.join(root_dir, in_file)
                in_file = h.assure_valid_extension(in_file)

                in_file_name = path.basename(in_file)
                curr_dir = path.dirname(in_file)

                in_string = resolve(in_file_name, root_dir, curr_dir, maxdepth=maxdepth-1)

                tex = tex.replace(match.group(), in_string)

            # resolve include commands
            for match in INCLUDE_RE.finditer(tex):
                in_file = match.groups()[0]
                in_file = in_file.strip("{}")

                # ignore tikz input
                if TIKZ_ENDING in in_file:
                    tex = tex.replace(match.group(), "")
                    continue

                in_file = path.join(root_dir, in_file)
                in_file = h.assure_valid_extension(in_file)

                in_file_name = path.basename(in_file)
                curr_dir = path.dirname(in_file)

                in_string = resolve(in_file_name, root_dir, curr_dir, maxdepth=maxdepth-1)

                tex = tex.replace(match.group(), in_string)

            # resolve subimport commands
            for match in SUBIMPORT_RE.finditer(tex):
                path_to_file = match.groups()[0]
                file = match.groups()[1]
                path_to_file = path_to_file.strip("{}")
                file = file.strip("{}")
                in_file = path.join(path_to_file, file)

                # ignore tikz input
                if TIKZ_ENDING in in_file:
                    tex = tex.replace(match.group(), "")
                    continue

                in_file = path.join(curr_dir, in_file)
                in_file = h.assure_valid_extension(in_file)

                in_file_name = path.basename(in_file)
                curr_dir = path.dirname(in_file)

                in_string = resolve(in_file_name, root_dir, curr_dir, maxdepth=maxdepth-1)

                tex = tex.replace(match.group(), in_string)

            # resolve import commands
            for match in IMPORT_RE.finditer(tex):
                path_to_file = match.groups()[0]
                file = match.groups()[1]
                path_to_file = path_to_file.strip("{}")
                file = file.strip("{}")
                in_file = path.join(path_to_file, file)

                # ignore tikz input
                if TIKZ_ENDING in in_file:
                    tex = tex.replace(match.group(), "")
                    continue

                in_file = path.join(curr_dir, in_file)
                in_file = h.assure_valid_extension(in_file)

                in_file_name = path.basename(in_file)
                curr_dir = path.dirname(in_file)

                in_string = resolve(in_file_name, root_dir, curr_dir, maxdepth=maxdepth-1)

                tex = tex.replace(match.group(), in_string)

            bbl_path = path.join(curr_dir, file_name).replace(TEX_ENDING, BBL_ENDING)
            if os.path.exists(bbl_path):
                tex += resolve(bbl_path, root_dir, curr_dir, maxdepth=maxdepth-1)
            return tex
    except FileNotFoundError:
        logging.warning("File not found: " + file_path)
        return ""


##########################
# Functions for sectionizing
##########################
FORBIDDEN_SEC_CHARS = ['/', '{', '}', '$', '^', '\\', "\'", "`", "\""]
def sectionize(tex_string):
    """Splits a given tex-string in its sections.
    Requires a string without commented statements.
    You may use rm_comms to ensure this.
    :param tex_string: A string containing a whole arxiv-tex-document.
    :return: A dictionary of strings. Each entry maps the name
    of a section to its content.
    """
    sections = {}
    current_sec = SECTION_RE.search(tex_string)

    # while another section command can be found
    while current_sec:
        sec_str = current_sec.group()
        tex_string = tex_string.replace(sec_str, "")

        next_sec = SECTION_RE.search(tex_string)
        sec_start_index = current_sec.span()[1] - len(sec_str)

        if not next_sec:
            sec_content = tex_string[sec_start_index:]
        else:
            sec_end_index = next_sec.span()[0]
            sec_content = tex_string[sec_start_index:sec_end_index]

        sec_id = current_sec.groups()[0]

        for forbidden_char in FORBIDDEN_SEC_CHARS:
            sec_id = sec_id.replace(forbidden_char, "")

        sections[sec_id] = sec_content

        current_sec = next_sec

    return sections


#######################################
# Functions for Extracting the preamble
#######################################


def extract_preamble(tex_string):
    """
    Extract everything before the begin document command
    with the goal to get most of the used packages and
    self defined commands.
    """
    splitted = tex_string.split(BEGIN_DOC)
    preamble = splitted[0]
    preamble = filter_doc_class(preamble)
    macros = extract_macros(preamble)

    return macros


def filter_doc_class(tex_string):
    """identify the document class in tex strings"""
    for line in tex_string.split("\n"):
        if "documentclass" in line:
            tex_string = tex_string.replace(line, "")
            return tex_string
    return tex_string


def extract_macros(preamble):
    """Extract all macros from preamble."""
    lines = preamble.split("\n")
    macros = []
    brace_count = 0

    for line in lines:

            if MACRO_RE.match(line) or brace_count > 0:

                macros.append(line)
                # brace difference in this line
                brace_count += len([x for x in LATEX_BRACES_L.findall(line) if len(x) == 1]) - \
                        len([x for x in LATEX_BRACES_R.findall(line) if len(x) == 1])

    return macros
