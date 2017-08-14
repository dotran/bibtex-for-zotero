#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import sys
import time

import bibutils
from beautify_bib import beautify_bib


DEFAULT_URL = "http://localhost:23119/better-bibtex/collection?/0/7CJV7E9Q.biblatex"


def add_new_zotero_entries_to_bib(zotero_localhost_url, input_file, output_file=None):
    """
    This script will read your persistent/long-running BIB database and then
    pull new entries from your Zotero to create a joint, newer BIB file.
    
    You need to specify your existing BIB database as a base bib and specify
    the output BIB file to store the new database.
    """
    new_bib = bibutils.read_zotero_localhost(url=zotero_localhost_url,
                                             omit_indecent_citekey=True,
                                             verbose=True)
    new_bib = beautify_bib(new_bib)
    
    bib = bibutils.read_bib_file(input_file)
    bibutils.add_new_entries_to_basebib(base_bib=bib, new_bib=new_bib)
    
    bibutils.write_bib_file(beautify_bib(bib), output_file)


def parse_args(params, ext='.bib'):
    import os
    if len(params) == 0:
        raise Exception("No argument specified. Expected a localhost url and an input bib.")
    elif len(params) == 1:
        if 'http://localhost' in params[0]:
            raise Exception("Missing an input bib file.")
        elif ext in params[0]:
            url = DEFAULT_URL
            input_file = params[0]
            output_file = input_file
        else:
            raise Exception("Unknown command line argument: %s" % params[0])
    elif len(params) == 2:
        if 'http://localhost' in params[0] and ext in params[1]:
            url = params[0]
            input_file = params[1]
            output_file = input_file
        elif 'http://localhost' in params[1] and ext in params[0]:
            url = params[1]
            input_file = params[0]
            output_file = input_file
        else:
            raise Exception("Unknown command line arguments:\n\t%s\n\t%s" % (params[0], params[1]))
    elif len(params) == 3:
        assert 'http://localhost' in params[0] and ext in params[1] and ext in params[2], \
               "Unknown command line arguments"
        url = params[0]
        input_file = params[1]
        output_file = params[2]
    else:
        raise Exception("Too many arguments. Two are expected: input localhost url and output file.")
    
    url = url.replace('.biblatex', '.bibtex')
    if not os.path.isfile(input_file):
        raise Exception("Non-existing input bib file '%s'" % input_file)
    print("\nlocalhost_url = %s\ninput_file = %s\noutput_file = %s\n" % (url, input_file, output_file))
    
    return url, input_file, output_file


def main(params):
    add_new_zotero_entries_to_bib(*parse_args(params))


if __name__ == '__main__':
    startTime = time.time()
    main(sys.argv[1:])
    print('Processing done in %1.2f' % (time.time() - startTime), 'seconds.')
