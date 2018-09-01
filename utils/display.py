#!/usr/bin/env python3

import json

try:
    from colorama import Fore, Back, Style
    COLOUR_AVAILABLE = True
except ImportError:
    COLOUR_AVAILABLE = False

DEFAULT_WIDTH = 50


def render_ratings_as_bar(ratings, width=DEFAULT_WIDTH,
                          use_unicode=True, use_colour=COLOUR_AVAILABLE):
    """
    Given a list of star-rating counts, return a string of desired length
    representing the distribution of ratings.
    """

    def unicode_bar_mapper(num):
        # https://en.wikipedia.org/wiki/Block_Elements
        # https://en.wikipedia.org/wiki/Block_Elements
        return [None,    # 0 is not valid
                u'\u2582', # Lower one quarter block
                u'\u2583', # Lower three eighths block
                u'\u2584', # Lower half block
                u'\u2585', # Lower five eights block
                u'\u2586'][num] # Lower three quarters block

    char_mapper = unicode_bar_mapper if use_unicode else str

    def colour_mapper(num):
        if use_colour:
            return ([None,    # 0 is not a valid rating
                     Fore.LIGHTYELLOW_EX,
                     Fore.LIGHTGREEN_EX,
                     Fore.LIGHTCYAN_EX,
                     Fore.LIGHTBLUE_EX,
                     Fore.LIGHTMAGENTA_EX][num], Style.RESET_ALL)
        else:
            return ('', '')


    # Note: this feels somewhat overdone - I'd not be in the least bit
    #       surprised if there's a far simpler implementation.

    total = sum(ratings[1:]) # Skip 0th item as we don't have 0 scores

    def calculate_bar_width_for_rating(rating):
        return ratings[rating] * (width/total)

    bar_vals = [calculate_bar_width_for_rating(z) for z in range(1,6)]

    # Note from this point onwards we switch to 5 element arrays, element 0
    # is for 1-star, etc

    # Get the fractional part of the bars
    bar_scores = [(i, z - int(z)) for i, z in enumerate(bar_vals)]

    # Work out the priority of which elements  we should increment to reach
    # the target width
    sorted_bar_scores = sorted(bar_scores, key=lambda z: -z[1])


    # Regenerate the "base" integer values
    bar_vals = [int(z) for z in bar_vals]

    # Now increment the priority elements to reach the target width
    for i in range(width - sum(bar_vals)):
        bar_vals[ sorted_bar_scores[i][0] ] += 1


    def stringbit2(rating, qty):
        col_on, col_off = colour_mapper(rating)
        return '%s%s%s' % (col_on, char_mapper(rating) * qty, col_off)

    # Note the increment-by-1 here, because the colour and character lists
    # have a "dummy" 0-th element
    bits = [stringbit2(i+1, z) for i, z in enumerate(bar_vals)]

    return ''.join(bits)





COLOUR_MAPPINGS = {
    'LIGHTBLACK': 'LIGHTBLACK_EX',
    'LIGHTBLUE': 'LIGHTBLUE_EX',
    'LIGHTCYAN': 'LIGHTCYAN_EX',
    'LIGHTGREEN': 'LIGHTGREEN_EX',
    'LIGHTMAGENTA': 'LIGHTMAGENTA_EX',
    'LIGHTRED': 'LIGHTRED_EX',
    'LIGHTWHITE': 'LIGHTWHITE_EX',
    'LIGHTYELLOW': 'LIGHTYELLOW_EX'
}
STYLE_MAPPINGS = {
    # TODO: maybe (unlike the colours, these seem reasonable)
}

DEFAULT_CHAR = '\u259a\u259a' # checkerboard-like

def translate_colour(col, fb=Fore):
    col = col.upper()
    try:
        return getattr(fb, COLOUR_MAPPINGS[col])
    except KeyError:
        return getattr(fb, col)

def translate_style(st):
    st = st.upper()
    try:
        return getattr(Style, STYLE_MAPPINGS[st])
    except KeyError:
        return getattr(Style, st)

def translate_char(ch):
    # Do we need this?  Obviously not with the current implementation, but
    # perhaps we might need to do more (e.g. for non-colour rendering?)
    return ch




class ColourConfig(object):

    def __init__(self, json_data):
        self.colour_cfg = json.load(json_data)
        self.colour_guide = {}

    def get_colour_bits(self, shelf_tuple):
        if COLOUR_AVAILABLE:
            fore = Fore.WHITE
            back = Back.LIGHTBLACK_EX
            style = ''
        ch = DEFAULT_CHAR
        used_bits = {}
        for colour_rule, values in self.colour_cfg[::-1]:
            if colour_rule in shelf_tuple:
                if COLOUR_AVAILABLE:
                    if 'fg' in values:
                        fore = translate_colour(values['fg'], Fore)
                        used_bits['fg'] = colour_rule
                    if 'bg' in values:
                        back = translate_colour(values['bg'], Back)
                        used_bits['bg'] = colour_rule
                    if 'st' in values:
                        style = translate_style(values['style'])
                        used_bits['st'] = colour_rule
                if 'ch' in values:
                    ch = translate_char(values['ch'])
                    used_bits['ch'] = colour_rule
        if COLOUR_AVAILABLE:
            blob_bits = (fore, back, style, ch)
            blob = self._blobbify(blob_bits)

            relevant_shelves = sorted(set(used_bits.values()))
            self.colour_guide[' / '.join(relevant_shelves)] = blob

            return blob_bits
        else:
            return ch

    def _blobbify(self, blob_bits):
        blob = ''.join([z for z in blob_bits if z])
        if COLOUR_AVAILABLE:
            blob += Style.RESET_ALL
        return blob

    def get_colour_blob(self, shelf_tuple):
        return self._blobbify(self.get_colour_bits(shelf_tuple))
