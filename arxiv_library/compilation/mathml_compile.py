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
PREAMBLE_HOTFIX = [r"\newcommand{\label}[1]{}",
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

PREAMBLE_SUBS  = {
        r"\boldmath" : r"\bf",
        r"\DeclareMathOperator" : r"\newcommand"
        }

LATEX_SUBS = {
        r"\begin{split}" : "",
        r"\end{split}" : ""
        }


def format_def(preamble_entry):
    match = def_re.match(preamble_entry)
    if match:
        residual = def_re.sub("", preamble_entry)
        groups = match.groups()
        return groups[0] + "#1"+ residual
    else:
        return preamble_entry

def substitute_from_dict(preamble_entry, sub_dict):
    for key, value in sub_dict.items():
        preamble_entry = preamble_entry.replace(key, value)

    if EXPERIMENTAL:
        preamble_entry = format_def(preamble_entry)

    return preamble_entry


def compile_one_eq(eq, preamble, paper_id):
    """Compiles a single equation given as eq and preamble"""
    job_no = eq['no']
    mathml_file_name = str(job_no) + ".kmathml"
    latex = eq["latex"]
    latex = substitute_from_dict(latex, LATEX_SUBS)
    # The eq might be a tabbed multiline equation with (&s and \\s).
    # To handle this we surround the formula with the aligned env. This env is supported by katex.
    latex = preamble + "\n" + r"\begin{aligned}" + latex + r"\end{aligned}"
    latex = latex.replace("\\newcommand*", "\\newcommand")
    try:
        # if this runs with shell-escape somehow the nonstopmode is deactivated
        # maybe work with a timeout argument for run function.
        p, _ = os.path.split(__file__)
        result = subprocess.run(["js/tex2mathml.js",
                                latex 
                                ],
                                cwd=os.path.join(p),
                                universal_newlines=True,
                                text=True,
                                capture_output=True,
                                timeout=120)
        if result.returncode != 0:
            logging.error("Non-zero returncode for eq no. {} in paper {}: \n\t".format(job_no, paper_id) +\
                    result.stderr) 
            return False
        else:
            eq["mathml"] = annotation_re.sub('', result.stdout)
            return True
    except subprocess.TimeoutExpired:
        logging.warning("Timeout for eq no. {} in paper {}: \n".format(job_no, paper_id) + "\n")
        return False

def clean_preamble(preamble):
    preamble = [substitute_from_dict(preamble_entry, PREAMBLE_SUBS) for preamble_entry in preamble]
    full_preamble = PREAMBLE_HOTFIX + preamble
    preamble_lines = "\n".join(full_preamble)
    return preamble_lines

def compile_eqs_in_paper(extracted_eqs_file):
    """Compile all formulas from one arxiv-paper
    :param extracted_eqs_file: Path to file where all the formulas
    and the necessary packages/macros are stored."""
    paper_dict = None
    paper_id = os.path.basename(extracted_eqs_file).replace(".json", "")
    with open(extracted_eqs_file, 'r') as f:
                paper_dict = json.load(f)

                preamble = paper_dict['preamble']
                preamble_lines = clean_preamble(preamble)

                sections = paper_dict['sections']
                for section in sections:
                    eqs = section["equations"]
                    for eq in eqs:
                        compile_one_eq(eq, preamble_lines, paper_id)

    with open(extracted_eqs_file, 'w') as f:
        json.dump(paper_dict, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    file_path = "/home/schill/arxiv/json_db_old/1505.06478.json"
    with open(file_path) as f:
        pd = json.load(f)
        eq = pd["sections"][1]['equations'][0]
        preamble = pd["preamble"]
        preamble = [substitute_from_dict(preamble_entry, PREAMBLE_SUBS) for preamble_entry in preamble]
        full_preamble = PREAMBLE_HOTFIX + preamble
        preamble_lines = "\n".join(full_preamble)
        compile_one_eq(eq, preamble_lines, "xxxx.xxxx")
