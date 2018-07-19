#!/usr/bin/env python3

def render_ratings_as_bar(ratings, width=50, unicode=False):
    total = sum(ratings[1:]) # Skip 0th item as we don't have 0 scores
    bits = []
    bodge_width = width - 1

    def unicode_bar_mapper(num):
        # https://en.wikipedia.org/wiki/Block_Elements
        return [None,    # 0 is not valid
                u'\u2581', # Lower one eight block
                u'\u2582', # Lower one quarter block
                u'\u2584', # Lower half block
                u'\u2586', # Lower three quarters block
                u'\u2588'][num] # Full block

    char_mapper = unicode_bar_mapper if unicode else str

    def bitlen(b):
        return sum([len(z) for z in b])

    while bitlen(bits) < width:
        # logging.warning('%f, %s, %d' % (bodge_width, bits, bitlen(bits)))
        bodge_width += 1
        bits = [char_mapper(z) * int(ratings[z] * (bodge_width/total))
                for z in range(1, 6)]

    return ''.join(bits)[:width]
