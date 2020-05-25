import os
import tqdm
import json
import argparse


class Graph:

    def __init__(self):
        self.nodes = []  # i -> [neighbour indices of i]
        self.arxiv_ids = []  # i -> arxiv_id
        self.node_ids = {}  # arxiv_id -> i, fast check if id already exists
        self.attributes = {}  # i -> {arxiv_id, authors, published, title, arxiv_primary_category}

    def add(self, arxiv_id):
        if arxiv_id not in self.node_ids:
            self.nodes.append(set())
            self.arxiv_ids.append(arxiv_id)

            index = len(self.nodes) - 1
            self.node_ids[arxiv_id] = index
            self.attributes[index] = {'arxiv_id': arxiv_id}

    def link(self, arxiv_id_a, arxiv_id_b):
        index_a = self.node_ids[arxiv_id_a]
        index_b = self.node_ids[arxiv_id_b]
        self.nodes[index_a].add(index_b)

    def size(self):
        return len(self.nodes)

    def add_attribute(self, arxiv_id, key, value):
        if arxiv_id not in self.node_ids:
            return

        self.attributes[self.node_ids[arxiv_id]][key] = value

    def str_attributes(self, node_id):
        return ', '.join(['{}: {}'.format(key, value) for key, value in self.attributes[node_id].items()])


def build(source_path):
    # see https://chrsmrrs.github.io/datasets/docs/format/ for reference

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
