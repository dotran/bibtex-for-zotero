#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os

from .compile_bib_to_html import compile_bib_to_html
from .join_html_chunks import join_html_chunks


BIBTEX_MAX_CAPACITY = 15  # 7000


def bib_to_html(bib, path=None, filename=None):
    nb_batches, remainder = divmod(len(bib), BIBTEX_MAX_CAPACITY)
    
    # Backup the existing bib file
    cur_bib_file = os.path.join(path, filename.replace('.html', '.bib'))
    bak_bib_file = backup_restore_file(cur_bib_file, 'backup')
    
    # Process each single batch
    for i in range(nb_batches):
        sta_idx = i * BIBTEX_MAX_CAPACITY
        end_idx = sta_idx + BIBTEX_MAX_CAPACITY
        chunk_idx = i if len(bib) / BIBTEX_MAX_CAPACITY > 1 else ''
        html_files = compile_bib_to_html(bib[sta_idx:end_idx], chunk_idx, path, filename)
    
    # Process the remaining entries that did not constitute a whole batch
    if remainder:
        sta_idx = nb_batches * BIBTEX_MAX_CAPACITY
        end_idx = len(bib) + 1
        chunk_idx = nb_batches if len(bib) > BIBTEX_MAX_CAPACITY else ''
        html_files = compile_bib_to_html(bib[sta_idx:end_idx], chunk_idx, path, filename)
    
    # Join the separate HTLM files if they have multiple parts
    if len(bib) / BIBTEX_MAX_CAPACITY > 1:
        nb_chunks = nb_batches + 1 if remainder else nb_batches
        join_html_chunks(html_files, nb_chunks)
    
    # Restore the backed up bib file
    backup_restore_file(bak_bib_file, 'restore')


def backup_restore_file(file, mode):
    import os
    import shutil
    BACKUP_EXT = ".backup"
    if mode == "backup":
        if not os.path.isfile(file):
            print("%s does not exist. No need to backup.")
            return None
        else:
            backup_file = file + BACKUP_EXT
            print("Backing up '%s'" % file)
            shutil.copyfile(file, backup_file)
            # os.remove(file)
            return backup_file
    elif mode == "restore":
        if not file or not os.path.isfile(file):
            print("No file to restore.")
        else:
            original_file = file.replace(BACKUP_EXT, '')
            print("Restoring '%s'" % original_file)
            shutil.copyfile(file, original_file)
            os.remove(file)
    else:
        raise Exception("Unknown 'mode'.")
