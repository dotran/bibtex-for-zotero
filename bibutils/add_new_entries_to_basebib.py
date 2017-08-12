#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def add_new_entries_to_basebib(basebib, newbib):
    all_basebib_citekeys = [item['id'] for item in basebib]
    new_entries = []
    
    for entry in newbib:
        if entry['id'] not in all_basebib_citekeys:
            new_entries.append(entry)
    
    basebib += new_entries
    
    if new_entries:
        print("%d new entries found and added to the basebib." % len(new_entries))
    else:
        print("No new entries found.")
