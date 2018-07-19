#!/usr/bin/env python3
"""
Output list of books ordered by publication year.

NB: I believe this data in the export is not reliable (in part, this script
has been written to ascertain this).  UPDATE: looks like either "Year
Published" or "Original Publication Year" can be empty, but not both - at
least based on the books I own.
"""

from __future__ import division

from collections import defaultdict
from functools import cmp_to_key
import logging
import pdb

from utils.export_reader import TEST_FILE, read_file
from utils.display import render_ratings_as_bar

if __name__ == '__main__':
    books_in_pub_date_order = sorted(read_file(TEST_FILE),
                                     key=lambda z: z.year or 9999)
    for b in books_in_pub_date_order:
        print('%s %-5s : %s' % (b.year or '????',
                              b.rating * '*' if b.rating else '',
                              b))
