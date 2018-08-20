#!/usr/bin/env python3
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
import sys

TEST_FILE = os.path.join('/', 'home', 'john', 'Downloads',
                         'goodreads_library_export_latest.csv')

TODAY = date.today() # Assumption: anything using this lib will never run over multiple days

# Q: Does this affect logging behaviour in other modules?  (I tried setting
# up a custom logger, but it was ****ing me around, and I couldn't be ****d
# to fix it properly)
logging.getLogger().setLevel(logging.ERROR)

SPECIAL_SHELVES = ('read', 'currently-reading', 'to-read')


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
        try:
            self.pagination = int(row_dict['Number of Pages'])
        except ValueError as err:
            self._warn('%s does not have a valid pagination (%s)' %
                            (self.title, row_dict['Number of Pages']))
            self.pagination = None
        self.format = row_dict['Binding']

        # Goodreads stuff
        self.average_rating = Decimal(row_dict['Average Rating'])
        self.book_id = int(row_dict['Book Id'])
        # BCID?  Seems to be empty



        # Reader specific stuff
        self.status = row_dict['Exclusive Shelf']
        self._raw_shelves = row_dict['Bookshelves']
        self.rating = int(row_dict['My Rating'])
        if self.rating == '0':
            self.rating = None

        self.date_added = date_from_string(row_dict['Date Added'])
        self.date_read = date_from_string(row_dict['Date Read'])
        self.read_count = int(row_dict['Read Count'])
        if self.read_count > 0 and not self.date_read:
            if self.status == 'currently-reading':
                pass # This is ignorable
            elif self.status == 'to-read':
                self._warn('%s is marked as to-read, but has been read %d times' %
                                (self.title, self.read_count))
            else:
                # Hmm, this seems to show entries that have been subsequently
                # fixed
                self._warn('%s has been read %d times, but no read date (%s)' %
                                (self.title, self.read_count, self.status))

    def _warn(self, msg):
        logging.warning(msg)

    @property
    def is_read(self):
        return self.status == 'read'

    @property
    def is_unread(self):
        # Note that this excludes currently read books
        return self.status == 'to-read'


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
        if self.originally_published_year:
            return self.originally_published_year
        elif self.year_published:
            return self.year_published
        else:
            return None

    @property
    def decade(self):
        return str(self.year)[:3] + '0s'

    @property
    def rating_as_stars(self):
        if self.rating is None:
            return ""
        else:
            return '*' * self.rating

    @property
    def padded_rating_as_stars(self):
        return '%-5s' % (self.rating_as_stars)

    @property
    def days_on_tbr_pile(self):
        if self.is_read:
            if not self.date_added or not self.date_read:
                raise ValueError('%s is read, but has missing add or read date' %
                                 (self.title))
            days = (self.date_read - self.date_added).days
            if days < 0:
                raise ValueError('%s has read date before add date' %
                                 (self.title))
            return days
        else:
            if not self.date_added or \
               (self.date_added > TODAY): # Q: Can this ever happen?
                raise ValueError('%s is read, but has missing or future add date' %
                                 (self.title))
            return (TODAY - self.date_added).days

    @property
    def shelves(self):
        s = []
        if not self._raw_shelves:
            self._warn('%s is not shelved anywhere' % (self.title))
        else:
            s = re.split('[, ]+', self._raw_shelves)

        # There seems to be a bug in the exported data, whereby 'to-read'
        # and 'currently-reading' are in the shelves column, but 'read'
        # isn't - so we patch it here
        if self.is_read and 'read' not in s:
            s.append('read')
        return s

    @property
    def user_shelves(self):
        return set(self.shelves) - set(SPECIAL_SHELVES)

    @property
    def goodreads_url(self):
        return 'https://www.goodreads.com/book/show/%d' % (self.book_id)


    def __repr__(self):
        # use square parens to make it easier to distinguish from a series
        # reference in the title
        return "'%s' by %s [%s], %s" % (self.title, self.author, self.year,
                                        self.status)

### Some commonly used filters for use with read_file()
def only_read_books(bk):
    return bk.is_read
def only_unread_books(bk):
    return bk.is_unread
def only_read_and_rated_books(bk):
    return bk.is_read and bk.rating is not None and bk.rating > 0

def read_file(filename, filter_funcs=None):
    # pdb.set_trace()
    # er_logger.basicConfig(format='XXXX %(levelname)s:%(message)s', level=logging.DEBUG)
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for line_num, row in enumerate(reader):
            try:
                bk = Book(row)
                wanted = True
                if filter_funcs:
                    for fn in filter_funcs:
                        if not fn(bk):
                            wanted = False
                            break
                if wanted:
                    yield bk
            except Exception as err:
                logging.error('Blew up on line %d: %s/%s' % (line_num, err, type(err)))
                pdb.set_trace()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARNING)

    for b in read_file(TEST_FILE):
        print(b)

