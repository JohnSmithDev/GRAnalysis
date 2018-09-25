#!/usr/bin/env python3

from utils.colorama_canvas import (ColoramaCanvas, Fore, Back, Style,
                                   FG_RAINBOW, ColourTextObject)

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
