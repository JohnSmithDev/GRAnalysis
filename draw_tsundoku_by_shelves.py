#!/usr/bin/env python3
"""
Draw a graphical representation of your to-be-read books (aka Mount Tsundoku)
and/or your read books, colour coded by shelves.
"""

from utils.arguments import parse_args
from utils.export_reader import read_file
from utils.tsundoku import Tsundoku

if __name__ == '__main__':
    args = parse_args('Render a graphical representation of your to-be-read pile '
                      'aka Mount Tsundoku, colour coded by shelves',
                      'cdf')

    col_cfg = args.colour_cfg.select_category('shelves')
    t = Tsundoku(col_cfg, 'user_shelves')
    t.process(read_file(args=args))
    t.postprocess()
    t.render()
    t.output_colour_key() # Q: Or do this within .render() method?

