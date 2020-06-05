import arxiv
import itertools
import re


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
    else:
        return '/'.join(["".join(x) for _, x in itertools.groupby(filename, key=str.isdigit)])


def receive_meta_data(paper_dicts, chunk_size=100):
    arxiv_ids = [id_from_filename(paper_dict['arxiv_id']) for paper_dict in paper_dicts]
    chunk_generator = (arxiv_ids[i:i+chunk_size] for i in range(0, len(arxiv_ids), chunk_size))

    for chunk in chunk_generator:
        response = arxiv.query(id_list=chunk)

        for paper in response:
            # retrieve id in the format that we can store locally (See description of format_id). paper['id'] gives the
            # url under which the paper (more precis is abstract [abs/]) is available

            paper_id = paper["id"].split("abs/")[1].replace("/", "")
            paper_id = _paper_version_tag.sub("", paper_id)

            meta_data_set = False

            for paper_dict in paper_dicts:
                if paper_id == paper_dict['arxiv_id']:
                    paper_dict['metadata'] = paper
                    meta_data_set = True
                    break
            assert meta_data_set, "Meta data was not set for Arxiv ID: {}".format(paper_id)

    return paper_dicts
