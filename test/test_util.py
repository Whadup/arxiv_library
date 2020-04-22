

def assert_files_are_equal(out_path, expected_out_path):
    output = open(out_path).read().split("\n")
    expected_output = open(expected_out_path).read().split("\n")
    for i in range(len(output)):
        expected = expected_output[i]
        if "\"base\"" in expected:
            continue
        got = output[i]
        assert got == expected, "Lines \n {} \n and \n {} \n do not match".format(got, expected) + "for file: {}".format(out_path) 
