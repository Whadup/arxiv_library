import re

_latex_section = re.compile(r"\\section\{(.*?)\}")


def extract_sections(paper_dict):
    tex_string = paper_dict['paper']
    sections = {}
    indices = []  # (start, end)

    while True:
        next_section = _latex_section.search(tex_string)

        if next_section is None:
            break

        indices.append((next_section.start(), next_section.end()))

    for i in range(len(indices)):
        section_start = indices[i][1]
        section_end = indices[i+1][0] if i+1 < len(indices) else len(tex_string)
        sections[i] = tex_string[section_start:section_end]

    paper_dict['sections'] = sections
