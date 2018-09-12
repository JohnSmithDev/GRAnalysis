#!/usr/bin/env python3
"""
Book class and associated consts, helper functions etc
"""

from collections import Sequence
from datetime import date
from decimal import Decimal
import logging
import pdb
import re


TODAY = date.today() # Assumption: anything using this lib will never run over multiple days

# Q: Does this affect logging behaviour in other modules?  (I tried setting
# up a custom logger, but it was ****ing me around, and I couldn't be ****d
# to fix it properly)
logging.getLogger().setLevel(logging.ERROR)

SPECIAL_SHELVES = ('read', 'currently-reading', 'to-read')


def date_from_string(ds):
    """Turn a string of format yyyy/mm/dd into a Python date object"""
    # This is now used for the command-line filters, so we also support -
    # as a separator
    separator = '/'
    if '-' in ds:
        separator = '-'
    if ds:
        dbits = [int(z) for z in ds.split(separator)]
        return date(dbits[0], dbits[1], dbits[2])
    else:
        return None

def _formatted_month(dt, separator='-'):
        return '%04d%s%02d' % (dt.year, separator,
                               dt.month)


def nullable_int(s):
    """Convert a string into an integer, or None if it is an empty string."""
    if s:
        return int(s)
    else:
        return None

def strip_prefixes(txt, prefixes):
    if not txt:
        return None
    txt = txt.strip()
    for prefix in prefixes:
        if txt.startswith(prefix):
            strip_len = len(prefix)
            txt = txt[strip_len:]
    return txt

def strip_suffixes(txt, suffixes):
    if not txt:
        return None
    txt = txt.strip()
    for suffix in suffixes:
        if txt.endswith(suffix):
            strip_len = -len(suffix)
            txt = txt[:strip_len]
    return txt

def sanitise_publisher(pub):
    """
    Remove extraneous text from publisher name, primarily to aid reports that
    group books from a publisher together.

    This is a bit of a losing battle, but hopefully we'll catch many of the
    easy ones.
    """
    return strip_suffixes(pub, (' PLC', ' and Company', ' Limited', ' Ltd', ' LLC',
                                ' Books', ' UK', ' Press', ' Digital',
                                ' Publishing', ' Publishers',
                                ' Publishing Co', ' Publishing Group'))

class NotOwnedAtSpecifiedDateError(Exception):
    pass

