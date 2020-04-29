import os
import preprocessing.comments
import preprocessing.imports
import extraction.preample
import extraction.sections
import extraction.equations
import extraction.citations


test_data = '/home/jan/Experiments/DataSets/arxivlib_test_data'
file_dicts = []

for folder in os.listdir(test_data)[:1]:
    print(folder)
    file_dict = {}

    for root, dirs, files in os.walk(os.path.join(test_data, folder)):
        for file in files:
            if file.endswith('bbl') or file.endswith('tex'):
                full_path = os.path.join(root, file)
                relative_path = full_path.replace(test_data, '')
                relative_path = relative_path.replace(folder, '')[2:]  # hack

                with open(full_path, 'r') as f:
                    string = f.read()

                file_dict[relative_path] = string

    file_dicts.append(file_dict)


file_dicts = [preprocessing.comments.remove_comments(f) for f in file_dicts]
paper_dicts = [preprocessing.imports.resolve_imports(f) for f in file_dicts]

paper_dicts = [extraction.preample.extract_preamble(p) for p in paper_dicts]
paper_dicts = [extraction.sections.extract_sections(p) for p in paper_dicts]
paper_dicts = [extraction.equations.extract_equations(p) for p in paper_dicts]
paper_dicts = [extraction.citations.extract_citations(p) for p in paper_dicts]

print(paper_dicts[0]['preamble'])
print(len(paper_dicts[0]['sections']))
print(paper_dicts[0]['sections'])
print(paper_dicts[0]['equations'])
print(paper_dicts[0]['citations'])
