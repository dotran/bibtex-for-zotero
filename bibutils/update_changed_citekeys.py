#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
import time
import csv
import re
import copy
import pprint


diff_file   = "E:/RES/Lib/Bib/bibchanges.diff"
tex_infile  = "E:/INRIA/thesis-temp/10-introduction.tex"
tex_outfile = "E:/INRIA/thesis-temp/10-introduction_keysfixed.tex"

def main():
    """Export the whole Zotero library to BibTeX using Better BibTeX
    and use the BibTeX2HTML tool to make nicely formatted HTML files with
    with abstracts, links, etc.
    """
    citekey_changes = read_citekey_changes_from_diff_file(diff_file)
    # pprint.pprint(citekey_changes)
    print(len(citekey_changes))
    with open(tex_infile, 'rb') as f:
        doc = f.read()
    # print(doc[:200])
    print(type(doc))
    print(len(doc))
    
    for key in citekey_changes:
        pattern = r'%s\b' % key['old']
        # print(pattern)
        doc = re.sub(pattern, key['new'], doc)
    
    with open(tex_outfile, 'wb') as f:
        f.write(doc)


def read_citekey_changes_from_diff_file(diffFile):
    with open(diffFile, 'rb') as f:
        buf = f.read().split('\n')
    buf = [line[:-1] if line.endswith('\r') else line for line in buf]  # remove '\r' in Windows files
    
    # old_citekeys = [extract_citekey(line) for line in buf if line.startswith('-@')]
    # new_citekeys = [extract_citekey(line) for line in buf if line.startswith('+@')]
    old_citekeys = []
    new_citekeys = []
    for idx, line in enumerate(buf):
        if line.startswith('-@') and buf[idx+1].startswith('+@'):
            old_citekeys.append(extract_citekey(line))
            new_citekeys.append(extract_citekey(buf[idx+1]))
    
    citekey_changes = []
    for old, new in zip(old_citekeys, new_citekeys):
        citekey_changes.append({'old': old,
                                'new': new})
    return citekey_changes


def extract_citekey(string):
    m = re.search(r'\{(.+)\,', string)
    if m:
        citekey = m.groups()[0]
    else:
        exit("Cannot extract citekey in %s", string)
    return citekey


if __name__ == '__main__':
    startTime = time.time()
    main()
    print('Processing done in %1.2f' % (time.time() - startTime), 'seconds.')
