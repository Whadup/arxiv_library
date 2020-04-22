from extract_meta_data import get_all_meta_data, format_id
import os
import shutil
from test_util import assert_files_are_equal

input_dir = "test_ressources/meta_data_input"
output_dir = "test_ressources/meta_data_output"
tmp_dir = "test_ressources/meta_data_tmp_dir"
input_files = os.listdir(input_dir)
paper_ids = [format_id(paper_id) for paper_id in input_files] 


if __name__ == "__main__":
    shutil.copytree(input_dir, tmp_dir)
    get_all_meta_data(paper_ids, test_dir=tmp_dir)

    for input_file in input_files:
        output_path = os.path.join(tmp_dir, input_file)
        exp_out_path = os.path.join(output_dir, input_file)
        assert_files_are_equal(output_path, exp_out_path)


    shutil.rmtree(tmp_dir)
    print("Test was succesful :)")
    
