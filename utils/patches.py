#!/usr/bin/env python3
"""
Code to load in patches for book data.

The application of those patches is done in the Book class.
"""

from collections import namedtuple
from glob import glob
import os
import pdb
import re

MatchOrPatch = namedtuple('MatchOrPatch', 'property, value')

class PatchParsingError(Exception):
    pass

IGNORE_FILENAME_REGEX_PATTERNS = ['.*~$', # emacs temp files
                                  ]


def _load_patch_stream(inputstream, label='Unknown'):
    """
    Core functionality for load_patch_file(), factored out for testability.

    label is just a helpful text string (typically a filename) when logging
    or raising exceptions to help track things.
    """
    current_matches = []
    current_patches = []
    state = None
    for line_num, raw_line in enumerate(inputstream):
        line = raw_line.strip()
        mp_regex = re.search('^(\w+)\s*=\s*(.+)$', line)
        if mp_regex:
            if state == 'match_section' or not state:
                state = 'match_section'
                current_matches.append(MatchOrPatch(mp_regex.group(1), mp_regex.group(2)))
            elif state == 'patch_section':
                current_patches.append(MatchOrPatch(mp_regex.group(1), mp_regex.group(2)))
            else:
                # Not sure if this can actually happen, but catch it in case
                raise PatchParsingError('Unknown state %s in %s at line %d' %
                                        (state, label, line_num))
        elif line.startswith('#'):
            continue
        elif not line:
            if state == 'patch_section':
                yield current_matches, current_patches
                state = None
                current_matches = []
                current_patches = []
            elif not state:
                continue # Ignore consecutive blank lines
            else:
                raise PatchParsingError('Unexpected blank line in %s at line %d' %
                                        (label, line_num))
        elif line.startswith('-'):
            if state == 'match_section':
                state = 'patch_section'
            else:
                raise PatchParsingError('Unexpected divider line in %s at line %d' %
                                        (label, line_num))
        else:
            raise PatchParsingError('Unable to parse line in %s at line %d: [%s]' %
                                    (label, line_num, line))
    # Yield final patch
    if current_matches and current_patches:
        yield current_matches, current_patches


def load_patch_file(filename):
    """
    Yields ([MatchPatches], [MatchPatches]) loaded from specified file, the
    first list being the properties to match on, the second list being the
    properties to patch.
    """
    with open(filename) as filestream:
        for p in _load_patch_stream(filestream, filename):
            yield p


def load_patches(dirs):
    patches = []
    for dir in dirs:
        patch_files = glob(os.path.join(dir, '*'))
        for filename in patch_files:
            basename = os.path.basename(filename)
            ignore_this_file = False
            for bad_pattern in IGNORE_FILENAME_REGEX_PATTERNS:
                if re.search(bad_pattern, basename):
                    # print("Ignoring file %s" % (filename))
                    ignore_this_file = True
                    break
            if ignore_this_file:
                continue
            patchset = load_patch_file(filename)
            patches.extend(patchset)
    return patches


if __name__ == '__main__':
    patch_data = load_patches(['/proj/goodreads_analysis/patches'])
    pdb.set_trace()

