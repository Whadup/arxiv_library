import os
import json
import argparse


out_file = "stat.json"


def count(json_dir):
    json_files = [os.path.join(json_dir, j_file) for j_file in os.listdir(json_dir)]

    latex_sum = 0
    mathml_sum = 0
    category_dict = dict()

    for i, json_file in enumerate(json_files, 1):
        latex_count = 0
        mathml_count = 0

        with open(json_file) as jf:
            paper_dict = json.load(jf)
            for section in paper_dict['sections']:
                for eq in section['equations']:
                    latex_count += 1 if eq['latex'] else 0
                    mathml_count += 1 if eq.get('mathml') else 0

            latex_sum += latex_count
            mathml_sum += mathml_count
            category = paper_dict['metadata']['arxiv_primary_category']['term']
            category_dict[category] = category_dict.get(category, 0) + 1

    compile_ratio = mathml_sum / latex_sum

    result_dict = {
        'total_papers': len(json_files),
        'total_latex': latex_sum,
        'total_mathml': mathml_sum,
        'compile_ratio': compile_ratio
    }
    result_dict.update(category_dict)

    print(json.dumps(result_dict, indent=4))

    with open(out_file, 'w') as f:
        json.dump(result_dict, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'json_path',
        help='The directory where the resulting json files are stored',
        type=str)
    args = parser.parse_args()
    count(args.json_path)
