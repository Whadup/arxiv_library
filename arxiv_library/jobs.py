import sys
import json
import ray
import psutil
import argparse
import extraction.citations


def extract_citations():
    ray.init()

    @ray.remote(num_cpus=1)
    def extract(paper_dicts_stdin):
        paper_dicts = []

        for pd in paper_dicts_stdin:
            try:
                pd = json.loads(pd)
                pd = extraction.citations.extract_citations(pd)
                pd = json.dumps(pd)

                paper_dicts.append(pd)

            except Exception as exception:
                print(exception)

        return paper_dicts

    paper_dicts_stdin = []

    while True:
        try:
            paper_dicts_stdin.append(json.loads(input()))

        except EOFError:
            break

    chunk_size = len(paper_dicts_stdin) // psutil.cpu_count()
    generator = (paper_dicts_stdin[i:i + chunk_size] for i in range(0, len(paper_dicts_stdin), chunk_size))
    paper_dicts = [extract.remote(chunk) for chunk in generator]

    for paper_dict in ray.get(paper_dicts):
        sys.stdout.write(json.dumps(paper_dict))

    ray.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--citations',
                        help='Extracts citations for a list of paper dictionaries and returns the list to std out. The '
                             'citations will be saved as list under the key "citations".',
                        metavar='[dicts]'
    )

    args = parser.parse_args()

    if args.citations:
        extract_citations(args.citations)
