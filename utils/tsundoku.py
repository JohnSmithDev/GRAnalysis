#!/usr/bin/env python3
"""
Draw a graphical representation of your to-be-read books (aka Mount Tsundoku)
and/or your read books
"""

from __future__ import division

from collections import defaultdict, namedtuple
# import json
import pdb
import sys

try:
    from colorama import Fore, Back, Style
    COLOUR_AVAILABLE = True
except ImportError:
    COLOUR_AVAILABLE = False

from utils.arguments import parse_args
# from utils.display import ColourConfig
from utils.colorama_canvas import ColoramaCanvas, COLORAMA_RESET
# from utils.export_reader import read_file

GROUP_BY_COLOURS = True

Count = namedtuple('Count', 'key, count')
Aggregates = namedtuple('Aggregates', 'max_count, num_columns, total')


def calculate_x_positions(count_data, offset=0):
    """
    Given a list of (presumably) Counts ordered in (roughly) descending order
    return a list of the indices to that list in a "mountain" esque form i.e.
    with the biggest ones in the middle, going down as you go further out to
    the start or end of the list.  Also keeps like 'keys' grouped with like.

    (You can pass this an unordered list, but the return value probably
     won't be terribly useful/interesting.)

    >>> calculate_x_positions(Count('a', 10), Count('b', 8), Count('c', 6), 3)
    [4, 3, 5]

    """
    right = 1
    left = 0
    currently_going_right = False
    prev_key = None

    temp_positions = []
    for k, _  in count_data:
        if k == prev_key:
            if currently_going_right:
                temp_positions.append(right)
                right += 1
            else:
                temp_positions.append(left)
                left -= 1
        else:
            currently_going_right = not currently_going_right
            if currently_going_right:
                temp_positions.append(right)
                right += 1
            else:
                temp_positions.append(left)
                left -= 1
        prev_key = k
    return [z - left -1 + offset for z in temp_positions]


