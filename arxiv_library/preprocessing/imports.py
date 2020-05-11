import os
import re


_regexs = [
    re.compile(r"\\input\{(\./)??P<path>(.*?)\}"),
    re.compile(r"\\include\{(\./)??P<path>(.*?)\}"),
    re.compile(r"\\subimport\{?P<folder>(.*?)\}\{?P<path>(.*?)\}"),
    re.compile(r"\\import\{?P<folder>(.*?)\}\{?P<path>(.*?)\}")
]


def resolve_imports(file_dict):
    for path, text in file_dict.items(): 
        if path.endswith('.tex'):
            if '\\begin{document}' in text:
                try:
                    return {'paper': _resolve_imports(path, file_dict), 'arxiv_id': file_dict['arxiv_id']}
                except Exception as exception:
                    raise exception

    if len(file_dict.items()) == 0:
        raise ValueError('File dict was empty.')

    raise ValueError('Did not find file with \\begin{{document}} in file dict.')


def _resolve_imports(path, file_dict, depth=3):
    tex_string = file_dict[path]

    if depth == 0:
        return tex_string

    for regex in _regexs:
        for match in regex.finditer(file_dict[path]):
            matched_path = match.group('path')

            if match.group('folder'):
                matched_path = os.path.join(match.group('folder'), matched_path)

            # NICETOHAVE Gibt es hier eine bessere Lösung? Ist das zwangsweise eine tex file?

            if '.' not in matched_path:
                matched_path += '.tex'

            if '.tikz' in matched_path:
                tex_string = tex_string.replace(match.group(), ''); continue

            matched_file_tex_string = _resolve_imports(matched_path, file_dict, depth - 1)
            tex_string = tex_string.replace(match.group(), matched_file_tex_string)

    if path.replace('.tex', '.bbl') in file_dict.keys():
        tex_string += _resolve_imports(path.replace('.tex', '.bbl'), file_dict, depth - 1)

    return tex_string
