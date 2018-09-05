#!/usr/bin/env python3

import unittest
from .. import export_reader
from ..book import Book


class TestBook(unittest.TestCase):

    MOCK_BOOK = {
        'Title': 'A Mock Book',
        'Author': 'Mick Mock',
        'Original Publication Year': '2001',
        'Publisher': 'Mock Corp',
        'Year Published': '2002',
        'Number of Pages': '123',
        'Binding': 'Paperback',
        'Average Rating': '1.23',
        'Book Id': '12345678',

        'Exclusive Shelf': 'read',
        'Bookshelves': 'testing, mocking, software, python',
        'My Rating': '4',
        'Date Added': '2012/12/22',
        'Date Read': '2015/12/25',
        'Read Count': '1',
    }

    def test_book_basic(self):
        bk = Book(self.MOCK_BOOK)
        self.assertEqual(2001, bk.year)
        self.assertTrue(bk.is_read)
        self.assertFalse(bk.is_unread)
        self.assertIsNone(bk.series)
        self.assertEqual('2000s', bk.decade)
        self.assertEqual(2015, bk.year_read)
        self.assertEqual('2015-12', bk.month_read)
        self.assertEqual('100-149', bk.pagination_range)
        self.assertEqual('****', bk.rating_as_stars)
        self.assertEqual('**** ', bk.padded_rating_as_stars)

        self.assertEqual(['mocking', 'python', 'read', 'software', 'testing'],
                         sorted(bk.shelves))
        self.assertEqual({'mocking', 'python', 'software', 'testing'},
                         bk.user_shelves)

        self.assertEqual(['mocking', 'python', 'read', 'software', 'testing'],
                         sorted(bk.property_as_sequence('shelves')))
        self.assertEqual([4],
                         sorted(bk.property_as_sequence('rating')))

        self.assertEqual(('mocking', 'python', 'read', 'software', 'testing'),
                         bk.property_as_hashable('shelves'))
        self.assertEqual((4,),
                         bk.property_as_hashable('rating'))

    def test_book_in_series_with_comma(self):
        # e.g. Tales From Earthsea (Earthsea Cycle, #5)
        bdict = self.MOCK_BOOK.copy()
        bdict['Title'] = 'The Cliche of Cliches (Overlong Fantasy Series, #13)'
        bk = Book(bdict)
        self.assertEqual(('Overlong Fantasy Series', '13'), bk.series_and_volume)
        self.assertEqual('Overlong Fantasy Series', bk.series)
        self.assertEqual('13', bk.volume_number)

    def test_book_in_series_no_comma(self):
        # e.g. The Space Merchants (The Space Merchants #1)
        bdict = self.MOCK_BOOK.copy()
        bdict['Title'] = 'The Cliche of Cliches (Overlong Fantasy Series #14)'
        bk = Book(bdict)
        self.assertEqual(('Overlong Fantasy Series', '14'), bk.series_and_volume)
        self.assertEqual('Overlong Fantasy Series', bk.series)
        self.assertEqual('14', bk.volume_number)

    def test_book_in_series_trilogy(self):
        # e.g. "Annihilation (Southern Reach Trilogy 1)"
        bdict = self.MOCK_BOOK.copy()
        bdict['Title'] = 'The Cliche of Cliches (Fantasy Trilogy 3)'
        bk = Book(bdict)
        self.assertEqual(('Fantasy', '3'), bk.series_and_volume)
        self.assertEqual('Fantasy', bk.series)
        self.assertEqual('3', bk.volume_number)

    def test_book_in_series_trilogy_with_book_in_name(self):
        # e.g. Colossus and the Crab (Colossus Trilogy Book 3)
        bdict = self.MOCK_BOOK.copy()
        bdict['Title'] = 'The Cliche of Cliches (Fantasy Trilogy Book 3)'
        bk = Book(bdict)
        self.assertEqual(('Fantasy', '3'), bk.series_and_volume)
        self.assertEqual('Fantasy', bk.series)
        self.assertEqual('3', bk.volume_number)

    def test_book_in_series_compilation(self):
        # e.g. Helliconia (Helliconia, #1-3)
        bdict = self.MOCK_BOOK.copy()
        bdict['Title'] = 'The Cliche of Cliches (Overlong Fantasy Series #1-3)'
        bk = Book(bdict)
        self.assertEqual(('Overlong Fantasy Series', '1-3'), bk.series_and_volume)
        self.assertEqual('Overlong Fantasy Series', bk.series)
        self.assertEqual('1-3', bk.volume_number)

    def test_book_in_series_no_number(self):
        # e.g. Meeting Infinity (The Infinity Project)
        bdict = self.MOCK_BOOK.copy()
        bdict['Title'] = 'The Cliche of Cliches (Overlong Fantasy Series)'
        bk = Book(bdict)
        self.assertEqual(('Overlong Fantasy Series', None), bk.series_and_volume)
        self.assertEqual('Overlong Fantasy Series', bk.series)
        self.assertIsNone(bk.volume_number)

    def test_book_with_parens_but_not_in_series(self):
        # e.g. I Am (Not) A Number: Decoding The Prisoner
        bdict = self.MOCK_BOOK.copy()
        bdict['Title'] = 'Foo (Bar) Baz'
        bk = Book(bdict)
        self.assertIsNone(bk.series_and_volume)
        self.assertIsNone(bk.series)
        self.assertIsNone(bk.volume_number)

if __name__ == '__main__':
    unittest.main()