def _squash_calculation(number, target):
    """
    Given a number, return a list of roughly equal numbers that together
    sum up to number, but are all less than or equal to target.

    >>> _squash_calculation(9, 3)
    [3, 3, 3]
    >>> _squash_calculation(9, 4)
    [3, 3, 3]
    >>> _squash_calculation(9, 5)
    [5, 4]
    >>> _squash_calculation(9, 8)
    [5, 4]
    >>> _squash_calculation(9, 9)
    [9]
    >>> _squash_calculation(9, 10)
    [9]
    """
    if number <= target:
        return [number]
    elif number % target == 0:
        return [target for _ in range(number // target)]
    else:
        number_of_items = (number // target) + 1
        remainder = number % number_of_items
        base_value = number // number_of_items
        vals = [base_value for _ in range(number_of_items)]
        for i in range(remainder):
            vals[i] += 1
        return vals

def squash(key_to_books_dict, max_height=None):
    """
    Given a dict of keys->set(Book), split up the larger ones so that no value
    exceeds target_height.
    If max_height is not specified, then a - hopefully - reasonable value
    is calculated.
    """
    counts = [Count(k, len(v)) for k, v in key_to_books_dict.items()]

    if max_height is None:
        num_counts = len(counts)
        # This seems to be a reasonable heuristic using the test data I
        # currently have.
        if num_counts < 10:
            max_height = int(sum([z[1] for z in counts]) / len(counts))
        else:
            max_height = int(2 * sum([z[1] for z in counts]) / len(counts))

    sorted_counts = sorted(counts, key=lambda z: -z.count)
    squashed_counts = []
    for c in sorted_counts:
        for v in _squash_calculation(c.count, max_height):
            squashed_counts.append(Count(c.key, v))
    return squashed_counts



class Tsundoku(object):
    def __init__(self, col_cfg, group_by='user_shelves'):
        self.col_cfg = col_cfg
        self.group_by = group_by

        self.unread_shelves = defaultdict(set)
        self.read_shelves = defaultdict(set)

    def process(self, books):
        for bk in books:
            # composite_key = tuple(sorted(bk.user_shelves))
            # composite_key = (bk.decade,)
            composite_key = bk.property_as_hashable(self.group_by)
            if GROUP_BY_COLOURS:
                composite_key = self.col_cfg.get_colour_bits(composite_key)
            if bk.is_read:
                self.read_shelves[composite_key].add(bk)
            else:
                self.unread_shelves[composite_key].add(bk)

    def postprocess(self):
        self.unread_counts = squash(self.unread_shelves)
        self.read_counts = squash(self.read_shelves)
        self.unread_aggregates = Aggregates(
            max([z.count for z in self.unread_counts]),
            len(self.unread_counts),
            sum([z.count for z in self.unread_counts]),
        )
        self.read_aggregates = Aggregates(
            max([z.count for z in self.read_counts]),
            len(self.read_counts),
            sum([z.count for z in self.read_counts])
        )

    def render(self):
        OLD_CODE = """
        for label, data in [('Unread', self.unread_counts),
                            ('Read', self.read_counts)]:
            self._render_read_counts(label, data)
        """

        offset_for_y_axis_label = len(str(max(self.unread_aggregates.max_count,
                                              self.read_aggregates.max_count)))

        height = self.unread_aggregates.max_count + self.read_aggregates.max_count + 1
        width = 2 * max(self.unread_aggregates.num_columns, self.read_aggregates.num_columns)
        ground_level = self.unread_aggregates.max_count + 1 # This is like the x-axis of a graph

        x_padding = 0
        y_padding = 0

        self.cc = ColoramaCanvas(width + 20, height + 1, x_padding, y_padding)

        self.cc.print_at(offset_for_y_axis_label+1, ground_level, '\u2b61 unread (%d) \u2b61' %
                         (self.unread_aggregates.total))
        rstr ='\u2b63 read (%d) \u2b63' % (self.read_aggregates.total)
        self.cc.print_at(3 + width - len(rstr), ground_level, rstr)


        # Ensure that both halves of the mountain are roughly centered,
        # even if one half has more columns than the other
        offset_for_symmetry = abs(int((self.read_aggregates.num_columns -
                                       self.unread_aggregates.num_columns) / 2))
        if self.read_aggregates.num_columns > self.unread_aggregates.num_columns:
            unread_x_offset = offset_for_symmetry + offset_for_y_axis_label
            read_x_offset = offset_for_y_axis_label
        else:
            read_x_offset = offset_for_symmetry + offset_for_y_axis_label
            unread_x_offset = offset_for_y_axis_label

        x_positions = calculate_x_positions(self.unread_counts, unread_x_offset)
        self._render_half_mountain(self.unread_counts, x_positions, ground_level,
                                   offset_for_y_axis_label,
                                   max_count=self.unread_aggregates.max_count,
                                   going_up=True)

        x_positions = calculate_x_positions(self.read_counts, read_x_offset)
        self._render_half_mountain(self.read_counts, x_positions, ground_level,
                                   offset_for_y_axis_label,
                                   max_count=self.read_aggregates.max_count,
                                   going_up=False)

        self.cc.render()

    def _render_half_mountain(self, counts, x_positions, ground_level,
                              offset_for_y_axis_label,
                              max_count=None,
                              going_up=True):

        if going_up:
            axis_marker = u'\u2581 ' # Lower one eighth block
        else:
            axis_marker = u'\u2594 ' # Upper one eighth block

        def calculate_y_pos(y):
            if going_up:
                return ground_level - y - 1
            else:
                return ground_level + y + 1

        if max_count is None:
            # Work it out ourselves
            max_count = max([z.count for z in counts])
        if max_count < 50:
            step = 5
        else:
            step = 10

        for i in range(0, max_count, step):
            self.cc.reset_style()
            txt = str(i)
            self.cc.print_at(offset_for_y_axis_label - len(txt),
                             calculate_y_pos(i) if i == 0 else calculate_y_pos(i-1),
                             txt)
            self.cc.current_fg = Fore.LIGHTBLACK_EX
            self.cc.print_at(offset_for_y_axis_label, calculate_y_pos(i),
                             axis_marker * int((self.cc.width - offset_for_y_axis_label)/2))
        for i, (k, v) in enumerate(counts):
            fg, bg, style, txt = k
            self.cc.current_fg = fg
            self.cc.current_bg = bg
            self.cc.current_style = style
            for y in range(v):
                self.cc.print_at(x_positions[i] * 2, calculate_y_pos(y),
                                 txt)


    def _render_read_counts(self, label, sorted_counts):
        """
        The very first attempt at rendering bars - no longer in use,
        but may be helpful for debugging
        """
        print('= %s =' % (label))
        for i, (k, v) in enumerate(sorted_counts):
            if GROUP_BY_COLOURS:
                blob = self.col_cfg._blobbify(k)
            else:
                blob = self.col_cfg.get_colour_blob(k)
            print('%2d. %3d %s %s' % (i+1,
                                      v,
                                      blob * v,
                                      "" # k
            ))


            ABORTED_SUBSET_CODE = """
            for j in range(i+1, len(sorted_unread_counts)):
                test_against = sorted_unread_counts[j][0]
                if unread_shelves[k].issuperset(unread_shelves[test_against]):
                    print('  contains %s' % (test_against))
            """

    def output_colour_key(self):
        print('\n%sColour key:' % (COLORAMA_RESET))
        for shelves, colour in sorted(self.col_cfg.colour_guide.items(),
                                      key=lambda z: z[0]):
            if not shelves:
                shelves = 'Default'
            print('%s : %s' % (colour, shelves))

