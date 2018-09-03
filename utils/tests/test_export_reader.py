#!/usr/bin/env python3

import unittest
from .. import export_reader


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
        bk = export_reader.Book(self.MOCK_BOOK)
        self.assertEqual(2001, bk.year)
        self.assertTrue(bk.is_read)
        self.assertFalse(bk.is_unread)
        self.assertIsNone(bk.series)
        self.assertEqual('2000s', bk.decade)

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
        bk = export_reader.Book(bdict)
        self.assertEqual(('Overlong Fantasy Series', '13'), bk.series)

    def test_book_in_series_no_comma(self):
        # e.g. The Space Merchants (The Space Merchants #1)
        bdict = self.MOCK_BOOK.copy()
        bdict['Title'] = 'The Cliche of Cliches (Overlong Fantasy Series #14)'
        bk = export_reader.Book(bdict)
        self.assertEqual(('Overlong Fantasy Series', '14'), bk.series)

    def test_book_in_series_compilation(self):
        # e.g. Helliconia (Helliconia, #1-3)
        bdict = self.MOCK_BOOK.copy()
        bdict['Title'] = 'The Cliche of Cliches (Overlong Fantasy Series #1-3)'
        bk = export_reader.Book(bdict)
        self.assertEqual(('Overlong Fantasy Series', '1-3'), bk.series)

    def test_book_in_series_no_number(self):
        # e.g. Meeting Infinity (The Infinity Project)
        bdict = self.MOCK_BOOK.copy()
        bdict['Title'] = 'The Cliche of Cliches (Overlong Fantasy Series)'
        bk = export_reader.Book(bdict)
        self.assertEqual(('Overlong Fantasy Series', None), bk.series)

    def test_book_with_parens_but_not_in_series(self):
        # e.g. I Am (Not) A Number: Decoding The Prisoner
        bdict = self.MOCK_BOOK.copy()
        bdict['Title'] = 'Foo (Bar) Baz'
        bk = export_reader.Book(bdict)
        self.assertIsNone(bk.series)

if __name__ == '__main__':
    unittest.main()
