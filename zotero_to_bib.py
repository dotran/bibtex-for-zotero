#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import sys
import time
import bibutils


DEFAULT_URL     = "http://localhost:23119/better-bibtex/collection?/0/7CJV7E9Q.biblatex"
DEFAULT_OUTPUT  = "./biblio.bib"
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


def zotero_to_bib(zotero_localhost_url, output_file):
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
    
    new_bib = bibutils.read_zotero_localhost(url=zotero_localhost_url,
                                             omit_indecent_citekey=True,
                                             verbose=True)
    
    bib = sorted(new_bib,
                 key=lambda k: k['data']['dateadded'],  # sort by "Date Added"
                 reverse=False)
    
    bibutils.format_output(bib,
                           excluded_fields=EXCLUDED_FIELDS,
                           keep_both_doi_url=False)
    
    bibutils.write_bib_file(bib, output_file)
    
    return new_bib


def parse_args(params):
    if len(params) == 0:
        print("No argument specified. Using the preset localhost url and output file.")
        url = DEFAULT_URL
        output_file = DEFAULT_OUTPUT
    elif len(params) == 1:
        if 'http://localhost' in params[0]:
            url = params[0]
            output_file = DEFAULT_OUTPUT
        elif '.bib' in params[0]:
            url = DEFAULT_URL
            output_file = params[0]
        else:
            raise Exception("Unknown command line argument: %s" % params[0])
    elif len(params) == 2:
        if 'http://localhost' in params[0] and '.bib' in params[1]:
            url = params[0]
            output_file = params[1]
        elif 'http://localhost' in params[1] and '.bib' in params[0]:
            url = params[1]
            output_file = params[0]
        else:
            raise Exception("Unknown command line arguments:\n\t%s\n\t%s" % (params[0], params[1]))
    else:
        raise Exception("Too many arguments. Two are expected: input localhost url and output file.")
    
    url = url.replace('.biblatex', '.bibtex')
    print("localhost_url = {arg1}\noutput_file = {arg2}".format(arg1=url, arg2=output_file))
    
    return url, output_file


def main(params):
    zotero_to_bib(*parse_args(params))


if __name__ == '__main__':
    startTime = time.time()
    main(sys.argv[1:])
    print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
