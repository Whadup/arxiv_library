import os
import tqdm
import json
import argparse


class Graph:

    def __init__(self, directed=True):
        self.directed = directed
        self.nodes = []  # i -> [neighbour indices of i]
        self.labels = []  # i -> arxiv_id
        self.indices = {}  # arxiv_id -> i

    def add(self, arxiv_id):
        self.nodes.append(set())
        self.labels.append(arxiv_id)
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
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('path', help='The directory where the json files are located', type=str)
    args = parser.parse_args()

    graph = Graph()

    # build graph, see https://chrsmrrs.github.io/datasets/docs/format/ for reference

    # n = total number of nodes
    # m = total number of edges
    # N = number of graphs

    for path in tqdm.tqdm(os.listdir(args.path)):
        arxiv_id = path.replace('.json', '')
        path = os.path.join(args.path, path)

        graph.add(arxiv_id)

        with open(path, 'r') as file:
            paper_dict = json.load(file)

        for bib_id in paper_dict['citations']:
            graph.add(bib_id)
            graph.link(arxiv_id, bib_id)

    # DS_A.txt (m lines): sparse (block diagonal) adjacency matrix for all graphs, each line corresponds to (row, col)
    # resp. (node_id, node_id)

    with open('/home/jan/arxiv_lib/arxiv_A.txt', 'w') as file:
        for source in range(graph.size()):
            for target in graph.nodes[source]:
                file.write('({}, {})\n'.format(source, target))

    # DS_node_labels.txt (n lines): column vector of node labels, the value in the i-th line corresponds to the node
    # with node_id i

    with open('/home/jan/arxiv_lib/arxiv_node_labels.txt', 'w') as file:
        for i in range(graph.size()):
            file.write(graph.labels[i] + '\n')

    # DS_graph_indicator.txt (n lines): column vector of graph identifiers for all nodes of all graphs, the value in
    # the i-th line is the graph_id of the node with node_id i

    with open('/home/jan/arxiv_lib/arxiv_graph_indicator.txt', 'w') as file:
        file.write('0\n' * graph.size())

    # DS_graph_labels.txt (N lines): class labels for all graphs in the data set, the value in the i-th line is the
    # class label of the graph with graph_id i

    with open('/home/jan/arxiv_lib/arxiv_graph_labels.txt', 'w') as file:
        file.write('find a good graph name')
