
def remove_comments(file_dict):
    """ Remove all commented statements from tex_string."""

    for path, text in file_dict.items():
        # There is one item that does not represent a file: the arxiv_id
        if path == "arxiv_id":
            continue

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
                    break
                else:
                    resulting_line += char

            result += resulting_line + "\n"

        file_dict[path] = result

    return file_dict
