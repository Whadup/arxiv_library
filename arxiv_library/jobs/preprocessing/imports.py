import arxiv_library.utils.utils as utils
import logging
import os
import re


def find_main(root):
    """ Find main tex-file in dir and return its path """

    for file_path in os.listdir(root):
        if file_path.endswith('.tex'):
            file_path = os.path.join(root, file_path)

            with open(file_path) as f:
                file_string = f.read()

                if file_string is None:
                    return None

                if '\\begin{document}' in file_string:
                    return os.path.basename(file_path)

    return None


def resolve(file_name, root_dir, depth=3):
    """Resolve all imports in a given latex file.
    :param file_name: A string denoting the name of the file
    that should be resolved.
    :param root_dir: A string denoting the absolute directory
    root, in which the file of the paper is located.
    :param depth:
    :returns: A string with all importing latex commands recursively
    resolved.
    """

    file_path = os.path.join(root_dir, file_name)

    if not os.path.exists(file_path):
        logging.warning("File not found: " + file_path); return

    regexs = [
        (re.compile(r"\\input(\{.*?\})"), False),  # (regex, filepath is relative)
        (re.compile(r"\\include(\{.*?\})"), False),
        (re.compile(r"\\subimport\*?(\{.*?\})(\{.*?\})"), True),
        (re.compile(r"\\import\*?(\{.*\})(\{.*?\})"), True)
    ]

    with open(file_path) as tex_file:
        tex_string = tex_file.read()

        if tex_string is None:
            return

        if depth == 0:
            return tex_string

        for regex, matched_path_is_relative in regexs:
            for match in regex.finditer(tex_string):
                if matched_path_is_relative:
                    dir = root_dir
                    name = match.groups()[0]

                else:
                    dir = match.groups()[0]
                    name = match.groups()[1]

                dir = dir.strip("{}")
                name = name.strip("{}")
                path = os.path.join(dir, name)

                if '.tikz' in name:
                    tex_string = tex_string.replace(match.group(), ""); continue

                corrected_path = utils.assure_valid_extension(path)
                corrected_name = os.path.basename(corrected_path)
                corrected_dir = os.path.dirname(corrected_path)

                matched_file_tex = resolve(corrected_name, corrected_dir, depth - 1)
                tex_string = tex_string.replace(match.group(), matched_file_tex)

    bbl_path = os.path.join(root_dir, file_name).replace('.tex', '.bbl')

    if os.path.exists(bbl_path):
        tex_string += resolve(bbl_path, root_dir, depth - 1)

    return tex_string
