#!/usr/bin/env python3

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

