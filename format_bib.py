#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import time
import csv
import re
import copy
import pprint


EXCLUDED_FIELDS = ('note', 'isbn', 'abstract', 'keywords', 'month', 'shorttitle', 'issn', 'copyright', 'file', 'timestamp', 'language', 'urldate')

infile  = "E:\\RES\\Lib\\Bib\\zbiball.bib"
outfile = "E:\\RES\\Lib\\Bib\\zbiball.bib"

def main(infile=infile, outfile=outfile):
    """
    This script is to read a .bib file and re-format it
    in order to create a cleaner and nicer ordering version.
    You need to only specify the 'infile' and 'outfile'.
    """
    bib_data = read_bib_database(infile)
    fix_and_split_bib_database(bib_data)
    format_output_data(bib_data)
    
    # Write the extracted bib data to file
    with open(outfile, 'wb') as f:
        for record in bib_data:
            # f.write(os.linesep)
            f.write('\n')
            f.write('\n'.join(record['outdata']))
            f.write('\n')
    print("%s nicely formatted entries written to '%s'" % (len(bib_data), outfile))
    

def fix_and_split_bib_database(list_of_dicts):
    """list_of_dicts is a list of dictionaries, each dictionary has:
        {'id': "citekey"
         'raw': ["line", "line", ...]
         'type': "article"
         'data': {'author': "", 'journal': "", ...}
         'outdata': ["nice line", "nice line", ...]
        }
    """
    for item in list_of_dicts:
        rawdata = item['raw']
        buf = []
        # Lowercase the entry type
        idx = rawdata[0].index('{')
        item['type'] = rawdata[0][1:idx].lower()
        item['type'] = item['type']
        buf.append('@' + item['type'] + rawdata[0][idx:])
        
        # Lowercase the field name and join broken lines
        for line in rawdata[1:-1]:
            line = line.strip()
            match = re.search(r'\A([a-zA-Z]+)+\s?=\s?(\{.*|[a-zA-Z]+\,|[0-9]+\,)', line)
            if match:
                fixed_line = match.groups()[0].lower() + " = " + match.groups()[1]
                buf.append(fixed_line)
            else:
                buf[-1] = buf[-1] + " " + line  # join broken lines
        
        buf.append(rawdata[-1])  # the closing brace of a bib entry
        # item['raw'] = buf
        """
        # Remove unimportant fields
        patt = r'\A([a-zA-Z]+)+ = (\{.*\}|[a-zA-Z]+|[0-9]+)\,?'
        # item['raw'] = [line for line in buf if (not re.search(patt, line)) or
        #                                             (re.search(patt, line) and re.search(patt, line).groups()[0] not in EXCLUDED_FIELDS)]
        item['raw'] = filter(lambda line: (not re.search(patt, line)) or
                                               (re.search(patt, line) and re.search(patt, line).groups()[0] not in EXCLUDED_FIELDS),
                                  buf)
        
        # Remove the comma ',' at the end of the last field
        if item['raw'][-2].endswith(','):
            item['raw'][-2] = item['raw'][-2][:-1]
        """
        
        # Extract bib fields into dictionaries
        item['data'] = {}
        for line in buf[1:-1]:
            match = re.search(r'\A([a-z]+) = (.*)', line)
            if match:
                field = match.groups()[0]
                value = match.groups()[1].rstrip(',')
                if value.startswith('{') and value.endswith('}'):
                    value = value[1:-1]
                    # Ensure we WERE not trimming braces in "{ABC} is not {DEF}"
                    if all(b in value for b in ['}', '{']) and value.index('}') < value.index('{'):
                        value = '{' + value + '}'
                # TODO: if you want to fix format for some fields, do it here
                if field == 'pages' and '--' in value:
                    m = re.search(r'(.*\d+)(\s*--\s*)([a-zA-Z]?\d+.*)', value)
                    if m: value = m.groups()[0] + '--' + m.groups()[2]
                if field == 'year' and len(value) != 4:
                    m = re.search(r'[1|2]\d{3}', value)
                    if m: value = m.group()
                item['data'][field] = value
            else:
                print("The following line cannot be extracted by the rule 'field = value':")
                print(line)
    
        
def format_output_data(list_of_dicts):
    """Create and format the data to be written out to a new .bib file
    """
    OUTPUT_ORDER = ['author',
                    'title',
                    'journal',
                    'booktitle',
                    'type',
                    'edition',
                    'series',
                    'editor',
                    'year',
                    'volume',
                    'number',
                    'pages',
                    'isbn',
                    'publisher',
                    'address',
                    'institution',
                    'location',
                    'doi',
                    'url',
                    'note']
    
    for item in list_of_dicts:
        item['outdata'] = []
        item['outdata'].append("@%s{%s," % (item['type'], item['id']))
        available_fields = item['data'].keys()
        for field in OUTPUT_ORDER:
            if not available_fields: break
            if field in available_fields:
                if field in EXCLUDED_FIELDS: continue
                item['outdata'].append("  %s = {%s}," % (field, item['data'][field]))
                available_fields.remove(field)
        if available_fields:
            for field in available_fields:
                if field in EXCLUDED_FIELDS: continue
                item['outdata'].append("  %s = {%s}," % (field, item['data'][field]))
        
        item['outdata'][-1] = item['outdata'][-1][:-1]  # remove comma seperator for the last record
        item['outdata'].append("}")
    

def read_bib_database(bibfile):
    """Read a bibliography .bib file into a list of dictionaries,
    each dictionary has 'id' and 'raw' keys, where 'id is the citekey
    and 'raw' contains a list of all *raw* lines of the entry 'id'.
    """
    with open(bibfile, 'rb') as f:
        buf = f.read().split('\n')
    buf = [line[:-1] if line.endswith('\r') else line for line in buf]  # remove '\r' in Windows files
    
    list_of_dicts = []
    for line in buf:
        if line.strip() == '': continue  # ignore empty lines
        if not list_of_dicts and not line.startswith("@"): continue  # ignore header lines, like those from JabRef
        if line.startswith("@"):
            citekey = re.search(r'\{(.*)\,', line).group(1)
            list_of_dicts.append({'id' : citekey.strip(),
                                  'raw': [line]})
        else:
            list_of_dicts[-1]['raw'].append(line)
    return list_of_dicts


if __name__ == '__main__':
    startTime = time.time()
    main()
    # print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
