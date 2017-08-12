#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re


def read_bib_file(bibfile):
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
    
    return cut_into_list_of_dicts(buf)


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
