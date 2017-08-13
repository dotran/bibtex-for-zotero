#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def check_duplicate_citekeys(list_of_dicts):
    list_of_citekeys = [item['id'] for item in list_of_dicts]
    if len(set(list_of_citekeys)) == len(list_of_citekeys):
        print("No duplicate citation key detected.")
    else:
        print("There are duplicate citation keys:")
        for citekey in set(list_of_citekeys):
            if list_of_citekeys.count(citekey) > 1:
                print("'%s'" % citekey, "occurs", list_of_citekeys.count(citekey), "times")
