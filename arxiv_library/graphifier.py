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

    for path in tqdm.tqdm(os.listdir(args.path)):
        arxiv_id = path.replace('.json', '')
        path = os.path.join(args.path, path)

        graph.add(arxiv_id)

        with open(path, 'r') as file:
            paper_dict = json.load(file)

        for bib_id in paper_dict['citations']:
            graph.add(bib_id)
            graph.link(arxiv_id, bib_id)

    with open('/home/jan/test.txt', 'w') as file:
        file.write(str(graph))
