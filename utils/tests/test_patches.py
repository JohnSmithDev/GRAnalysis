#!/usr/bin/env python3

# import logging
# import pdb
import unittest

from ..patches import PatchParsingError, MatchOrPatch, _load_patch_stream

class TestPatches(unittest.TestCase):

    MOCK_PATCH1 = (
        'alpha=1',
        'beta = two',
        ' gamma     =     III     ',
        '-',
        'x=ichi',
        'y = ni',
        '    z     =    san   '
        )

    MOCK_PATCH2 = (
        'foo=bar',
        '----',
        'yin=yang'
        )

    def test_patch_basic(self):
        foo = list(_load_patch_stream(self.MOCK_PATCH1))
        self.assertEqual( [([MatchOrPatch('alpha', '1'),
                             MatchOrPatch('beta', 'two'),
                             MatchOrPatch('gamma', 'III')],
                            [MatchOrPatch('x', 'ichi'),
                             MatchOrPatch('y', 'ni'),
                             MatchOrPatch('z', 'san')])],
                          foo)

        bar = list(_load_patch_stream(self.MOCK_PATCH2))
        self.assertEqual( [([MatchOrPatch('foo', 'bar')],
                            [MatchOrPatch('yin', 'yang')])],
                          bar)

    def test_patch_multiple_in_one_file(self):
        lines = ['', '# here is a comment']
        lines.extend(self.MOCK_PATCH1)
        lines.extend(['', '# here is another comment'])
        lines.extend(self.MOCK_PATCH2)

        foo = list(_load_patch_stream(lines))
        self.assertEqual( [([MatchOrPatch('alpha', '1'),
                             MatchOrPatch('beta', 'two'),
                             MatchOrPatch('gamma', 'III')],
                            [MatchOrPatch('x', 'ichi'),
                             MatchOrPatch('y', 'ni'),
                             MatchOrPatch('z', 'san')]),
                           ([MatchOrPatch('foo', 'bar')],
                            [MatchOrPatch('yin', 'yang')])],
                          foo)

    def test_breaks_on_invalid_patch(self):
        lines = ['bork']
        lines.extend(self.MOCK_PATCH1)
        with self.assertRaises(PatchParsingError):
            whatever = list(_load_patch_stream(lines))

    def test_breaks_on_incomplete_patch(self):
        lines = ['one=1', '', 'two=2', '---', 'omega=z']
        lines.extend(self.MOCK_PATCH1)
        with self.assertRaises(PatchParsingError):
            whatever = list(_load_patch_stream(lines))



if __name__ == '__main__':
    unittest.main()


