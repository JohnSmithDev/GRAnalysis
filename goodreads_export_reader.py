#!/usr/bin/env python
"""
Library to read the CSV export that GoodReads makes available
"""

import csv
from datetime import date
from decimal import Decimal
import logging
import os
import pdb
import re

TEST_FILE = os.path.join('/', 'home', 'john', 'Downloads',
                         'goodreads_library_export_20180214.csv')

def date_from_string(ds):
    if ds:
        dbits = [int(z) for z in ds.split('/')]
        return date(dbits[0], dbits[1], dbits[2])
    else:
        return None

def nullable_int(s):
    if s:
        return int(s)
    else:
        return None

class Book(object):
    def __init__(self, row_dict):
        # Book specific stuff
        self.title = row_dict['Title']
        self.author = row_dict['Author']
        self.originally_published_year = nullable_int(row_dict['Original Publication Year'])

        # Edition specific stuff
        self.publisher = row_dict['Publisher']
        self.year_published = nullable_int(row_dict['Year Published'])
        self.pagination = row_dict['Number of Pages']
        self.format = row_dict['Binding']

        # Goodreads stuff
        self.average_rating = Decimal(row_dict['Average Rating'])
        self.book_id = int(row_dict['Book Id'])
        # BCID?  Seems to be empty



        # Reader specific stuff
        self.status = row_dict['Exclusive Shelf']
        self.raw_shelves = row_dict['Bookshelves']
        self.rating = row_dict['My Rating']
        self.date_read = date_from_string(row_dict['Date Read'])
        self.read_count = int(row_dict['Read Count'])
        if self.read_count > 0 and not self.date_read:
            if self.status == 'currently-reading':
                pass # This is ignorable
            elif self.status == 'to-read':
                logging.warning('%s is marked as to-read, but has been read %d times' %
                                (self.title, self.read_count))
            else:
                # Hmm, this seems to show entries that have been subsequently
                # fixed
                logging.warning('%s has been read %d times, but no read date (%s)' %
                                (self.title, self.read_count, self.status))


    @property
    def clean_title(self):
        if title.endswith(')'):
            return title.split('(')[0].strip()
        else:
            return title

    @property
    def series(self):
        if title.endswith(')'):
            regex = re.search('\((.)*\)$', title)
            # TODO: filter out ", #1" if it exists
            return regex.group(1)
        else:
            return None

    @property
    def year(self):
        if self.originally_published:
            return self.originally_published
        elif self.year_published:
            return self.year_published
        else:
            return None

    @property
    def shelves(self):
        return [s.strip() for s in self.raw_shelves]

    def __repr__(self):
        return "'%s' by %s, %s" % (self.title, self.author, self.status)


def read_file(filename):
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                yield Book(row)
            except Exception as err:
                pdb.set_trace()


if __name__ == '__main__':
    for b in read_file(TEST_FILE):
        print(b)


