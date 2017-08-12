#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from .compile_bib_to_html import compile_bib_to_html
from .join_html_chunks import join_html_chunks


BIBTEX_MAX_CAPACITY = 15  # 7000


def bib_to_html(bib, path=None, filename=None):
    nb_batches, remainder = divmod(len(bib), BIBTEX_MAX_CAPACITY)
    
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
