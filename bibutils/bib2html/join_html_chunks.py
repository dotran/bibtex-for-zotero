#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os


def join_html_chunks(html_files, nb_chunks):
    for key, file in html_files.items():
        join_chunks(key, file, nb_chunks)


def join_chunks(key, file, nb_chunks):
    f = open(file % '', 'wb')
    
    for i in range(nb_chunks):
        tag = 'table' if key in ['ref', 'abs'] else 'body'
        f_i = open(file % str(i), 'rb')
        
        # First part
        if i == 0:
            for line in f_i.readlines():
                if line.splitlines()[0] != "</%s>" % tag:
                    f.write(line)
                else:
                    f.write('\n')
                    break
        
        # Last part
        elif i == nb_chunks - 1:
            WRITING = False
            for line in f_i.readlines():
                if not WRITING and line.splitlines()[0] == "<%s>" % tag:
                    WRITING = True
                    continue
                if WRITING:
                    f.write(line)
        
        # Middle parts
        else:
            WRITING = False
            for line in f_i.readlines():
                if not WRITING and line.splitlines()[0] == "<%s>" % tag:
                    WRITING = True
                    continue
                if WRITING:
                    if line.splitlines()[0] == "</%s>" % tag:
                        f.write('\n')
                        break
                    f.write(line)
        
        f_i.close()
        os.remove(file % str(i))  # remove the partial file that have been read
    
    f.close()
