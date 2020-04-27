import re

_latex_environments = [
    re.compile(r'\\begin\{equation\}(\[(.*?)\])?(.*?)\\end\{equation\}'),
    re.compile(r'\\begin\{displaymath\}(\[(.*?)\])?(.*?)\\end\{displaymath\}'),
    re.compile(r'\\begin\{array\}(\[(.*?)\])?(.*?)\\end\{array\}'),
    re.compile(r'\\begin\{eqnarray\}(\[(.*?)\])?(.*?)\\end\{eqnarray\}'),
    re.compile(r'\\begin\{multline\}(\[(.*?)\])?(.*?)\\end\{multline\}'),
    re.compile(r'\\begin\{gather\}(\[(.*?)\])?(.*?)\\end\{gather\}'),
    re.compile(r'\\begin\{align\}(\[(.*?)\])?(.*?)\\end\{align\}'),
    re.compile(r'\\begin\{flalign\}(\[(.*?)\])?(.*?)\\end\{flalign\}'),
    re.compile(r'\$\$(.*?)\$\$')
]


def extract_equations(file_dict):
    file_dict['equations'] = []

    for index, section in file_dict['sections'].items():
        for env in _latex_environments:
            for match in re.finditer(env, section):
                file_dict['equations'].append(match.groups()[-1])  # skip [..] if present
