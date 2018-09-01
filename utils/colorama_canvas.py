#!/usr/bin/env python3
"""
Library to output colo(u)rized text at any point across a canvas.

(I guess this is comparable to what curses does, although I haven't used that
in ~20 years...)
"""

import logging

from colorama import Fore, Back, Style

COLORAMA_RESET = Fore.RESET + Back.RESET + Style.RESET_ALL



class ColoramaCanvas(object):

    def __init__(self, width, height, x_padding=0, y_padding=0,
                 output_function=print):

        self.width = width
        self.height = height

        self.x_padding = x_padding
        self.y_padding = y_padding

        self.output_function = output_function

        self.create_empty_canvas()
        self.move_to(0, 0)

        self.current_fg = None
        self.current_bg = None
        self.current_style = None


    def create_empty_canvas(self):
        # Note that the 2-d arrays are stored in order (y, x) rather than
        # (x, y) - this is a fairly arbitrary decision, based on simplicity
        # of render() method
        self.chars = [ [' ' for x in range(self.width)]
                              for y in range(self.height)]
        self.fg = [ [None for x in range(self.width)]
                              for y in range(self.height)]
        self.bg = [ [None for x in range(self.width)]
                              for y in range(self.height)]
        self.style = [ [Style.RESET_ALL for x in range(self.width)]
                              for y in range(self.height)]

    def reset_style(self):
        self.current_fg = Fore.RESET
        self.current_bg = Back.RESET
        self.current_style = Style.RESET_ALL

    def _output(self, text, x=None, y=None):
        if x is None:
            x = self.cursor_x
        if y is None:
            y = self.cursor_y

        for i, ch in enumerate(text):
            try:
                self.chars[y][x + i] = ch
            except IndexError as err:
                logging.error('Cannot print "%s" at (%d,%d) in %dx%d canvas' %
                              (ch, x, y, self.width, self.height))
                raise(err)
            if self.current_fg:
                self.fg[y][x + i] = self.current_fg
            if self.current_bg:
                self.bg[y][x + i] = self.current_bg
            if self.current_style:
                self.style[y][x + i] = self.current_style


    def print_at(self, x, y, text):
        self._output(text, x, y)
        self.move_to(x, y + 1)

    def print(self, text):
        self._output(text)
        self.move_to(self.cursor_x, self.cursor_y + 1)

    def move_to(self, x, y):
        self.cursor_x = x
        self.cursor_y = y

    def render(self):
        for _ in range(self.y_padding):
            print(COLORAMA_RESET_STRING)
        for y in range(self.height):
            bits = []
            for x in range(self.width):
                fg = self.fg[y][x] or ''
                bg = self.bg[y][x] or ''
                style = self.style[y][x] or Style.RESET_ALL
                bits.append('%s%s%s%s' % (style, fg, bg, self.chars[y][x]))
            line = '%s%s%s' % (' ' * self.x_padding,
                               ''.join(bits),
                               ' ' * self.x_padding)
            self.output_function(line)
        self.reset_style()
        for _ in range(self.y_padding):
            print(COLORAMA_RESET)

    def clear(self):
        # https://stackoverflow.com/questions/2084508/clear-terminal-in-python
        self.output_function(chr(27) + '[2J')


if __name__ == '__main__':
    cc = ColoramaCanvas(20,20)
    # cc.clear()
    cc.current_fg = Fore.LIGHTRED_EX
    cc.current_bg = Back.LIGHTBLACK_EX
    cc.print_at(5, 5, 'Hello')
    cc.current_fg = Fore.LIGHTYELLOW_EX
    cc.print_at(10, 10, 'World')
    cc.print('!!!!!')
    cc.render()

