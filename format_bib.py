#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import time
import csv
import re
import copy
import pprint
import bibutils


EXCLUDED_FIELDS = ('note', 'isbn', 'abstract', 'keywords', 'month', 'shorttitle', 'issn', 'copyright', 'file', 'timestamp', 'language', 'urldate')

infile  = "E:\\RES\\Lib\\Bib\\zbiball.bib"
outfile = "E:\\RES\\Lib\\Bib\\zbiball.bib"

def main(infile=infile, outfile=outfile):
    """
    This script is to read a .bib file and re-format it
    in order to create a cleaner and nicer ordering version.
    You need to only specify the 'infile' and 'outfile'.
    """
    bib_data = bibutils.read_bib_file(infile)
    bibutils.fix_and_split(bib_data)
    bibutils.format_output(bib_data, excluded_fields=EXCLUDED_FIELDS)
    bibutils.write_bib_file(bib_data, outfile)


if __name__ == '__main__':
    startTime = time.time()
    main()
    # print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
