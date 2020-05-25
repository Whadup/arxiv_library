import os
import tqdm
import json
import argparse
import io_pkg.paths


class Graph:

    def __init__(self, directed=True):
        self.directed = directed

        self.nodes = []  # i -> [neighbour indices of i]
        self.attributes = []  # i -> arxiv_id
        self.indices = {}  # arxiv_id -> i, fast check if id already exists

    def add(self, arxiv_id):
        if arxiv_id not in self.indices:
            self.nodes.append(set())
            self.attributes.append(arxiv_id)
            self.indices[arxiv_id] = len(self.nodes) - 1

    def link(self, arxiv_id_a, arxiv_id_b):
        index_a = self.indices[arxiv_id_a]
        index_b = self.indices[arxiv_id_b]
        self.nodes[index_a].add(index_b)

        if not self.directed:
            self.nodes[index_b].add(index_a)

    def size(self):
        return len(self.nodes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Builds a dataset from json paper dict files, for reference see'
                                                 'https://chrsmrrs.github.io/datasets/docs/format/.')
    parser.add_argument('json_path', help='The directory where the json files are located', type=str)
    parser.add_argument('dataset_path', help='The directory where the dataset will be stored', type=str)
    args = parser.parse_args()

    graph = Graph()

    # build graph, see https://chrsmrrs.github.io/datasets/docs/format/ for reference

    # n = total number of nodes
    # m = total number of edges
    # N = number of graphs

    for path in tqdm.tqdm(os.listdir(args.json_path)):
        arxiv_id = path.replace('.json', '')
        path = os.path.join(args.json_path, path)

        graph.add(arxiv_id)

        try:
            with open(path, 'r') as file:
                paper_dict = json.load(file)

        except Exception as exception:
            print('Could not load file {}.'.format(path))
            print(exception)
            continue

        if 'citations' not in paper_dict:
            print('Did not find citation key in dict for file {}.'.format(path))
            continue

        for bib_id in paper_dict['citations']:
            graph.add(bib_id)
            graph.link(arxiv_id, bib_id)

    # DS_A.txt (m lines): sparse (block diagonal) adjacency matrix for all graphs, each line corresponds to (row, col)
    # resp. (node_id, node_id)

    with open(os.path.join(args.dataset_path, 'arxiv_A.txt'), 'w') as file:
        for source in range(graph.size()):
            for target in graph.nodes[source]:
                file.write('({}, {})\n'.format(source, target))

    # DS_node_labels.txt (n lines): column vector of node labels, the value in the i-th line corresponds to the node
    # with node_id i

    with open(os.path.join(args.dataset_path, 'arxiv_node_labels.txt'), 'w') as file:
        file.write('0\n' * graph.size())

    # DS_graph_indicator.txt (n lines): column vector of graph identifiers for all nodes of all graphs, the value in
    # the i-th line is the graph_id of the node with node_id i

    with open(os.path.join(args.dataset_path, 'arxiv_graph_indicator.txt'), 'w') as file:
        file.write('0\n' * graph.size())

    # DS_graph_labels.txt (N lines): class labels for all graphs in the data set, the value in the i-th line is the
    # class label of the graph with graph_id i

    with open(os.path.join(args.dataset_path, 'arxiv_graph_labels.txt'), 'w') as file:
        file.write('citation_graph')

    # DS_node_labels.txt (n lines): column vector of node labels, the value in the i-th line corresponds to the node
    # with node_id i

    with open(os.path.join(args.dataset_path, 'arxiv_node_attributes.txt'), 'w') as file:
        for i in range(graph.size()):
            file.write(graph.attributes[i] + '\n')
