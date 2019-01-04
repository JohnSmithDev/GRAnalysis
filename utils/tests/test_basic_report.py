#!/usr/bin/env python3

import pdb
import unittest


from ..basic_report import GROUP_SEPARATOR, process_books, output_grouped_lists

class MockBookForBasicReport(object):
    def __init__(self, author, title):
        self.title = title
        self.author = author

    def __repr__(self):
        return '%s - %s' % (self.title, self.author)

    def custom_format(self, format):
        fmt = format.replace('{', '{0.')
        return fmt.format(self)



MOCK_BOOKS = [
    MockBookForBasicReport('Albert Andrews', 'A Test Book'),
    MockBookForBasicReport('Albert Andrews', 'Another Test Book'),
    MockBookForBasicReport('Albert Andrews', 'Awesome Test Book'),

    MockBookForBasicReport('Clive Custer', 'Codswallop'),

    MockBookForBasicReport('Billy Brown', 'Book for Testing'),
    MockBookForBasicReport('Billy Brown', 'Book Again'),

    MockBookForBasicReport('Dave Dump', 'Dire'),
    MockBookForBasicReport('Dave Dump', 'Dung')
    ]

class MockArgs(object):
    def __init__(self):
        self.sort_properties = None
        self.property_names = None
        self.enumerate_output = None
        self.inline_separator = None
        self.inline_separator_with_breaks = None
        self.format = None
        self.properties = []

class TestProcessBooks(unittest.TestCase):
    def test_no_filtering_formatting_or_sorting(self):
        ret = []
        def collate_strings(txt):
            ret.append(txt)
        process_books(MOCK_BOOKS, MockArgs(), collate_strings)
        self.assertEqual([
            'A Test Book - Albert Andrews',
            'Another Test Book - Albert Andrews',
            'Awesome Test Book - Albert Andrews',
            'Codswallop - Clive Custer',
            'Book for Testing - Billy Brown',
            'Book Again - Billy Brown',
            'Dire - Dave Dump',
            'Dung - Dave Dump'
            ], ret)

    def test_with_sorting(self):
        ret = []
        def collate_strings(txt):
            ret.append(txt)
        args =  MockArgs()
        args.sort_properties = ['author']
        process_books(MOCK_BOOKS, args, collate_strings)
        self.assertEqual([
            'A Test Book - Albert Andrews',
            'Another Test Book - Albert Andrews',
            'Awesome Test Book - Albert Andrews',
            'Book for Testing - Billy Brown',
            'Book Again - Billy Brown',
            'Codswallop - Clive Custer',
            'Dire - Dave Dump',
            'Dung - Dave Dump'
            ], ret)

    def test_inline_output(self):
        ret = []
        def collate_strings(txt):
            ret.append(txt)
        args =  MockArgs()
        args.inline_separator = ';'
        process_books(MOCK_BOOKS, args, collate_strings)
        self.assertEqual([
            'A Test Book - Albert Andrews',
            'Another Test Book - Albert Andrews',
            'Awesome Test Book - Albert Andrews',
            'Codswallop - Clive Custer',
            'Book for Testing - Billy Brown',
            'Book Again - Billy Brown',
            'Dire - Dave Dump',
            'Dung - Dave Dump'
            ], ret)
        # Note that the concatenation is done in the __main__ method of
        # shelf_intersection.py, which is out of scope of this test

    def test_grouped_inline_output(self):
        ret = []
        def collate_strings(txt):
            ret.append(txt)
        args =  MockArgs()
        args.inline_separator_with_breaks = ';'
        args.sort_properties = ['author']
        args.format = '{title}'
        process_books(MOCK_BOOKS, args, collate_strings)
        print(ret)
        self.assertEqual([
            GROUP_SEPARATOR, # Ideally this wouldn't be in the output
            'Albert Andrews',
            'A Test Book',
            'Another Test Book',
            'Awesome Test Book',
            GROUP_SEPARATOR,
            'Billy Brown',
            'Book for Testing',
            'Book Again',
            GROUP_SEPARATOR,
            'Clive Custer',
            'Codswallop',
            GROUP_SEPARATOR,
            'Dave Dump',
            'Dire',
            'Dung'
            ], ret)
        # Note that the concatenation is done in the __main__ method of
        # shelf_intersection.py, which is out of scope of this test


