import arxiv
import itertools
import re
import os
import json
import argparse


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


def receive_meta_data(paper_dicts, chunk_size=100):
    arxiv_ids = [paper_dict['arxiv_id'] for paper_dict in paper_dicts]
    chunk_generator = (arxiv_ids[i:i+chunk_size] for i in range(0, len(arxiv_ids), chunk_size))

    for chunk in chunk_generator:
        response = arxiv.query(id_list=chunk)

        for paper in response:
            # retrieve id in the format that we can store locally (See description of format_id). paper['id'] gives the
            # url under which the paper (more precis is abstract [abs/]) is available

            paper_id = paper["id"].split("abs/")[1].replace("/", "")
            paper_id = _paper_version_tag.sub("", paper_id)

            for paper_dict in paper_dicts:
                if paper_id == paper_dict['arxiv_id']:
                    paper_dict['metadata'] = paper
                    break

    return paper_dicts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')  # TODO description

    parser.add_argument(
        'src_path',
        help='the folder where the json files are located',
        type=str
    )
    parser.add_argument(
        'target_path',
        help='the folder where the results will be stored',
        type=str
    )
    parser.add_argument(
        '-overwrite',
        help='when set, the old files will be overwritten and target path will be ignored',
        action='store_true'
    )

    args = parser.parse_args()

    json_paths = os.listdir(args.src_path)
    cache = []

    for i, path in enumerate(json_paths):
        try:
            with open(os.path.join(args.src_path, path), 'r') as file:
                cache.append(json.load(file))

        except Exception as exception:
            print(exception)

        if len(cache) > 100 or i == len(json_paths) - 1:
            paper_dicts = receive_meta_data(cache)

            for paper_dict in paper_dicts:
                with open(os.path.join(args.target_path, '{}.json'.format(paper_dict['arxiv_id'])), 'w') as file:
                    json.dump(paper_dict, file)
