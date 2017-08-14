#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re


def format_output(list_of_dicts, excluded_fields=[], keep_both_doi_url=False):
    """Create and format the data to be written out to a new .bib file
    """
    OUTPUT_ORDER = ['title',
                    'author',
                    'journal',
                    'booktitle',
                    'type',
                    'edition',
                    'editor',
                    'series',
                    'year',
                    'month',
                    'volume',
                    'number',
                    'pages',
                    'publisher',
                    'address',
                    'institution',
                    'location',
                    'isbn',
                    'doi',
                    'url',
                    'abstract',
                    'file',
                    'note']
    
    for item in list_of_dicts:
        item['outdata'] = []
        item['outdata'].append("@%s{%s," % (item['type'], item['id']))
        #--------------------------------------------------------------------
        # Patch the field "number" in @incollection of Springer to "volume":
        if (item['type'] == "incollection" or item['type'] == "book") and \
           'publisher' in item['data'].keys() and any(p in item['data']['publisher'] for p in ["Springer", "Verlag"]) and \
           'series' in item['data'].keys() and 'number' in item['data'].keys() and 'volume' not in item['data'].keys():
            item['data']['volume'] = item['data'].pop('number')
        
        # Patch the field "publisher" and "address", mostly for Springer:
        if 'publisher' in item['data'].keys():
            if item['data']['publisher'].strip('{}') in ["Springer Berlin Heidelberg", "Springer Berlin / Heidelberg", "Springer, Berlin, Heidelberg"]:
                item['data']['publisher'] = "{Springer-Verlag}"
                item['data']['address'] = "Berlin, Heidelberg"
            elif "Physica-Verlag H" in item['data']['publisher']:
                item['data']['publisher'] = "{Physica-Verlag}"
                item['data']['address'] = "Heidelberg"
            elif "Springer International Publishing" in item['data']['publisher']:
                item['data']['publisher'] = "{Springer International Publishing}"
                item['data']['address'] = "Switzerland"
        
        # Attempt to extract DOI from the URL if available
        if 'url' in item['data'].keys():
            if 'doi' not in item['data'].keys() and any(p in item['data']['url'] for p in ["doi", "springer", "wiley"]):
                m = re.match(r'.*/(10\.\d{4}/.+?)(/summary|/abstract)?$', item['data']['url'])
                if m: item['data']['doi'] = m.group(1)
        
        # Add "publisher" of "IEEE" to conference papers with DOI of 10.1109/...
        if item['type'] == "inproceedings" and 'doi' in item['data'].keys() and item['data']['doi'].startswith("10.1109/"):
            if 'publisher' not in item['data'].keys():
                item['data']['publisher'] = "{IEEE}"
        #--------------------------------------------------------------------
        available_fields = item['data'].keys()
        for field in OUTPUT_ORDER:
            if not available_fields: break
            if field in available_fields:
                if field in excluded_fields: continue
                elif field == 'isbn':  # Allow ISBN only for @book without a DOI
                    if item['type'] != "book": continue
                    elif 'doi' in item['data'].keys() and item['data']['doi']: continue
                if field == 'url' and 'doi' in item['data'].keys():  # omit URL if not specified or the URL is just a DOI link
                    if not keep_both_doi_url or\
                       item['data']['doi'] in item['data']['url'] or\
                       any(s in item['data']['url'] for s in ["sciencedirect.com", "linkinghub.elsevier.com", "link.springer.com", "springerlink.com", "ieeexplore"]):
                        continue
                item['outdata'].append("  %s = {%s}," % (field, item['data'][field]))
                available_fields.remove(field)
        if available_fields:
            for field in available_fields:
                if field in excluded_fields: continue
                elif field == 'isbn':  # Allow ISBN only for @book without a DOI
                    if item['type'] != "book": continue
                    elif 'doi' in item['data'].keys() and item['data']['doi']: continue
                if field == 'url' and 'doi' in item['data'].keys():
                    if not keep_both_doi_url or\
                       item['data']['doi'] in item['data']['url'] or\
                       any(s in item['data']['url'] for s in ["sciencedirect.com", "linkinghub.elsevier.com", "link.springer.com", "springerlink.com", "ieeexplore"]):
                        continue
                item['outdata'].append("  %s = {%s}," % (field, item['data'][field]))
        
        item['outdata'][-1] = item['outdata'][-1][:-1]  # remove comma seperator for the last record
        item['outdata'].append("}")


def write_bib_file(list_of_bibs, outfile):
    """Write the extracted bib data to file
    """
    import os
    if not outfile.endswith('.bib'):
        outfile = outfile + '.bib'
    parent_dir = os.path.dirname(os.path.abspath(outfile))
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir)
    with open(outfile, 'wb') as f:
        for record in list_of_bibs:
            # f.write(os.linesep)
            f.write('\n')
            f.write('\n'.join(record['outdata']))
            f.write('\n')
    
    print("%s nicely formatted entries written to '%s'" % (len(list_of_bibs), outfile))
