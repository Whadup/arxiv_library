""" Query arxiv API for meta_data for the papers in the JSON_LOCATION. """
import arxiv
import os
import itertools
import json
from tqdm import tqdm
import re
import logging

# Get the meta_dat for CHUNK_SIZE papers at once
CHUNK_SIZE = 100

paper_version_re = re.compile(r"v[0-9]+$")

def format_id(txt_file):
    """ Until March 2007 arxiv-ids had a prefix that tells the archive and subject class of the paper.
    E. g. math.GT/0309136 (archive.subjet_class/yearmonthnumber). Our dirs with the tex-sources cannot
    be named like this because "/" is forbidden for UNIX-Paths. They are named like this math0309136.
    The arxiv API cannot deal with this format. So, this function translates our format into a
    format that is suitable for the arxiv API.
    """

    arxiv_id = txt_file.replace(".json", "")
    has_version_tag = paper_version_re.match(arxiv_id)
    assert has_version_tag is None, "WARNING your json files use arxiv-ids with version:" + arxiv_id
    first_char = arxiv_id[0]

    if first_char.isdigit():
        return arxiv_id
    else:
        subject, no = ["".join(x) for _, x in itertools.groupby(arxiv_id, key=str.isdigit)]
        return subject + "/" + no


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def store_meta_data_chunk(response, overwrite=False, test_dir=None):
    """ Take a list of responeses and store the retrieved data in the respective json-files. """
    for paper in response:

        # retrieve id in the format that we can store locally (See description of format_id).
        # paper['id'] gives the url under which the paper (more precis is abstract [abs/]) is available.
        paper_id = paper["id"].split("abs/")[1].replace("/", "")
        paper_id = paper_version_re.sub("", paper_id)

        if test_dir:
            out_file_path = os.path.join(test_dir, paper_id + ".json")
        else:
            out_file_path = os.path.join(c.JSON_LOCATION, paper_id + ".json")

        # Since we fetch meta_data for all papers for that we have json files,
        # there should be json file for the id that we extracted from the response
        assert os.path.isfile(out_file_path), "There is no file for the id extracted from an arxiv api response. The file should be: " + out_file_path

        paper_dict = None
        with open(out_file_path, 'r') as f:
            paper_dict = json.load(f)

        stored_id = paper_dict.get('id', None)
        if stored_id is not None and not overwrite:
            logging.info("The file {} already exists with the respective entries. Overwrite option is off. Skipping...".format(out_file_path))
            continue

        with open(out_file_path, 'w') as f:
            paper_dict.update(paper)
            json.dump(paper_dict, f, indent=4, sort_keys=True)


def get_all_meta_data(paper_ids, test_dir=None):
    id_chunks = chunks(paper_ids, CHUNK_SIZE)

    for chunk in tqdm(id_chunks):
        resp = arxiv.query(id_list=chunk)
        store_meta_data_chunk(resp, test_dir=test_dir)


if __name__ == '__main__':
    logging.basicConfig(filename="extract_meta_data.log", level=logging.INFO)
    paper_ids = [format_id(paper_id) for paper_id in os.listdir(c.JSON_LOCATION)]
    get_all_meta_data(paper_ids)
