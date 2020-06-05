import re

_latex_environments = [
    re.compile(r'\\begin\{equation\}(\[(.*?)\])?(.*?)\\end\{equation\}', flags=re.DOTALL),
    re.compile(r'\\begin\{displaymath\}(\[(.*?)\])?(.*?)\\end\{displaymath\}', flags=re.DOTALL),
    re.compile(r'\\begin\{array\}(\[(.*?)\])?(.*?)\\end\{array\}', flags=re.DOTALL),
    re.compile(r'\\begin\{eqnarray\}(\[(.*?)\])?(.*?)\\end\{eqnarray\}', flags=re.DOTALL),
    re.compile(r'\\begin\{multline\}(\[(.*?)\])?(.*?)\\end\{multline\}', flags=re.DOTALL),
    re.compile(r'\\begin\{gather\}(\[(.*?)\])?(.*?)\\end\{gather\}', flags=re.DOTALL),
    re.compile(r'\\begin\{align\}(\[(.*?)\])?(.*?)\\end\{align\}', flags=re.DOTALL),
    re.compile(r'\\begin\{flalign\}(\[(.*?)\])?(.*?)\\end\{flalign\}', flags=re.DOTALL),
    re.compile(r'\$\$(.*?)\$\$', flags=re.DOTALL),
    re.compile(r'\\\[(.*?)\\\]', flags=re.DOTALL)
]


def extract_equations(paper_dict):
    count = 0

    for section in paper_dict['sections']:
        for env in _latex_environments:
            for match in re.finditer(env, section['latex']):
                section['equations'].append({
                    'no': count,
                    'latex': match.groups()[-1]
                })

                count += 1

    return paper_dict
