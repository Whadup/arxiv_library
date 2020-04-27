
def rm_comms(tex_string):
    """ Remove all commented statements from tex_string."""
    lines = tex_string.split("\n")
    resulting_lines = ""
    for line in lines:
        res_line = rm_comm_in_line(line)
        resulting_lines += res_line + "\n"

    return resulting_lines


def rm_comm_in_line(line):
    """remove comments in line"""
    escaped = False
    resulting_line = ""

    for ch in line:
        if escaped:
            escaped = False
            resulting_line += ch
        elif ch == '\\':
            escaped = True
            resulting_line += ch
        elif ch == '%':
            return resulting_line
        else:
            resulting_line += ch

    return resulting_line