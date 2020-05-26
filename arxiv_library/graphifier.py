import os
import tqdm
import json
import argparse


class Graph:
    """
    A simple graph class to represent the citation dependencies of the arxiv papers. Each node represents a paper.
    nodes is a list where nodes[i] is a list of neighbor indices j of node i. arxiv_ids is a list, where arxiv_ids[i]
    gives the arxiv id of node i. node_ids is a dictionary that returns the node id i for an arxiv id. attributes
    is a dictionary that returns a dictionary of attributes for node id i. Nodes can be added to the list with a
    unique (arxiv) id, the node id is determined by the order of additions starting with 0.
    """

    def __init__(self):
        self.nodes = []  # i -> [neighbour indices of i]
        self.arxiv_ids = []  # i -> arxiv_id
        self.node_ids = {}  # arxiv_id -> i, fast check if id already exists
        self.attributes = {}  # i -> {arxiv_id, authors, published, title, arxiv_primary_category}

    def add(self, arxiv_id):
        """
        Adds a node to the graph. Each node represents a paper.
        :param arxiv_id: The id can be of any format, but should follow the arxiv id convetion, since it will be stored
        under arxiv_id as attribute of the node, see https://arxiv.org/help/arxiv_identifier.
        """

        if arxiv_id not in self.node_ids:
            self.nodes.append(set())
            self.arxiv_ids.append(arxiv_id)
            self.node_ids[arxiv_id] = len(self.nodes) - 1
            self.attributes[len(self.nodes) - 1] = {'arxiv_id': arxiv_id}

    def link(self, arxiv_id_a, arxiv_id_b):
        """
        Adds an edge from node with id a to the node with id b. The graph assumes to be directed, so for an undirected
        graph a reverse edge should be added. The ids should be the same ids under which the nodes have been added to
        the graph.
        """

        index_a = self.node_ids[arxiv_id_a]
        index_b = self.node_ids[arxiv_id_b]
        self.nodes[index_a].add(index_b)

    def size(self):
        """
        Returns the amount of nodes in the graph.
        """

        return len(self.nodes)

    def add_attribute(self, arxiv_id, key, value):
        """
        Adds an attribute to a node specified by the given id. The graphifier.save(..) function stores attributes like
        this: 'key: value, key: value,..'. The ids should be the same ids under which the nodes have been added to
        the graph.
        """

        if arxiv_id not in self.node_ids:
            return

        self.attributes[self.node_ids[arxiv_id]][key] = value

    def str_attributes(self, node_id):
        """
        Returns a string representation of the attributes of the specified node. The node id does not correspond to
        the id under which the node has been added to the file, but rather the internal integer id of the given node!
        The string representation looks like 'key: value, key: value,..'. The internal id is given by the index of the
        node in self.nodes (the ith node added to the graph will have index i).
        """

        return ', '.join(['{}: {}'.format(key, value) for key, value in self.attributes[node_id].items()])


def build(source_path):
    """
    Builds a citation graph from json data compiled by the pipeline. For the graph structure have a look at the graph
    class documentation. Each node represents a paper and has attributes authors, title, published, category and
    arxiv_id.
    :param source_path: The directory where the json paper dict files are located
    :return: Returns an object of type graphifier.Graph
    """

    graph = Graph()

    for path in tqdm.tqdm(os.listdir(source_path)):
        try:
            arxiv_id = path.replace('.json', '')
            path = os.path.join(args.json_path, path)

            with open(path, 'r') as file:
                paper_dict = json.load(file)

            graph.add(arxiv_id)

            for key in ['authors', 'title', 'published', 'arxiv_primary_category']:
                if 'metadata' in paper_dict and key in paper_dict['metadata']:
                    if key == 'authors':
                        paper_dict['metadata'][key] = '/'.join(paper_dict['metadata'][key])

                    if key == 'title':
                        paper_dict['metadata'][key] = paper_dict['metadata'][key].replace('\n', '')

                    if key == 'arxiv_primary_category':
                        paper_dict['metadata'][key] = paper_dict['metadata'][key]['term']

                    graph.add_attribute(arxiv_id, key, paper_dict['metadata'][key])

            for bib_id in paper_dict['citations']:
                graph.add(bib_id)
                graph.link(arxiv_id, bib_id)

        except Exception as exception:
            print(exception)

    return graph


def save(graph, dataset_path):
    """
    Takes an object of type graphifier.Graph and stores a corresponding dataset at the specified location. For the
    format of the dataset see https://chrsmrrs.github.io/datasets/docs/format/ for reference, where DS=arxiv_citations.
    This function generates a file arxiv_citations_node_attributes.txt aside from the required files, where the
    attributes specified in build() are stored.
    :param graph: An object of type graphifier.Graph, can be generated with graphifier.build(..)
    :param dataset_path: The location where the dataset should be stored
    """

    # n = total number of nodes
    # m = total number of edges
    # N = number of graphs

    # DS_A.txt (m lines): sparse (block diagonal) adjacency matrix for all graphs, each line corresponds to (row, col)
    # resp. (node_id, node_id)

    with open(os.path.join(dataset_path, 'arxiv_citations_A.txt'), 'w') as file:
        for source in range(graph.size()):
            for target in graph.nodes[source]:
                file.write('({}, {})\n'.format(source, target))

    # DS_node_labels.txt (n lines): column vector of node labels, the value in the i-th line corresponds to the node
    # with node_id i

    with open(os.path.join(dataset_path, 'arxiv_citations_node_labels.txt'), 'w') as file:
        file.write('0\n' * graph.size())

    # DS_graph_indicator.txt (n lines): column vector of graph identifiers for all nodes of all graphs, the value in
    # the i-th line is the graph_id of the node with node_id i

    with open(os.path.join(dataset_path, 'arxiv_citations_graph_indicator.txt'), 'w') as file:
        file.write('0\n' * graph.size())

    # DS_graph_labels.txt (N lines): class labels for all graphs in the data set, the value in the i-th line is the
    # class label of the graph with graph_id i

    with open(os.path.join(dataset_path, 'arxiv_citations_graph_labels.txt'), 'w') as file:
        file.write('citation_graph')

    # DS_node_attributes.txt (n lines): matrix of node attributes, the comma seperated values in the i-th line is the
    # attribute vector of the node with node_id i

    with open(os.path.join(dataset_path, 'arxiv_citations_node_attributes.txt'), 'w') as file:
        for node_id in range(graph.size()):
            file.write(graph.str_attributes(node_id) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Builds a dataset from json paper dict files, for reference see'
                                                 'https://chrsmrrs.github.io/datasets/docs/format/.')
    parser.add_argument('json_path', help='The directory where the json files are located', type=str)
    parser.add_argument('dataset_path', help='The directory where the dataset will be stored', type=str)
    args = parser.parse_args()

    ds_graph = build(args.json_path)
    save(ds_graph, args.dataset_path)
