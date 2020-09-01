#!/usr/bin/env python3
"""
Draw a graphical representation of your to-be-read books (aka Mount Tsundoku)
and/or your read books, colour coded by shelves (or some other dimension derived
from symlinked filename).
"""

from os.path import basename
import sys

from utils.arguments import parse_args
from utils.export_reader import read_file
from utils.tsundoku import Tsundoku

pattern_to_key = {
    'shelves': 'user_shelves',
    'decades': 'decade'
}

def determine_attributes(script_name=None):
    if not script_name:
        script_name = basename(sys.argv[0])
    for pat, k in pattern_to_key.items():
        if pat in script_name:
            key_attribute_name = pat
            key_attribute = k
            break
    else:
        raise Exception('No attribute found in script name')
    return key_attribute_name, key_attribute

if __name__ == '__main__':
    key_attribute_name, key_attribute = determine_attributes()


    args = parse_args('Render a graphical representation of your to-be-read pile '
                      'aka Mount Tsundoku, colour coded by %s' % (key_attribute_name),
                      'cdfl')

    col_cfg = args.colour_cfg.select_category(key_attribute_name)
    t = Tsundoku(col_cfg, key_attribute)
    t.process(read_file(args=args))
    t.postprocess(max_height=args.limit)
    t.render()
    t.output_colour_key() # Q: Or do this within .render() method?

