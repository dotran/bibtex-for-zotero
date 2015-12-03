#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import time
import csv
import re
import copy
import pprint
from pyzotero import zotero
import bibutils


EXCLUDED_FIELDS = ('note', 'isbn', 'abstract', 'keywords', 'month', 'shorttitle', 'issn', 'copyright', 'file', 'timestamp', 'language', 'urldate')

outfile  = "E:\\RES\\Lib\\Bib\\zbiball.bib"
# outfile = "./biblio.bib"

def main():
    """
    This script exports the whole library (or only a collection if specified)
    in Zotero Standalone to a BibTeX .bib file using the Better BibTeX format.
    
    Note: As it is time consuming to pull items from the Zotero Web API
    (either with HTTP request or with the help of the "pyzotero" library),
    and it is also tough (yet possible) to read from the local "zotero.sqlite"
    [see, http://www.texmacs.org/tmweb/miguel/task-zotero.en.html
          https://github.com/smathot/qnotero/blob/master/libzotero/libzotero.py]
    I decided to use the Zotero localhost utility along with Better BibTeX.
    """
    
    # Export the whole Zotero library to BibTeX using Better BibTeX
    URL = "http://localhost:23119/better-bibtex/library?library.bibtex"
    # URL = "http://localhost:23119/better-bibtex/collection?/0/6FRGZRRU.biblatex"
    # URL = "http://localhost:23119/better-bibtex/collection?/0/QBN8FDDA.bibtex"  # for only one collection
    
    new_bib = bibutils.read_zotero_localhost_bib(URL)
    bibutils.fix_and_split(new_bib, omit_indecent_citekey=True)
    bibutils.format_output(new_bib, excluded_fields=EXCLUDED_FIELDS)
    bibutils.write_bib_file(new_bib, outfile)


def request_to_zotero_web_api(limit, start):
    import requests
    # URL = 'https://api.zotero.org/users/1123907/items?format=bibtex&v=3&key=E2DDvV8ONTGhpSBsL3S2YCPs'
    base_URL     = 'https://api.zotero.org'
    library_type = 'user'
    library_id   = '1123907'
    api_key      = 'E2DDvV8ONTGhpSBsL3S2YCPs'
    
    http_header = {'Zotero-API-Version': 3,
                   'Authorization'     : 'Bearer %s' % api_key}
    
    prefix = '/%ss/%s/items' % (library_type, library_id)
    params = '?format=bibtex&sort=dateAdded&direction=asc&limit=%d&start=%d' % (limit, start)
    URL = base_URL + prefix + params
    
    try:
        req = requests.get(URL, headers=http_header)
        if req.status_code == 200:
            # print("Successfull request")
            pass
        else:
            print("Request failed (%d): %s" % (req.status_code, req.content))
    except requests.ConnectionError:
        print("Connection failed!")
        exit()
    
    # print(req.content)
    # print(len(req.content))
    string_data = req.content
    return string_data


if __name__ == '__main__':
    startTime = time.time()
    main()
    print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
