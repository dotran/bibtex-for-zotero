#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import time
import bibutils


EXCLUDED_FIELDS = (
    'note',
    # 'isbn',
    # 'abstract',
    # 'month',
    # 'file',
    # 'urldate',
    'keywords',
    'shorttitle',
    'issn',
    'copyright',
    'timestamp',
    'language',
    'lccn',
    'pmid',
    'pmcid',
    'dateadded')

infile  = "E:\\RES\\Lib\\Bib\\zbiball.bib"
outfile = "E:\\RES\\Lib\\Bib\\zbiball.bib"


def beautify_bi(input_file, output_file):
    """
    Reads a BIB file and re-format it to create a cleaner and nicer version.
    You only need to specify the input and output bib files.
    """
    bib = bibutils.read_bib_file(input_file)
    


def main(infile=infile, outfile=outfile):
    bibutils.fix_and_split(bib_data)
    bibutils.format_output(bib_data, excluded_fields=EXCLUDED_FIELDS)
    bibutils.write_bib_file(bib_data, outfile)


if __name__ == '__main__':
    startTime = time.time()
    main()
    # print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
