#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def add_new_entries_to_basebib(base_bib, new_bib):
    basebib_citekeys = [item['id'] for item in base_bib]
    new_entries = []
    
    for entry in new_bib:
        if entry['id'] not in basebib_citekeys:
            new_entries.append(entry)
    
    base_bib += new_entries
    
    if new_entries:
        print("%d new entries found and added to the base bib." % len(new_entries))
    else:
        print("No new entries found. Nothing to add to the base bib.")
