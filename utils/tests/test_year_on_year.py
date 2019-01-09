#!/usr/bin/env python3

from collections import Sequence, Counter

import unittest
from ..year_on_year import YearOnYearReport

class MockBook(object):
    def __init__(self, year_added, year_read, shelves, rating, decade):
        self.year_added = year_added
        self.year_read = year_read
        self.user_shelves = shelves
        self.rating = rating
        if rating:
            self.rating_as_stars = '*' * rating
        else:
            self.rating_as_stars = None
        self.decade = decade

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

MOCK_BOOKS = [
    MockBook(2000, 2010, ['alpha', 'beta'], 3, '1990s'),
    MockBook(2001, 2011, ['beta', 'gamma'], 4, '1980s'),
    MockBook(2002, 2012, ['gamma', 'delta'], 2, '1970s'),

    MockBook(2001, 2013, ['alpha',], 3, '1980s'),
    MockBook(2000, 2011, ['delta'], 5, '1990s'),
    MockBook(2000, None, ['beta'], None, '1990s')
    ]

class TestYearOnYearReport(unittest.TestCase):

    def test_yoy_by_decade_and_year_added(self):
        rpt = YearOnYearReport('decade', 'year_added')
        rpt.process(MOCK_BOOKS)

        # First test the mundane meta-data
        self.assertEqual(2000, rpt.min_year)
        self.assertEqual(2002, rpt.max_year)
        self.assertFalse(rpt.none_year_found)
        self.assertEqual(5, rpt.max_key_length)
        self.assertEqual({2000: 3, 2001: 2, 2002: 1}, rpt.number_of_books_by_year)

        # Now the 'real' data
        self.assertEqual({
            '1970s': Counter({2002: 1}),
            '1980s': Counter({2001: 2}),
            '1990s': Counter({2000: 3}),
            }, rpt.key_to_year_counts)

    def test_yoy_by_rating_and_year_read(self):
        rpt = YearOnYearReport('rating_as_stars', 'year_read')
        rpt.process(MOCK_BOOKS)

        # First test the mundane meta-data
        self.assertEqual(2010, rpt.min_year)
        self.assertEqual(2013, rpt.max_year)
        self.assertFalse(rpt.none_year_found) # Q: Shouldn't this be True?
        self.assertEqual(5, rpt.max_key_length)
        self.assertEqual({2010: 1, 2011: 2, 2012: 1, 2013: 1}, rpt.number_of_books_by_year)

        # Now the 'real' data
        self.assertEqual({
            '**': Counter({2012: 1}),
            '***': Counter({2010: 1, 2013: 1}),
            '****': Counter({2011: 1}),
            '*****': Counter({2011: 1}),
            }, rpt.key_to_year_counts)