class Book(object):
    def __init__(self, row_dict, as_of_date=None):
        self._as_of_date = as_of_date

        # Book specific stuff
        self.title = row_dict['Title'].strip()
        self.author = row_dict['Author'].strip()
        self._raw_additional_authors = row_dict['Additional Authors']
        # self._raw_additional_authors = row_dict['Bookshelves']
        self.originally_published_year = nullable_int(row_dict['Original Publication Year'])

        # Edition specific stuff
        self.raw_publisher = sanitise_publisher(row_dict['Publisher'])
        self.publisher = sanitise_publisher(self.raw_publisher)
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
        if self.rating == 0:
            self.rating = None

        self.date_added = date_from_string(row_dict['Date Added'])
        if as_of_date and self.date_added > as_of_date:
            raise NotOwnedAtSpecifiedDateError('Book %s was added at %s' %
                                                   (self.title, self.date_added))


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
        if self.date_read and self._as_of_date:
            return self.was_read_by(self._as_of_date)
        return self.status == 'read'

    def was_owned_by(self, dt):
        # This assumes the object was created without an as_of_date arg
        return self.date_added and self.date_added <= dt

    def was_read_by(self, dt):
        return self.date_read and self.date_read <= dt

    @property
    def is_unread(self):
        # Note that this excludes currently read books
        return self.status == 'to-read'

    @property
    def year_read(self):
        if not self.date_read:
            return None
        return self.date_read.year

    @property
    def month_read(self):
        if not self.date_read:
            return None
        return _formatted_month(self.date_read)


    @property
    def year_added(self):
        return self.date_added.year

    @property
    def month_added(self):
        return _formatted_month(self.date_added)

    @property
    def clean_title(self):
        # TODO: This will return the wrong thing on a hypothetical title like
        # 'Was (Not) Was (Volume 1' - use something like the regexes in
        # .series_and_volume() to do the right thing
        if self.title.endswith(')'):
            return self.title.split('(')[0].strip()
        else:
            return self.title

    @staticmethod
    def _strip_trilogy_etc(series_name):
        """
        Remove any excess prefixes and/or suffixes from a series name

        Note that this is less to do with objecting to the bits that get removed
        than it is about trying to work aroundinconsistent naming in the GR
        data e.g.
        Downloads $ grep -i southern.reach goodreads_library_export.csv | cut -c -50
        38830119,Annihilation (Southern Reach Trilogy 1),J
        25984319,"Acceptance (Southern Reach, #3)",Jeff Va
        21198143,Authority (Southern Reach #2),Jeff Vander
        (See also "Expanse" vs "The Expanse"
        """

        series_name = strip_prefixes(series_name, ('The ',)) # A? An?
        series_name = strip_suffixes(series_name, ('Trilogy',)) # Duology?  Quartet?
        return series_name

    @property
    def series_and_volume(self):
        """
        Return either None (if the book is not in a series) or a tuple of
        (name-of-series, volume[s]).  Note the latter is a string or None, in
        order to be able to cater for compilation volumes e.g. (Earthsea Cycle, #1-4)
        or cases where the volume number is not specified.
        """
        strip_trilogy_etc = True # Would we ever not want to strip them?

        if self.title.endswith(')'):
            series_regex = re.search('\((.*)\)$', self.title)
            if series_regex:
                all_bits = series_regex.group(1)
                number_regex = re.search('^(.*[^,]),? (#|Book |Trilogy )([\d\-]+)$', all_bits)
                if number_regex:
                    series_name, volume_prefix, volume_number = (number_regex.group(1),
                                                                 number_regex.group(2),
                                                                 number_regex.group(3))
                else:
                    series_name = all_bits
                    volume_number = None
                if strip_trilogy_etc:
                    series_name = self._strip_trilogy_etc(series_name)
                return series_name.strip(), volume_number
            else:
                self._warn('Unclear if %s is in a series?  Assuming not' %
                           (self.title))
                return None
        else:
            return None

    @property
    def series(self):
        sv = self.series_and_volume
        if sv:
            return sv[0]
        else:
            return None

    @property
    def volume_number(self):
        sv = self.series_and_volume
        if sv and sv[1] is not None:
            return sv[1]
        else:
            return None

    @property
    def pagination_range(self):
        pg = self.pagination
        if pg is None:
            return None
        elif pg < 100:
            return '<100'
        elif pg >= 600:
            return '>600'
        else:
            base = pg - (pg % 50)
            return '%s-%s' % (base, base + 49)

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

    def _calculate_days_on_tbr_pile(self, effective_date):
            if self.was_read_by(effective_date):
                days = (self.date_read - self.date_added).days
                if days < 0:
                    raise ValueError('%s has read date before add date' %
                                     (self.title))
                return days
            else:
                if not self.date_added or \
                   (self.date_added > effective_date): # Q: Can this ever happen?
                    raise ValueError('%s is read, but has missing or future add date' %
                                     (self.title))
                return (effective_date - self.date_added).days


    @property
    def days_on_tbr_pile(self):
        if self._as_of_date:
            # Sanity check - I don't think this could happen currently -
            # NotOwnedAtSpecifiedDateError would be thrown in the constructor
            if not self.was_owned_by(self._as_of_date):
                raise ValueError('%s was not owned on %s'
                                 (self.title, self._as_of_date))
            return self._calculate_days_on_tbr_pile(self._as_of_date)
        else:
            if self.is_read:
                if not self.date_added or not self.date_read:
                    raise ValueError('%s is read, but has missing add or read date' %
                                     (self.title))
            return self._calculate_days_on_tbr_pile(TODAY)


    @property
    def additional_authors(self):
        if not self._raw_shelves:
            return []
        else:
            return [z.strip() for z in re.split(',', self._raw_additional_authors)]

    @property
    def all_authors(self):
        ret = [self.author]
        ret.extend(self.additional_authors)
        return ret

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
        """
        Returns only the shelves defined by the user.
        """
        return set(self.shelves) - set(SPECIAL_SHELVES)

    @property
    def goodreads_url(self):
        return 'https://www.goodreads.com/book/show/%d' % (self.book_id)

    def property_as_sequence(self, property_name):
        """
        Convenience method for reports/functions that take a configurable
        property that might be a scalar or an iterable, allowing that code
        to treat everything as the latter case.
        """
        v = getattr(self, property_name)
        # https://stackoverflow.com/questions/16807011/python-how-to-identify-if-a-variable-is-an-array-or-a-scalar
        if (isinstance(v, Sequence) or isinstance(v, set)) and \
           not isinstance(v, str):
            return v
        else:
            return [v]

    def property_as_hashable(self, property_name):
        """
        A further convenience over property_as_sequence().
        Q: Are there any cases where you'd want property_as_sequence over
           this?  Perhaps we can merge these methods, or make the other one
           private?
        """
        # Use of sorted() is for normalization
        return tuple(sorted(self.property_as_sequence(property_name)))

    def _properties(self):
        public_prop_names = [z for z in dir(self) if not z.startswith('_')]
        public_props = [(z, getattr(self, z)) for z in public_prop_names]
        return [z[0] for z in public_props if not hasattr(z[1], '__call__')]


    def __repr__(self):
        # use square parens to make it easier to distinguish from a series
        # reference in the title
        return "'%s' by %s [%s], %s" % (self.title, self.author, self.year,
                                        self.status)

