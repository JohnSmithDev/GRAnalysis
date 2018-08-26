#!/usr/bin/env python3
"""
Argument handling for command-line scripts/reports that is common to many.
"""

from argparse import ArgumentParser
import os
import pdb

class ArgumentError(Exception):
    pass

def parse_args(description, supported_args=''):
    parser = ArgumentParser(description=description)

    if 'f' in supported_args:
        parser.add_argument('-f', dest='filters',
                            action='append', default=[],
                            help='Filter only books that are on specified shelves')

    parser.add_argument('csv_file', nargs='?',
                        default=os.environ.get('GR_CSV_FILE'),
                        help='CSV export file from GoodReads, default=GR_CSV_FILE')
    args = parser.parse_args()

    if not args.csv_file:
        raise ArgumentError('Must specify a CSV file, or set GR_CSV_FILE environment variable')

    return args
