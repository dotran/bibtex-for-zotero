#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import time

import bibutils
from beautify_bib import parse_args, beautify_bib


EXCLUDED_FIELDS = (
    'note',
    'isbn',
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


def bib_to_html(bib, output_file):
    bib = sorted(bib,  # sort the database wrt 'year' for the HTML outputs
                 key=lambda k: k['data']['year'] if 'year' in k['data'].keys() else 0,
                 reverse=True)
    
    bibutils.format_output(bib,
                           excluded_fields=EXCLUDED_FIELDS,
                           keep_both_doi_url=True)
    
    bibutils.bib2html(bib,
                      path=os.path.dirname(output_file),
                      filename=os.path.basename(output_file))


def main(params):
    input_file, output_file = parse_args(params)
    new_bib = bibutils.read_bib_file(input_file,
                                     omit_indecent_citekey=True,
                                     verbose=True)
    bib = beautify_bib(new_bib)
    bibutils.write_bib_file(bib, output_file)
    bib_to_html(new_bib, output_file)


if __name__ == '__main__':
    startTime = time.time()
    main(sys.argv[1:])
    print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
