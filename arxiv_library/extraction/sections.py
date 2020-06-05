import re

_latex_section = re.compile(r"\\section\{(.*?)\}")


def extract_sections(paper_dict):
    tex_string = paper_dict['paper']
    paper_dict['sections'] = []
    names = []
    indices = []

    for match in re.finditer(_latex_section, tex_string):
        names.append(match.groups()[0])
        indices.append((match.start(), match.end()))

    for i in range(len(indices)):
        section_start = indices[i][1]
        section_end = indices[i+1][0] if i+1 < len(indices) else len(tex_string)

        paper_dict['sections'].append({
            'name': names[i],
            'equations': [],
            'latex': tex_string[section_start:section_end]
        })

    return paper_dict
