#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Convert Zotero library/collection to BibTeX database and HTML files.

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

__version__ = '0.1'
__author__ = 'Do Tran'

import sys
import time

from zotero_to_bib import parse_args, zotero_to_bib
from bib_to_html import bib_to_html


def main(params):
    url, output_file = parse_args(params)
    new_bib = zotero_to_bib(url, output_file)
    bib_to_html(new_bib, output_file)


if __name__ == '__main__':
    startTime = time.time()
    main(sys.argv[1:])
    print('Processing done in %1.2f' % (time.time() - startTime), 'seconds.')
