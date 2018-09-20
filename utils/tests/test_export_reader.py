#!/usr/bin/env python3

import unittest
from .. import export_reader
from ..book import Book

MOCK_BOOK_DATA = {
    'Title': 'A Mock Book',
    'Author': 'Mick Mock',
    'Additional Authors': 'Terry Test, Peter Python', # .additional_authors, .all_authors
    'Original Publication Year': '2001', # bk.originally_published_year
    'Publisher': 'Mock Corp',
    'Year Published': '2002', # bk.year_published
    'Number of Pages': '123',
    'Binding': 'Paperback', # bk.format
    'Average Rating': '1.23',
    'Book Id': '12345678',

    'Exclusive Shelf': 'read',
    'Bookshelves': 'testing, mocking, software, python',
    'My Rating': '4',
    'Date Added': '2012/12/22',
    'Date Read': '2015/12/25',
    'Read Count': '1',
}
MOCK_BOOK = Book(MOCK_BOOK_DATA)

class TestCreateShelfFilter(unittest.TestCase):

    def test_basic_positive_shelf(self):
        fltr = export_reader.create_shelf_filter('software')
        self.assertTrue(fltr(MOCK_BOOK))

    def test_basic_negative_shelf(self):
        fltr2 = export_reader.create_shelf_filter('bang')
        self.assertFalse(fltr2(MOCK_BOOK))

        fltr3 = export_reader.create_shelf_filter('test')
        self.assertFalse(fltr3(MOCK_BOOK))

    def test_inverse_positive_shelf(self):
        fltr = export_reader.create_shelf_filter('!boom')
        self.assertTrue(fltr(MOCK_BOOK))

        fltr2 = export_reader.create_shelf_filter('~crash')
        self.assertTrue(fltr2(MOCK_BOOK))

    def test_inverse_negative_shelf(self):
        fltr3 = export_reader.create_shelf_filter('!testing')
        self.assertFalse(fltr3(MOCK_BOOK))

        fltr4 = export_reader.create_shelf_filter('~python')
        self.assertFalse(fltr4(MOCK_BOOK))


