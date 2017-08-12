#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# from pyzotero import zotero
import requests

from .read_bib_file import cut_into_list_of_dicts


def read_zotero_localhost_bib(url):
    """Export the whole Zotero library to BibTeX using Better BibTeX and then
    read the bibtex output from Zotero localhost into a list of dictionaries,
    each dictionary has 'id' and 'raw' keys, where 'id' is the citekey
    and 'raw' contains a list of all *raw* lines of the entry 'id'.
    """
    try:
        req = requests.get(url)
    except requests.ConnectionError:
        # print("ConnectionError: Be sure you have Zotero Standalone running!", file=sys.stderr)
        # exit()
        exit("ConnectionError: Be sure you have Zotero Standalone running!")
    
    buf = []
    
    for line in req.content.split('\n'):
        if line.startswith("@comment{"):
            break
        buf.append(line)
    # buf = req.content.split('\n')
    buf = [line[:-1] if line.endswith('\r') else line for line in buf]  # remove '\r' in Windows files
    
    return cut_into_list_of_dicts(buf)
