import json
import preprocessing.comments
import preprocessing.imports
import extraction.preample
import extraction.sections
import extraction.equations
import extraction.citations


# for folder in os.listdir(test_data)[:1]:
#     file_dict = {}
#
#     for root, dirs, files in os.walk(os.path.join(test_data, folder)):
#         for file in files:
#             if file.endswith('bbl') or file.endswith('tex'):
#                 full_path = os.path.join(root, file)
#                 relative_path = full_path.replace(test_data, '')
#                 relative_path = relative_path.replace(folder, '')[2:]  # hack
#
#                 with open(full_path, 'r') as f:
#                     string = f.read()
#
#                 file_dict[relative_path] = string
#     file_dicts.append(file_dict)

# file_dicts = io_pkg.archive_extraction.extract_arxiv_month('/home/jan/Experiments/DataSets/arXiv_src_1810_012.tar',
#                                                            '/home/jan/temparxiv')
#
# with open('/home/jan/temp.json', 'w') as file:
#     json.dump(file_dicts, file)


with open('/home/jan/temp.json', 'r') as file:
    file_dicts = json.load(file)


paper_dicts = []
