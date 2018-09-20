#!/usr/bin/env python3
"""
Render a timeline bar chart, showing books acquired each month, and if/when
they have been read.  Colour coding - if available - indicates how long it took
for them to be read.
"""

from utils.arguments import parse_args
from utils.colorama_canvas import (ColoramaCanvas, Fore, Back, Style,
                                   FG_RAINBOW, ColourTextObject)
from utils.export_reader import read_file
from utils.timeline_chart import TimelineChart

# Special shelves are those where there are external factors indicating how
# rapidly (or not) a book gets read - typically if they have been borrowed for
# a limited period of time.
SPECIAL_SHELVES = set(['library-loan']) # TODO: this should be in colour config
def is_on_special_shelves(bk, special_shelves=SPECIAL_SHELVES):
    if not special_shelves:
        special_shelves = set()
    return not special_shelves.isdisjoint(bk.shelves)


def time_on_tbr_pile_to_colours(bk):
    """
    Returns a ColourTextObject based
    on if/when the book was read, relative to when/how it was obtained
    """
    if bk.is_read:
        bg = Back.LIGHTBLACK_EX
        try:
            tbrt = bk.days_on_tbr_pile
            months = tbrt // 31
            try:
                fg = FG_RAINBOW[months]
            except IndexError:
                fg = Fore.BLACK
            if is_on_special_shelves(bk):
                # txt = u'\u2666' # BLACK DIAMOND SUIT
                txt = u'\u25cb' # WHITE CIRCLE (hollow really)
            else:
                txt = u'\u2b24' # BLACK LARGE CIRCLE
        except ValueError:
            fg = Fore.WHITE
            txt = '?'
    else:
        fg = Fore.WHITE
        bg = Back.RESET
        txt = u'\u00b7' # MIDDLE DOT
    return ColourTextObject(fg, bg, Style.RESET_ALL, txt)

if __name__ == '__main__':
    args = parse_args('Draw a timeline of when books were added and read',
                      'cdf')

    books = read_file(args=args)
    tl = TimelineChart(books)
    tl.process().render(colour_function=time_on_tbr_pile_to_colours)



