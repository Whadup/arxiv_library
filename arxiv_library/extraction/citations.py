import re

_latex_bibliography = re.compile(r'\\begin{thebibliography}(\{[0-9]*\})?(.*?)\\end{thebibliography}')
_latex_bibitem = re.compile(r'\\bibitem(?:\[[^\]]*\])?\{[^\}]*\}')

_arxiv_id_new = re.compile(r"(?P<id>[0-9]{4}[.]+[0-9]{4,5})(?P<version>v[0-9]+)?")
_arxiv_ids_old = [r"astro\-ph(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"astro\-ph(?P<dotseparator>[. -]+)(GA|CO|EP|HE|IM|SR)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"cond\-mat(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"cond\-mat(?P<dotseparator>[. -]+)(dis\-nn|mtrl\-sci|mes\-hall|other|quant\-gas|soft|stat\-mech|str\-el|supr\-con)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"gr\-qc(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"hep\-(ex|lat|ph|th)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"math\-ph(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"nlin(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"nlin(?P<dotseparator>[. -]+)(AO|CG|CD|SI|PS)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"nucl\-(ex|th)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"physics(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"physics(?P<dotseparator>[. -]+)(acc\-ph|app\-ph|ao\-ph|atm\-clus|atom\-ph|bio\-ph|chem\-ph|class\-ph|comp\-ph|data\-an|flu\-dyn|gen\-ph|geo\-ph|hist\-ph|ins\-det|med\-ph|optics|soc\-ph|ed\-ph|plasm\-ph|pop\-ph|space\-ph|quant\-ph)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"(acc\-ph|app\-ph|ao\-ph|atm\-clus|atom\-ph|bio\-ph|chem\-ph|class\-ph|comp\-ph|data\-an|flu\-dyn|gen\-ph|geo\-ph|hist\-ph|ins\-det|med\-ph|optics|soc\-ph|ed\-ph|plasm\-ph|pop\-ph|space\-ph|quant\-ph)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"math(?P<dotseparator>[. -]+)(AG|AT|AP|CT|CA|CO|AC|CV|DG|DS|FA|GM|GN|GT|GR|HO|IT|KT|LO|MP|MG|NT|NA|OA|OC|PR|QA|RT|RA|SP|ST|SG)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"cs(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"cs(?P<dotseparator>[. -]+)(AI|CL|CC|CE|CG|GT|CV|CY|CR|DS|DB|DL|DM|DC|ET|FL|GL|GR|AR|HC|IR|IT|LO|LG|MS|MA|MM|NI|NE|NA|OS|OH|PF|PL|RO|SI|SE|SD|SC|SY)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"q\-bio(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"q\-bio(BM|CB|GN|MN|NC|OT|PE|QM|SC|TO)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"q\-fin(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"q\-fin(CP|EC|GN|MF|PM|PR|RM|ST|TR)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"stat(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"stat(AP|CO|ML|ME|OT|TH)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"eess(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"eess(AS|IV|SP|SY)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"econ(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?",
    r"econ(?P<dotseparator>[. -]+)(EM|GN|TH)(?P<slashseparator>[. /]+)[0-9]{7}(?P<version>v[0-9]+)?"
]
_arxiv_ids_old = [re.compile(regex) for regex in _arxiv_ids_old]


def extract_citations(paper_dict):
    tex_string = paper_dict['paper']
    # bib_string = _latex_bibliography.search(tex_string).groups()[-1]  # brauch man das ueberhaupt?
    bib_items = _latex_bibitem.split(tex_string)
    bib_ids = set()

    for item in bib_items:
        match = _arxiv_id_new.search(item)

        if not match:
            for regex in _arxiv_ids_old:
                match = regex.search(item)

                if match is not None:
                    break

        if match is not None:
            bib_ids.add(match.group(0))

    paper_dict['citations'] = bib_ids
    return paper_dict
