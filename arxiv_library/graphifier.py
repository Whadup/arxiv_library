import os
import tqdm
import json
import argparse


class Graph:

    def __init__(self, directed=True):
        self.nodes = {}
        self.directed = directed

    def add(self, id):
        self.nodes[id] = set()

    def link(self, id_a, id_b):
        self.nodes[id_a].add(id_b)

        if not self.directed:
            self.nodes['id_b'].add(id_a)

    def size(self):
        return len(self.nodes.keys())

    def labels(self):
        return list(self.nodes.keys())

    def __str__(self):
        string = ''
        keys = self.labels()

        for i in range(self.size()):
            for j in range(self.size()):
                if keys[j] not in self.nodes[keys[i]]:
                    string += '0'

                else:
                    string += '1'

            string += '\n'

        return string


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
    # resp. (node_id, node_id).

    with open('/home/jan/arxiv_lib/arxiv_A.txt', 'w') as file:
        file.write(str(graph))

    # DS_node_labels.txt (n lines): column vector of node labels, the value in the i-th line corresponds to the node
    # with node_id i

    with open('/home/jan/arxiv_lib/arxiv_node_labels.txt', 'w') as file:
        file.write('\n'.join(graph.labels()))

    # DS_graph_indicator.txt (n lines): column vector of graph identifiers for all nodes of all graphs, the value in
    # the i-th line is the graph_id of the node with node_id i

    with open('/home/jan/arxiv_lib/arxiv_graph_indicator.txt', 'w') as file:
        file.write('0\n' * graph.size())

    # DS_graph_labels.txt (N lines): class labels for all graphs in the data set, the value in the i-th line is the
    # class label of the graph with graph_id i

    with open('/home/jan/arxiv_lib/arxiv_graph_labels.txt', 'w') as file:
        file.write('find a good graph name')
