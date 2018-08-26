#!/usr/bin/env python3
"""
Show which shelves are least read (in terms of books read/books owned)
"""

from utils.export_reader import TEST_FILE, read_file
from utils.transformers import ReadVsUnreadStats


if __name__ == '__main__':
    ReadVsUnreadStats(read_file(TEST_FILE), 'user_shelves').process().render()
