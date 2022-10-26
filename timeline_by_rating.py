#!/usr/bin/env python3
"""
Render a timeline bar chart, showing books acquired each month, and if/when
they have been read.  Colour coding shows how many stars they were rated as.

Opinion: Currently this isn't particularly appealing visually, and the solid
         circles might be better rendered in 2-character columns.
"""

from utils.arguments import parse_args
#from utils.colorama_canvas import (ColoramaCanvas, Fore, Back, Style,
# FG_RAINBOW, ColourTextObject)
from utils.colour_coding import rating_to_colours
from utils.export_reader import read_file
from utils.timeline_chart import TimelineChart


if __name__ == '__main__':
    args = parse_args('Draw a timeline of when books were added and read',
                      'cdf')

    books = read_file(args=args)
    tl = TimelineChart(books)
    tl.process().render(colour_function=rating_to_colours)
