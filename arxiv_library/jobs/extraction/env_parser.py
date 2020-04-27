"""
This module offers a function extract_env that takes a string with tex code as an argument
and returns a generator that yields all mathematical environments from that tex code.
"""
import re 


ENV_END_TEMPLATE = r"\\end{}"
ENV_BEGIN_TEMPLATE = r"\\begin{}"

BEGIN_ENVS = [re.compile(r"\$\$"), re.compile(r"\\\[")]
BEGIN_ENVS_IDS = ["equation", "displaymath", "array", "eqnarray", "multline", "gather", "align", "flalign"]

TABULAR_ALIGNING_RE = r"\{[l,c,r,\|,\s]*?\}"
# construct REs for all possible env beginnings
for env_id in BEGIN_ENVS_IDS:
    env_begin_re = re.compile(ENV_BEGIN_TEMPLATE.format("{" + env_id + "}"))
    env_begin_re_star = re.compile(ENV_BEGIN_TEMPLATE.format("{" + env_id + r"\*}"))
    BEGIN_ENVS.append(env_begin_re)
    BEGIN_ENVS.append(env_begin_re_star)

identifier_re = re.compile(r"\\begin{(.*?)}")


def extract_envs(tex_string):
    """
    Yield all outer math-environments contained in the given tex_string.
    Outer means that a math-env that is inside another math-env (e. g. split)
    will not be yielded singularly.
    """

    # split string into lines
    all_lines = tex_string.split("\n")

    # This function has two states (<inside a math env> and <not inside a math env>)
    # which are determined by this bool value
    is_in_math_env = False
    # If is_in_math_env is true (the current line is inside a math env)
    # current_env_identifier stores the identifier of this env
    current_env_identifier = ""
    # current_env stores the lines of the env in that we are currently (if we are in an env)
    current_env = ""

    for line in all_lines:

        # State: <inside a math env>
        if is_in_math_env:
            match = scan_for_env_end(line, current_env_identifier)
            # if the current line ends the math env in that we are at the moment...
            if match:
                is_in_math_env = False
                current_env_identifier = ""

                line = cut_after_env_end(line, match)
                current_env = current_env.lstrip().rstrip()
                yield current_env
            # if the env is not ended yet, append the current line to the current_env
            else:
                current_env += "\n" + line

        # State: <not inside a math env>
        else:
            match = scan_for_env_begin(line)
            if match:
                is_in_math_env = True
                line = cut_before_env_begin(line, match)

                env_begin = match.group()
                current_env = line.replace(env_begin, "")
                current_env = re.sub(TABULAR_ALIGNING_RE, "", current_env)
                current_env_identifier = get_identifier(line)

                # this env could be closed in the same line (So, we check for that)
                match_end = scan_for_env_end(line, current_env_identifier)
                if match_end:
                    is_in_math_env = False
                    current_env_identifier = ""

                    env_end = match_end.group()
                    current_env = current_env.replace(env_end, "")
                    current_env = current_env.lstrip().rstrip()
                    yield current_env


def scan_for_env_end(line, current_env_identifier):
    # construct an re that matches a string that would terminate our current env
    if current_env_identifier == r"$$":
        env_end_re = r"\$\$"
    elif current_env_identifier == r"\]":
        env_end_re = r"\\\]"
    else:
        env_end_re = ENV_END_TEMPLATE.format("{" + current_env_identifier + "}")
    # return the match object (will be None if there is no match)
    match = re.search(env_end_re, line)
    return match


def scan_for_env_begin(line):
    for env_begin_re in BEGIN_ENVS:
        match = env_begin_re.search(line)
        if match:
            return match
    return None


def cut_after_env_end(line, match):
    cutted_line = line[:match.end()]
    return cutted_line


def cut_before_env_begin(line, match):
    cutted_line = line[match.start():]
    return cutted_line


def get_identifier(line):
    """
    This function is called with a string as an argument that contains the beginning of
    a math-environment. It returns the identifier of this env.
    """
    match = identifier_re.search(line)
    if match:
        identifier = match.groups()[0]
        identifier = identifier.replace("*", "\*")
        return identifier
    if "$$" in line:
        return r"$$"
    elif "\[" in line:
        return r"\]"
    else:
        return None
