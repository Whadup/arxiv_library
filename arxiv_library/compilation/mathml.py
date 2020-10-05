"""Functions for translating Latex-Equations MathML-Equations"""
import os
import subprocess
import json
import logging
import re

annotation_re = re.compile(r'<annotation.*</annotation>', re.DOTALL)

# In tex-sources \def macros are often defined like this: \def \foo [#1]
# KaTeX cannot handle the square brackets. This RE is part of the process to bring the def commands in 
# the right format for KaTeX. See the function format_def
def_re = re.compile(r"(\\def\s?\\(\w|\s)*)(\[#1\])")
# Use this process only when this var is True
EXPERIMENTAL = False

# Macros that often cause problems, but have no semantic efect for the formula, are redefiened so that they do nothing.
PREAMBLE_HOTFIX = [
    r"\newcommand{\label}[1]{}",
    r"\def \let {\def}",
    r"\newcommand{\mbox}[1]{\text{#1}}",
    r"\newcommand{\sbox}[1]{\text{#1}}",
    r"\newcommand{\hbox}[1]{\text{#1}}",
    r"\newcommand{\nonumber}{}",
    r"\newcommand{\notag}{}",
    r"\newcommand{\value}[1]{#1}",
    r"\newcommand{\todo}{}",
    r"\def{\cal}{\mathcal}",
    r"\def{\mathds}{\mathbb}",
    r"\def{\mathbbm}{\mathbb}",
    r"\newcommand{\scalebox}[1]{#1}",
    r"\newcommand{\vspace}[1]{}",
    r"\newcommand{\ensuremath}{}",
    r"\newcommand{\hfill}{}",
    r"\newcommand{\footnote}[1]{}",
    r"\newcommand{\footnotemark}[1]{}",
    r"\newcommand{\marginpar}[1]{}",
    r"\newcommand{\xspace}{}",
    r"\newcommand{\norm}[1]{\lVert #1 \rVert}",
    r"\newcommand{\lefteqn}[1]{#1}",
    r"\newcommand{\textsc}[1]{\text{#1}}",
    r"\newcommand{\newtheorem}[2]{}",
    r"\newcommand{\par}{ \\ }",
    r"\newcommand{\vskip}{}",
    r"\newcommand{\baselineskip}{}",
    r"\newcommand{\textsuperscript}[1]{^{#1}}",
    r"\newcommand{\title}[1]{}",
    r"\newcommand{\author}[1]{}",
    r"\newcommand{\makeatother}{}",
    r"\newcommand{\E}{\mathbb{E}}"
]

PREAMBLE_SUBS = {
    r"\boldmath": r"\bf",
    r"\DeclareMathOperator": r"\newcommand"
}

LATEX_SUBS = {
    r"\begin{split}": "",
    r"\end{split}": ""
}


def format_def(preamble_entry):
    match = def_re.match(preamble_entry)
    if match:
        residual = def_re.sub("", preamble_entry)
        groups = match.groups()
        return groups[0] + "#1" + residual
    else:
        return preamble_entry


def substitute_from_dict(preamble_entry, sub_dict):
    for key, value in sub_dict.items():
        preamble_entry = preamble_entry.replace(key, value)

    if EXPERIMENTAL:
        preamble_entry = format_def(preamble_entry)

    return preamble_entry


def clean_preamble(preamble):
    preamble = [substitute_from_dict(preamble_entry, PREAMBLE_SUBS) for preamble_entry in preamble]
    full_preamble = PREAMBLE_HOTFIX + preamble
    preamble_lines = "\n".join(full_preamble)
    return preamble_lines


def prepare_js_json(paper_dict):
    preamble = paper_dict['preamble']
    preamble_lines = clean_preamble(preamble)
    paper_dict["preamble"] = preamble_lines
    paper_dict["preamble"] = paper_dict["preamble"].replace("\\newcommand*", "\\newcommand")  # TODO: why?
    for sec in paper_dict["sections"]:
        for eq in sec["equations"]:
            eq['latex'] = substitute_from_dict(eq["latex"], LATEX_SUBS)
            stripped = eq['latex'].strip(' ')

            has_line_break = ('&' in stripped and '&gt' not in stripped and '&lt' not in stripped) or r'\\' in stripped
            has_align_start = r'\begin{align' in stripped[:20]
            has_align_end = r'\end{align' in stripped[-20:]

            # there are several aligned envs like aligned, align and align*, the might be surrounded by \left, \right,
            # \tag, whitespaces or dots

            if has_line_break and not (has_align_start and has_align_end):
                eq["latex"] = r"\begin{aligned}" + eq['latex'] + r"\end{aligned}"

    return paper_dict


def call_js(paper_dict, paper_id=""):
    try:
        # if this runs with shell-escape somehow the nonstopmode is deactivated
        # maybe work with a timeout argument for run function.
        p, _ = os.path.split(__file__)
        # print(dict(preamble=preamble, latex_equations=latex_equations))
        result = subprocess.run(
            ["./tex2mathml.js"],
            input=json.dumps(
                # dict(preamble=preamble, latex_equations=latex_equations)
                paper_dict
            ),
            cwd=os.path.join(p),
            universal_newlines=True,
            text=True,
            capture_output=True,
            timeout=120
        )
        if result.stderr:
            if "Error in LaTeX:KaTeX parse error" in result.stderr:
                logging.debug("Compilation failed: {}".format(result.stderr))
            else:
                logging.warning(
                    "Unexpected error in tex2mathml.js (Arxiv ID: {}):".format(paper_dict["arxiv_id"]) + result.stderr)
        result = json.loads(result.stdout)
        result["preamble"] = result["preamble"].split("\n")
        return result
    except subprocess.TimeoutExpired:
        logging.warning("Timeout for paper {}: \n".format(paper_id) + "\n")
        return False


def compile_paper(paper_dict, paper_id="<string>"):
    """Compile all formulas from one arxiv-paper
    and the necessary packages/macros are stored."""
    paper_dict = prepare_js_json(paper_dict)
    paper_dict = call_js(paper_dict, paper_id=paper_id)
    return paper_dict


def compile_string(latex):
    """Use the same compilation pipeline to compile a string"""
    paper_dict = {
        "preamble": [],
        "sections": [{"equations": [{"latex": latex, "no": 0}]}]
    }
    paper_dict = compile_paper(paper_dict)
    print(paper_dict)
    mml = paper_dict["sections"][0]["equations"][0].get("mathml", None)
    if mml:
        return annotation_re.sub("", mml)
    return None


# if __name__ == "__main__":
#     FILE_PATH = "/mathml/1703.08475.json"
#     PAPER_ID = os.path.basename(FILE_PATH).replace(".json", "")
#     with open(FILE_PATH, 'r') as f:
#         P = json.load(f)
#         print(compile_paper(P, PAPER_ID))
#     print(compile_string("f(x) = x^2"))