class TestCreateComparisonFilter(unittest.TestCase):

    def test_singleequals_positive(self):
        fltr = export_reader.create_comparison_filter('pagination', '=', '123')
        self.assertTrue(fltr(MOCK_BOOK))

    def test_doubleequals_positive(self):
        fltr = export_reader.create_comparison_filter('year_published', '==', '2002')
        self.assertTrue(fltr(MOCK_BOOK))

    def test_singleequals_negative(self):
        fltr = export_reader.create_comparison_filter('format', '=', 'Hardback')
        self.assertFalse(fltr(MOCK_BOOK))

    def test_doubleequals_negative(self):
        fltr = export_reader.create_comparison_filter('publisher', '==', 'EvilCorp')
        self.assertFalse(fltr(MOCK_BOOK))

    def test_bangequals_positive(self):
        fltr = export_reader.create_comparison_filter('pagination', '!=', '124')
        self.assertTrue(fltr(MOCK_BOOK))

    def test_anglebrackets_positive(self):
        fltr = export_reader.create_comparison_filter('year_published', '<>', '2001')
        self.assertTrue(fltr(MOCK_BOOK))

    def test_bangequals_negative(self):
        fltr = export_reader.create_comparison_filter('format', '!=', 'Paperback')
        self.assertFalse(fltr(MOCK_BOOK))

    def test_anglebrackets_negative(self):
        fltr = export_reader.create_comparison_filter('publisher', '<>', 'Mock Corp')
        self.assertFalse(fltr(MOCK_BOOK))

    def test_regex_positive(self):
        fltr1 = export_reader.create_comparison_filter('title', '~', 'A')
        self.assertTrue(fltr1(MOCK_BOOK))
        fltr2 = export_reader.create_comparison_filter('title', '=~', 'Mock')
        self.assertTrue(fltr2(MOCK_BOOK))
        fltr3 = export_reader.create_comparison_filter('title', '~=', 'Book')
        self.assertTrue(fltr3(MOCK_BOOK))

    def test_regex_positive_case_insensitive(self):
        fltr1 = export_reader.create_comparison_filter('title', '~', 'mOcK')
        self.assertTrue(fltr1(MOCK_BOOK))

    def test_regex_negative(self):
        fltr1 = export_reader.create_comparison_filter('title', '~!', 'Zonk')
        self.assertTrue(fltr1(MOCK_BOOK))
        fltr2 = export_reader.create_comparison_filter('title', '!~', 'Zonk')
        self.assertTrue(fltr2(MOCK_BOOK))
        fltr3 = export_reader.create_comparison_filter('title', '!~', 'Book')
        self.assertFalse(fltr3(MOCK_BOOK))


    def test_greaterthan(self):
        fltr1 = export_reader.create_comparison_filter('pagination', '>', '122')
        self.assertTrue(fltr1(MOCK_BOOK))
        fltr2 = export_reader.create_comparison_filter('pagination', '>', '123')
        self.assertFalse(fltr2(MOCK_BOOK))
        fltr3 = export_reader.create_comparison_filter('pagination', '>', '124')
        self.assertFalse(fltr2(MOCK_BOOK))

    def test_greaterorequalthan(self):
        fltr1 = export_reader.create_comparison_filter('pagination', '>=', '122')
        self.assertTrue(fltr1(MOCK_BOOK))
        fltr2 = export_reader.create_comparison_filter('pagination', '>=', '123')
        self.assertTrue(fltr2(MOCK_BOOK))
        fltr3 = export_reader.create_comparison_filter('pagination', '>=', '124')
        self.assertFalse(fltr3(MOCK_BOOK))

    def test_equalorgreaterthan(self):
        fltr1 = export_reader.create_comparison_filter('date_read', '=>', '2015-12-24')
        self.assertTrue(fltr1(MOCK_BOOK))
        fltr2 = export_reader.create_comparison_filter('date_read', '=>', '2015-12-25')
        self.assertTrue(fltr2(MOCK_BOOK))
        fltr3 = export_reader.create_comparison_filter('date_read', '=>', '2015-12-26')
        self.assertFalse(fltr3(MOCK_BOOK))

    def test_lessthan(self):
        fltr1 = export_reader.create_comparison_filter('pagination', '<', '122')
        self.assertFalse(fltr1(MOCK_BOOK))
        fltr2 = export_reader.create_comparison_filter('pagination', '<', '123')
        self.assertFalse(fltr2(MOCK_BOOK))
        fltr3 = export_reader.create_comparison_filter('pagination', '<', '124')
        self.assertTrue(fltr3(MOCK_BOOK))

    def test_lessorequalthan(self):
        fltr1 = export_reader.create_comparison_filter('pagination', '<=', '122')
        self.assertFalse(fltr1(MOCK_BOOK))
        fltr2 = export_reader.create_comparison_filter('pagination', '<=', '123')
        self.assertTrue(fltr2(MOCK_BOOK))
        fltr3 = export_reader.create_comparison_filter('pagination', '<=', '124')
        self.assertTrue(fltr3(MOCK_BOOK))

    def test_equalorlessthan(self):
        fltr1 = export_reader.create_comparison_filter('pagination', '=<', '122')
        self.assertFalse(fltr1(MOCK_BOOK))
        fltr2 = export_reader.create_comparison_filter('pagination', '=<', '123')
        self.assertTrue(fltr2(MOCK_BOOK))
        fltr3 = export_reader.create_comparison_filter('pagination', '=<', '124')
        self.assertTrue(fltr3(MOCK_BOOK))

class TestCreateFilter(unittest.TestCase):

    def test_creating_shelf_filter(self):
        fltr1 = export_reader.create_filter('testing')
        self.assertTrue(fltr1(MOCK_BOOK))
        fltr2 = export_reader.create_filter('besting')
        self.assertFalse(fltr2(MOCK_BOOK))

    def test_creating_comparison_filter(self):
        fltr1 = export_reader.create_filter('year = 2001')
        self.assertTrue(fltr1(MOCK_BOOK))
        fltr2 = export_reader.create_filter('year = 1999')
        self.assertFalse(fltr2(MOCK_BOOK))

if __name__ == '__main__':
    unittest.main()
