#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import time

import bibutils


EXCLUDED_FIELDS = (
    'note',
    'isbn',
    'abstract',
    'month',
    'file',
    'urldate',
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


def beautify_bib(new_bib):
    """
    Reads a BIB file and re-format it to create a cleaner and nicer version.
    You only need to specify the input and output bib files.
    """
    try:
        bib = sorted(new_bib,
                     key=lambda k: k['data']['dateadded'],  # sort by "Date Added"
                     reverse=False)
    except KeyError:
        print("WARNING: Absent 'dateadded' field ==> Sorting skipped.")
        bib = new_bib
    
    bibutils.format_output(bib,
                           excluded_fields=EXCLUDED_FIELDS,
                           keep_both_doi_url=False)
    return bib


def parse_args(params, ext=['.bib', '.html']):
    import os
    if len(params) == 0:
        raise Exception("No argument specified. Require an input bib file.")
    elif len(params) == 1:
        if params[0].endswith('.bib'):
            input_file = params[0]
            output_file = input_file
        else:
            raise Exception("An input bib file expected. Received: %s" % params[0])
    elif len(params) == 2:
        if params[0].endswith('.bib') and any(params[1].endswith(x) for x in ext):
            input_file = params[0]
            output_file = params[1]
        else:
            raise Exception("Unknown command line arguments:\n\t%s\n\t%s" % (params[0], params[1]))
    else:
        raise Exception("Too many arguments. Two are expected: an input bib and an output file.")
    
    if not os.path.isfile(input_file):
        raise Exception("Non-existing input bib file '%s'" % input_file)
    print("input_bib = {arg1}\noutput_file = {arg2}".format(arg1=input_file, arg2=output_file))
    
    return input_file, os.path.splitext(output_file)[0]


def main(params):
    input_file, output_file = parse_args(params)
    new_bib = bibutils.read_bib_file(input_file,
                                     omit_indecent_citekey=True,
                                     verbose=True)
    bib = beautify_bib(new_bib)
    bibutils.write_bib_file(bib, output_file)


if __name__ == '__main__':
    startTime = time.time()
    main(sys.argv[1:])
    print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
