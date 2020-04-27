import re

_latex_macro = re.compile(r'\\(newcommand|def|let|renewcommand)[ *\{\\].*')
_latex_braces_l = re.compile(r"(\\\{|\{)")
_latex_braces_r = re.compile(r"(\\\}|\})")


def extract_preamble(tex_string):
    """
    Extract everything before the begin document command with the goal to get most of the used packages and self
    defined commands.
    """

    preamble = tex_string.split('\\begin{document}')[0]
    macros = []
    brace_count = 0

    for line in preamble.split('\n'):
        if 'documentclass' in line:
            continue

        if _latex_macro.match(line) or brace_count > 0:
            macros.append(line)

            brace_count += len([x for x in _latex_braces_l.findall(line) if len(x) == 1])
            brace_count -= len([x for x in _latex_braces_r.findall(line) if len(x) == 1])

    return {'preamble': macros, 'paper': tex_string.split('\\begin{document}')[1]}
