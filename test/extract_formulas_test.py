import os
from extract_formulas import extract_from_arxiv_dir
from test_util import assert_files_are_equal
import shutil

input_dir = "test_ressources/extract_formula_input"
output_dir = "test_ressources/extract_formula_output"
tmp_dir = "test_ressources/tmp_dir_formula"



if __name__ == "__main__":
    os.mkdir(tmp_dir)
    arxiv_dirs = os.listdir(input_dir)
    for arxiv_dir in arxiv_dirs:
        extract_from_arxiv_dir(arxiv_dir, test_indir=input_dir, test_outdir=tmp_dir) 

        output_path = os.path.join(tmp_dir, arxiv_dir + ".json")
        exp_out_path = os.path.join(output_dir, arxiv_dir + ".json")
        assert_files_are_equal(output_path, exp_out_path)

    shutil.rmtree(tmp_dir)
    print("Test was succesful :)")
