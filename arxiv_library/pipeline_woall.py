import json
import preprocessing.comments
import preprocessing.imports
import extraction.preamble
import extraction.sections
import extraction.equations
import extraction.citations
import compilation.mathml
import io_pkg.metadata
import io_pkg.targz
import io_pkg.paths

# test_data = '/home/jan/Experiment'
# file_dicts = []
#
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

# io_pkg.paths.set_path('tmp_tar', '/home/jan/arxiv_lib/temp')
# # file_dicts = io_pkg.targz.extract_arxiv_month('/home/jan/Experiments/DataSets/arXiv_src_1810_012.tar')
# file_dicts = []
#
# with io_pkg.targz.TarMonthExtractor('/home/jan/Experiments/DataSets/arXiv_src_1810_012.tar') as paths:
#     for path in paths:
#         file_dicts.append(io_pkg.targz.gz_to_file_dict(path))
#
#
# with open('/home/jan/temp.json', 'w') as file:
#     json.dump(file_dicts, file)


with open('/home/jan/temp.json', 'r') as file:
    file_dicts = json.load(file)

# TODO sicherstellen, dass in allen teilen mit leeren paper dicts richtig umgegangen wird

paper_dicts = []

for file_dict in file_dicts:
    file_dict = preprocessing.comments.remove_comments(file_dict)
    paper_dict = preprocessing.imports.resolve_imports(file_dict)

    paper_dict = extraction.preamble.extract_preamble(paper_dict)
    paper_dict = extraction.sections.extract_sections(paper_dict)
    paper_dict = extraction.equations.extract_equations(paper_dict)
    paper_dict = extraction.citations.extract_citations(paper_dict)

    paper_dict = compilation.mathml.compile_equations(paper_dict)

    paper_dicts.append(paper_dict)

arxiv_ids = [pd['arxiv_id'] for pd in paper_dicts]
response = io_pkg.metadata.recieve_meta_data(arxiv_ids)

dir(response[0])
