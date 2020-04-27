
def remove_comments(tex_string):
    """ Remove all commented statements from tex_string."""

    lines = tex_string.split("\n")
    result = ''

    for line in lines:
        escaped = False
        resulting_line = ''

        for char in line:
            if escaped:
                escaped = False
                resulting_line += char
            elif char == '\\':
                escaped = True
                resulting_line += char
            elif char == '%':
                return resulting_line
            else:
                resulting_line += char

        result += resulting_line + "\n"

    return result
