#!/usr/bin/env python3
"""
Render a timeline bar chart, showing books acquired each month, and if/when
they have been read.  Colour coding shows how many stars they were rated as.

Opinion: Currently this isn't particularly appealing visually, and the solid
         circles might be better rendered in 2-character columns.
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

def rating_to_colours(bk):
    """
    Returns a ColourTextObject based
    on if the book was read and how it was rated
    """
    # CIRCLED_NUMBERS = (None, u'\u2460', u'\u2461', u'\u2462', u'\u2463', u'\u2464')
    CIRCLED_NUMBERS = (None, u'\u2776', u'\u2777', u'\u2778', u'\u2779', u'\u277a') # Neg/dingbat
    COLOURS = (None,
               Fore.BLUE,
               Fore.GREEN,
               Fore.YELLOW, # Bronze-ish, also tried LIGHTRED_EX
               Fore.WHITE, # Silver-ish, also tried LIGHTWHITE_EX
               Fore.LIGHTYELLOW_EX) # Gold-ish
    fg = Fore.RESET
    if bk.is_read:
        if bk.rating:
            txt = CIRCLED_NUMBERS[bk.rating]
            fg = COLOURS[bk.rating]
        else:
            txt = '?'
    else:
        txt = u'\u00b7' # MIDDLE DOT
    return ColourTextObject(fg, Back.RESET, Style.RESET_ALL, txt)


if __name__ == '__main__':
    args = parse_args('Draw a timeline of when books were added and read',
                      'cdf')

    books = read_file(args=args)
    tl = TimelineChart(books)
    tl.process().render(colour_function=rating_to_colours)



