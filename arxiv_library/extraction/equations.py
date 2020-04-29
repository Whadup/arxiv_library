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


def extract_equations(paper_dict):
    paper_dict['equations'] = []

    for index, section in paper_dict['sections'].items():
        for env in _latex_environments:
            for match in re.finditer(env, section):
                paper_dict['equations'].append(match.groups()[-1])  # skip [..] if present

    return paper_dict


test = r'\begin{equation} hello \end{equation}'
test2 = '\\begin{equation} hello \\end{equation}'
test3 = re.escape('\begin{equation} hello \end{equation}')
test4 = r'{}'.format('\begin{equation} hello \end{equation}')
test5 = repr(test2)
test6 = r'\\begin{equation} hello \\end{equation}'

#d = extract_equations(paperdict)
# print(d)

with open('/home/jan/test.tex', 'r') as file:
    string = file.read()

    paperdict = {
        'sections' : {
            0: string
        }
    }
    print(extract_equations(paperdict))
