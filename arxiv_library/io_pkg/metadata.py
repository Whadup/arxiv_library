import arxiv
import os
import itertools
import json
import re
import logging


_paper_version_tag = re.compile(r"v[0-9]+$")


def id_from_filename(filename):
    """ Until March 2007 arxiv-ids had a prefix that tells the archive and subject class of the paper. E.g.
    math.GT/0309136 (archive.subjet_class/yearmonthnumber). Our dirs with the tex-sources cannot be named like this
    because "/" is forbidden for UNIX-Paths. They are named like this math0309136. The arxiv API cannot deal with this
    format. This function translates our format into a format that is suitable for the arxiv API.
    """

    if _paper_version_tag.match(filename):
        raise ValueError('Found version tag in file name {}, no version tags allowed.'.format(filename))

    filename = filename.replace('.json', '')

    if filename[0].isdigit():
        return filename

    return '/'.join(["".join(x) for _, x in itertools.groupby(filename, key=str.isdigit)])


def receive_meta_data(arxiv_ids, folder=None, overwrite=False, chunk_size=100):
    results = []
    # split arxiv_ids into a list of chunks with len of chunk_size
    chunk_generator = (arxiv_ids[i:i+chunk_size] for i in range(0, len(arxiv_ids), chunk_size))
    for chunk in chunk_generator:
        response = arxiv.query(id_list=chunk)

        for paper in response:
            # retrieve id in the format that we can store locally (See description of format_id). paper['id'] gives the
            # url under which the paper (more precis is abstract [abs/]) is available

            paper_id = paper["id"].split("abs/")[1].replace("/", "")
            paper_id = _paper_version_tag.sub("", paper_id)
            paper_path = os.path.join(folder, paper_id + ".json")

            results.append(paper)

            # if no folder is given we don't save the results and just return the responses

            if not folder:
                continue

            # Since we fetch meta_data for all papers for that we have json files, there should be json file for the
            # id that we extracted from the response

            if not os.path.isfile(paper_path):
                raise ValueError('Could not find paper file {} when trying to recieve meta data.'.format(paper_path))

            with open(paper_path, 'r') as file:
                paper_dict = json.load(file)

            stored_id = paper_dict.get('id', None)

            if stored_id is not None and not overwrite:
                logging.info('The file {} already exists. Overwrite option is off.'.format(paper_path))
                continue

            with open(paper_path, 'w') as file:
                paper_dict.update(paper)
                json.dump(paper_dict, file, indent=4, sort_keys=True)

    return results
