#!/usr/bin/env python3
"""
Argument handling for command-line scripts/reports that is common to many.
"""

from argparse import ArgumentParser, ArgumentTypeError
import os
import pdb

from utils.book import date_from_string
from utils.display import ColourConfig

class ArgumentError(Exception):
    pass


def valid_date_type(arg_date_str):
    # Adapted from https://gist.github.com/monkut/e60eea811ef085a6540
    dt = date_from_string(arg_date_str)
    if not dt:
        raise ArgumentTypeError('%s does not seem to be a valid date' %
                                (arg_date_str))
    return dt

def create_parser(description, supported_args=''):
    parser = ArgumentParser(description=description)

    if 'a' in supported_args:
        parser.add_argument('-a', dest='all_authors', action='store_true',
                            help='Report on all authors, not just the main one')

    if 'c' in supported_args:
        parser.add_argument('-c', dest='colour_cfg_file', nargs='?',
                            default=os.environ.get('GR_COLOUR_CFG'),
                            help='Use named JSON file as colour configuration, default=GR_COLOUR_CFG')

    if 'd' in supported_args:
        parser.add_argument('-d', dest='date', nargs='?',
                            type=valid_date_type, default=None, required=False,
                            help='Output as if today was specified date')

    if 'f' in supported_args:
        parser.add_argument('-f', dest='filters',
                            action='append', default=[],
                            help='Filter only books that are on specified shelves, ' +
                            'or that have property with particular value(s)')

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

    try:
        with open(args.colour_cfg_file) as json_data:
            args.colour_cfg = ColourConfig(json_data)
    except AttributeError:
        args.colour_cfg = None # Q: Or should be just pass

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
