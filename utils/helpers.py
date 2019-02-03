#!/usr/bin/env python3

import math

def generate_enumeration_prefix_format(lst):
    """
    Given a list - or any len()able object - return a Python format string of
    the form "%Nd.", where N is a number wide enough to cope with all elements
    in the list e.g. 2 if there are 99 items, but 3 if there are 100.
    """
    return '%%%dd. ' % (math.ceil(math.log(len(lst), 10)))

