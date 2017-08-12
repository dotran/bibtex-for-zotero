#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import shutil
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


def zotero_to_html():
    """
    Export the whole Zotero library (or a collection) to BibTeX using Better BibTeX
    and use the BibTeX2HTML tool to make nicely formatted HTML files with
    with abstracts, links, etc.
    
    NOTE: This is the UPDATED VERSION which splits the large bib database
    (exceeding the Hash size of 35000) into smaller junks.
    
    UPDATE: To sort the .bib wrt "Date Added", we must have access to this field,
    which is not available by default in the Zotero Better BibTeX translator.
    Thus we need to add this field to the output by using an API of Better BibTeX
    which allows accessing the reference just before it's written out and cached.
    This can be achieved by adding the a JavaScript snippet to the Postscript box
    in the Advanced tab of the Better BibTeX preferences:
    
    if (Translator.BetterBibTeX) {
        if (this.item.dateAdded) {
            this.add({ name: 'dateadded', value: this.item.dateAdded });
        }
    }
    
    We can use this method to add any Zotero field to the Better BibTeX .bib output.
    Ref: https://github.com/retorquere/zotero-better-bibtex/wiki/Scripting
    """
    
    URL = "http://localhost:23119/better-bibtex/library?library.bibtex"
    # URL = "http://localhost:23119/better-bibtex/collection?/0/QBN8FDDA.bibtex"  # for only one collection
    # URL = "http://localhost:23119/better-bibtex/collection?/0/--GPU.bibtex"
    
    URL = "http://localhost:23119/better-bibtex/collection?/0/VWFR4ZR3.bibtex"
    
    
    # Step 1: Export Zotero library/collection to a .bib file
    new_bib = bibutils.read_zotero_localhost_bib(URL)
    bibutils.fix_and_split(new_bib, omit_indecent_citekey=True)
    new_bib = sorted(new_bib, key=lambda k: k['data']['dateadded'], reverse=False)  # sort by "Date Added"
    bibutils.format_output(new_bib, excluded_fields=EXCLUDED_FIELDS, keep_both_doi_url=True)
    
    
    # Sort the database wrt 'year' for the HTML outputs
    new_bib_sorted = sorted(new_bib,
                            key=lambda k: k['data']['year'] if 'year' in k['data'].keys() else 0,
                            reverse=True)
    
    
    bibutils.bib_to_html(bib=new_bib_sorted,
                         path=os.path.dirname(outfile),
                         filename=os.path.basename(outfile))
    
    
    # Step 5: Format the generated .bib file to remove the fields file, abstract, etc.
    # format_bib.main(infile=outfile, outfile=outfile)  # this is obsolete
    bibutils.format_output(new_bib, excluded_fields=EXCLUDED_FIELDS + ('abstract', 'month', 'file'))
    bibutils.write_bib_file(new_bib, 'outfile.bib')
    
    # Step 6 (additional): Check for any duplicate citation keys
    bibutils.check_duplicate_citekeys(new_bib)


def main():
    zotero_to_html()


if __name__ == '__main__':
    startTime = time.time()
    main()
    print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
