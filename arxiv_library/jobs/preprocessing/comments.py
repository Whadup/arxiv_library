
def remove_comments(file_dict):
    """ Remove all commented statements from tex_string."""

    for path, text in file_dict.items():
        text = text.split("\n")
        result = ''

        for line in text:
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

        file_dict[path] = result
