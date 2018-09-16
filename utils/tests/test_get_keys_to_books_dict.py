#!/usr/bin/env python3

import unittest

from ..transformers import get_keys_to_books_dict

class MockBookForReadVsUnreadReport(object):
    def __init__(self, keys, title, year):
        self.keys = keys
        self.title = title
        self.year = year

    def property_as_sequence(self, whatever):
        for k in self.keys:
            yield k

MOCK_BOOKS = [
    MockBookForReadVsUnreadReport(['foo'], 'Foo 1', 2000),
    MockBookForReadVsUnreadReport(['bar'], 'Bar 1', 2010),
    MockBookForReadVsUnreadReport(['baz'], 'Baz 1', 1990),

    MockBookForReadVsUnreadReport(['foo'], 'Foo 2', 2001),
    MockBookForReadVsUnreadReport(['bar'], 'Bar 2', 2011),
    MockBookForReadVsUnreadReport(['baz'], 'Baz 2', 1991),

    MockBookForReadVsUnreadReport(['foo'], 'Foo 3', None), # Note lack of year
    MockBookForReadVsUnreadReport(['bar'], 'Bar 3', 2012),
    MockBookForReadVsUnreadReport(['baz'], 'Baz 3', 1992)
]

class TestGetKeysToBooksDict(unittest.TestCase):
    def test_vanilla(self):
        ret = get_keys_to_books_dict(MOCK_BOOKS, 'whatever')
        self.assertEqual(sorted(['foo', 'bar', 'baz']),
                         sorted(ret.keys()))
        self.assertEqual(sorted(['Foo 1', 'Foo 2', 'Foo 3']),
                         sorted([z.title for z in ret['foo']]))
        self.assertEqual(sorted(['Bar 1', 'Bar 2', 'Bar 3']),
                         sorted([z.title for z in ret['bar']]))
        self.assertEqual(sorted(['Baz 1', 'Baz 2', 'Baz 3']),
                         sorted([z.title for z in ret['baz']]))
