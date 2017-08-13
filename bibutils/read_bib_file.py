#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re

from .parse_bib import parse_bib


def read_bib_file(bibfile, omit_indecent_citekey=False, verbose=False):
    """
    Read a bibliography .bib file into a list of dictionaries
    
    OUTPUT:
        a list of dictionaries, in which
            {'id' :  citekey,
             'raw': a list of all *raw* lines of the entry identified by 'id'}
    """
    
    with open(bibfile, 'rb') as f:
        buf = f.read().split('\n')
    buf = [line[:-1] if line.endswith('\r') else line for line in buf]  # remove '\r' in Windows files
    
    list_of_dicts = cut_into_list_of_dicts(buf)
    
    if omit_indecent_citekey:
        eliminate_indecent_citekeys(list_of_dicts, verbose)
    
    parse_bib(list_of_dicts)
    
    return list_of_dicts


def eliminate_indecent_citekeys(list_of_dicts, verbose):
    """Omit non-official references (those without a decent citekey)
    """
    for idx, item in reversed(list(enumerate(list_of_dicts))):
        citekey = item['id']
        if not re.search(r'[a-z]{2,}', citekey):
            notify_omitting(verbose, citekey)
            del list_of_dicts[idx]
        
        #elif item['type'] == 'misc' and re.search(r'\+[a-z]{2,}', citekey):
        elif re.search(r'\+[a-z]{2,}', citekey):
            notify_omitting(verbose, citekey)
            del list_of_dicts[idx]
        
        elif 'zotero-null' in citekey:
            notify_omitting(verbose, citekey)
            del list_of_dicts[idx]


def notify_omitting(verbose, citekey):
    if verbose:
        print("Omitting the entry with citekey '%s'" % citekey)


def cut_into_list_of_dicts(buf):
    list_of_dicts = []
    
    for line in buf:
        if line.strip() == '':
            continue  # ignore empty lines
        if not list_of_dicts and not line.startswith("@"):
            continue  # ignore header lines, like those from JabRef
        
        if line.startswith("@"):
            citekey = re.search(r'\{(.*)\,', line).group(1)
            list_of_dicts.append({'id' : citekey.strip(),
                                  'raw': [line]})
        else:
            list_of_dicts[-1]['raw'].append(line)
    
    return list_of_dicts
