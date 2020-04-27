import arxiv_library.utils.utils as utils
import logging
import os
import re


def resolve_imports(file_dict):
    for path, text in file_dict.items(): 
        if path.endswith('.tex'):
            if '\\begin{document}' in text:
                return _resolve_imports(path, file_dict)

    raise ValueError('Did not find file with \\begin{{document}} in file dict.')


def _resolve_imports(path, file_dict, depth=3):
    regexs = [
        (re.compile(r"\\input(\{.*?\})"), False),  # (regex, filepath has path prefix as argument)
        (re.compile(r"\\include(\{.*?\})"), False),
        (re.compile(r"\\subimport\*?(\{.*?\})(\{.*?\})"), True),
        (re.compile(r"\\import\*?(\{.*\})(\{.*?\})"), True)
    ]

    tex_string = file_dict[path]

    if depth == 0:
        return tex_string

    for regex, has_path_prefix in regexs:
        for match in regex.finditer(file_dict[path]):
            matched_path = match.groups()[0].strip("{}")

            if has_path_prefix:
                matched_path = os.path.join(matched_path, match.groups()[1].strip("{}"))

            if '.tikz' in matched_path:
                tex_string = tex_string.replace(match.group(), ''); continue

            matched_file_tex_string = _resolve_imports(matched_path, file_dict, depth - 1)
            tex_string = tex_string.replace(match.group(), matched_file_tex_string)

    if path.replace('.tex', '.bbl') in file_dict.keys():
        tex_string += _resolve_imports(path.replace('.tex', '.bbl'), file_dict, depth - 1)

    return tex_string
