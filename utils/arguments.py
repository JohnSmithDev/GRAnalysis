#!/usr/bin/env python3
"""
Argument handling for command-line scripts/reports that is common to many.
"""

from argparse import ArgumentParser
import os
import pdb

class ArgumentError(Exception):
    pass


def create_parser(description, supported_args=''):
    parser = ArgumentParser(description=description)

    if 'f' in supported_args:
        parser.add_argument('-f', dest='filters',
                            action='append', default=[],
                            help='Filter only books that are on specified shelves')

    if 'l' in supported_args:
        parser.add_argument('-l', dest='limit', type=int, nargs='?',
                            help='Limit to N results')

    parser.add_argument('csv_file', nargs='?',
                        default=os.environ.get('GR_CSV_FILE'),
                        help='CSV export file from GoodReads, default=GR_CSV_FILE')
    return parser

def validate_args(args):
    if not args.csv_file:
        # Q: Can this be specified within create_parser? This SO link implies not:
        # https://stackoverflow.com/questions/10551117/setting-options-from-environment-variables-when-using-argparse
        raise ArgumentError('Must specify a CSV file, or set GR_CSV_FILE environment variable')


def parse_args(description, supported_args=''):
    """
    Parse, validate and return the arguments.

    Don't use this if you need to use non-standard/non-generic arguments,
    instead do the following in your code:
        parser = create_parser(...)
        parser.add_argument(...)
        args = parser.parse_args()
        validate_args(args)
        ... any additional validation
    """


    parser = create_parser(description, supported_args)
    args = parser.parse_args()
    validate_args(args)

    return args
