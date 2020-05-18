import sys
import json
import argparse


def extract_citations(paper_dicts):
    paper_dicts = []

    for pd in paper_dicts:



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
