#!/usr/bin/env python3
"""
Show average ranking of publishers, with a bar chart breaking down the rankings.

Note that this is very prone to distortion by inconsistent GR data e.g. I have
books from "Tor", "Tor UK" and "Tor Books" in my collection.  Those particular
cases are now normalized, but I imagine there are many other similar ones that
aren't (yet) dealt with.

Not to mention parent/child companies e.g. SF Masterworks titles are variously
attributed to Gollancz, Gateway, Orion Publishing...
"""

from __future__ import division

from collections import defaultdict
from functools import cmp_to_key

from utils.arguments import parse_args
from utils.export_reader import read_file, only_read_books
from utils.transformers import best_ranked_report


if __name__ == '__main__':
    args = parse_args(
        'Show average rating of publishers, with a bar chart breaking down the rankings',
        supported_args='f')
    books = read_file(args=args, filter_funcs=[only_read_books])
    best_ranked_report(books, 'publisher', ignore_single_book_groups=True)
