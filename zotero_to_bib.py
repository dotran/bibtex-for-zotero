#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
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

outfile  = "./newtest/testlib.bib"
# outfile  = "E:\\RES\\Lib\\Bib\\zbiball.bib"


def read_zotero_to_bib(zotero_localhost_url):
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
    
    bib = bibutils.read_zotero_localhost_bib(zotero_localhost_url)
    bibutils.fix_and_split(bib, omit_indecent_citekey=True)
    
    # Sort by "Date Added"
    bib = sorted(bib, key=lambda k: k['data']['dateadded'], reverse=False)
    bibutils.format_output(bib, excluded_fields=EXCLUDED_FIELDS, keep_both_doi_url=True)


def main():
    # Export the whole Zotero library to BibTeX using Better BibTeX
    URL = "http://localhost:23119/better-bibtex/library?library.bibtex"
    
    # Export only a specific collection
    # URL = "http://localhost:23119/better-bibtex/collection?/0/QBN8FDDA.bibtex"
    
    read_zotero_to_bib(URL)
    
    new_bib = bibutils.read_zotero_localhost_bib(URL)
    bibutils.fix_and_split(new_bib, omit_indecent_citekey=True)
    bibutils.format_output(new_bib, excluded_fields=EXCLUDED_FIELDS)
    bibutils.write_bib_file(new_bib, outfile)


if __name__ == '__main__':
    startTime = time.time()
    main()
    print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
