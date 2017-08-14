#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Export the whole Zotero library (or a collection) to BibTeX using Better
BibTeX and use the BibTeX2HTML tool to make nicely formatted HTML files with
with abstracts, links, etc.

NOTE #1:
I decided to use the Zotero localhost utility along with Better BibTeX, as
it's time consuming to pull items from the Zotero Web API (either with HTTP
request or with the help of the "pyzotero" library), and it's also tough
(though possible) to read from the local "zotero.sqlite"

[see, http://www.texmacs.org/tmweb/miguel/task-zotero.en.html
      https://github.com/smathot/qnotero/blob/master/libzotero/libzotero.py]

NOTE #2:
This is the UPDATED VERSION which splits the large bib database (exceeding
the Hash size of 35000) into smaller junks.

UPDATE:
To sort the bib wrt "Date Added", we must have access to this field, which
isn't available by default in the Better BibTeX translator for Zotero. Thus
we need to add this field to the output by using an API of Better BibTeX
which allows accessing the reference just before it's written out and
cached. This can be achieved by adding the a JavaScript snippet to the
Postscript box in the Advanced tab of the Better BibTeX preferences:

if (Translator.BetterBibTeX) {
    if (this.item.dateAdded) {
        this.add({ name: 'dateadded', value: this.item.dateAdded });
    }
}

We can use this method to add any Zotero field to the Better BibTeX .bib output.
Ref: https://github.com/retorquere/zotero-better-bibtex/wiki/Scripting
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import time
import bibutils

from zotero_to_bib import parse_args, zotero_to_bib


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
    
    bibutils.bib_to_html(bib,
                         path=os.path.dirname(output_file),
                         filename=os.path.basename(output_file))


def main(params):
    url, output_file = parse_args(params)
    new_bib = zotero_to_bib(url, output_file)
    bib_to_html(new_bib, output_file)


if __name__ == '__main__':
    startTime = time.time()
    main(sys.argv[1:])
    print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
