"""Functions for translating tex equations into png images via pdflatex and ghostscript"""
import os
import subprocess
import re
import logging
import config as c


SECTION_RE = re.compile(r"\*\*(.*?)\*\*")

DOCUMENT = """\\DOCUMENTclass{{standalone}}
{preamble}
\\begin{{DOCUMENT}}
\\begin{{minipage}}[c][3cm]{{15cm}}
{equation}
\\end{{minipage}}
\\end{{DOCUMENT}}
"""

NO_PREAMBLE = 3
NO_DUPLICATE_PREAMBLE = 2
FULL_PREAMBLE = 1

PREAMBLE_RE = re.compile(c.BEGIN_PREAMBLE + "(.*?)" + c.END_PREAMBLE, re.DOTALL)


def compile_one_eq(data):
    """Compiles a single equation given as 'job_no, eq, preamble, current_dir'"""
    job_no, eq, preamble, current_dir = data

    tex_file_name = str(job_no) + ".tex"
    out_tex_file = os.path.join(current_dir, tex_file_name)

    with open(out_tex_file, 'w') as f:
        tex = DOCUMENT.format(equation=eq, preamble=preamble)
        f.write(tex)

    try:
        # if this runs with shell-escape somehow the nonstopmode is deactivated
        # maybe work with a timeout argument for run function.
        subprocess.run(["pdflatex", "-interaction=nonstopmode", out_tex_file],
                        cwd=current_dir, universal_newlines=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, timeout=2)
        pdf_file = out_tex_file.replace(".tex", ".pdf")

        if os.path.isfile(pdf_file):

            png_file = pdf_file.replace(".pdf", ".png")
            subprocess.run(["gs", "-dSAFER", "-dBATCH", "-dNOPAUSE",
                            "-sDEVICE=pngalpha", "-r90", "-sOutputFile=" + png_file, pdf_file],
                            cwd=current_dir, universal_newlines=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, timeout=2)
            # ghostscript_status = "PNG_SUCCES" if png_result.returncode == 0 else "PNG_FAIL"

        else:
            logging.warning("PDF Fail with %s", pdf_file)
    except subprocess.TimeoutExpired:
        logging.warning("Timeout with file %s", out_tex_file)


def compile_eqs_in_paper(extracted_eqs_file):
    """Compile all formulas from one arxiv-paper
    :param extracted_eqs_file: Path to file where all the formulas
    and the necessary packages/macros are stored."""
    with open(extracted_eqs_file, 'r') as file:

        arxiv_id = os.path.basename(file.name)
        arxiv_id, _ = os.path.splitext(arxiv_id)

        arxiv_dir = os.path.join(c.PNG_LOCATION, arxiv_id)

        os.mkdir(arxiv_dir)

        preamble_lines = ""

        file_content = file.read()

        preamble_match = PREAMBLE_RE.search(file_content)

        whole_match = preamble_match.group()
        preamble_lines = preamble_match.groups()[0]

        file_content = file_content.replace(whole_match, "")

        for line in file_content.split("\n"):
            section_match = SECTION_RE.match(line)

            if section_match:
                eq_counter = 0
                curr_sec = section_match.groups()[0]

            elif not line:
                pass

            else:
                eq_name = curr_sec + "_" + str(eq_counter)
                eq_counter += 1
                data = eq_name, line, preamble_lines, arxiv_dir
                compile_one_eq(data)
