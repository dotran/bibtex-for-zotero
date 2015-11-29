#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import time
import csv
import re
import copy
import pprint


EXTRACT_ON_BIB_FILE_BASIC = False  # set to False to extract using the order as in
                                   # the .bbl file (the order of \bibcite's in .aux)
EXCLUDED_FIELDS = ('note', 'isbn', 'abstract', 'keywords', 'month', 'shorttitle', 'issn', 'copyright', 'file', 'timestamp', 'language', 'urldate')
# EXCLUDED_FIELDS = ('abstract', 'keywords', 'month', 'shorttitle', 'issn', 'copyright', 'file', 'timestamp', 'language', 'urldate')  # for CV only

def main():
    """
    Note: this script must be located under the folder of your latex paper.
    
    This script is to generate a specific .bib database for references cited
    (and successfully rendered) in a latex paper. The script will look into
    references at the \\bibcite{} in the .aux file (which is created after you
    compile your latex paper) and then pull them out from the .bib file(s)
    that you used with your paper (the .bib files are indicated by at the
    \\bibdata{} command in the .aux file).
    
    The collective references will be written to a .bib file under the same
    folder of your latex paper with the same name as your main .tex file
    (which is also the name of the .aux file).
    
    It is possible to have multiple .aux files in a latex folder. If so, the
    collective references are written to output "extract_bib.bib" file.
    """
    
    # Get all .aux files from the current folder
    aux_sources = []
    for f in os.listdir('.'):
        if f.endswith('.aux'):
            aux_sources.append(f)
    # print(aux_sources)
    
    # Get all .bib databases and rendered references from each .aux file
    extracted_data = []
    for aux_file in aux_sources:
        print("Processing references in '%s'" % aux_file)
        all_bib_files = []
        all_citekeys  = []
        with open(aux_file) as f:
            for line in f.readlines():
                line = line.splitlines()[0]  # removes \r\n and takes the string
                
                # Get all .bib databases
                if line.startswith("\\bibdata{"):
                    bibs = re.search(r'\{(.*)\}', line).group(1)
                    all_bib_files += [name + ".bib" for name in bibs.split(',')]
                
                # Get all rendered references
                if line.startswith("\\bibcite{"):
                    key = re.search(r'\{(.*?)\}', line).group(1)
                    all_citekeys.append({'id' : key,
                                         'extracted': False})
        print("  - There are %d citation keys in '%s'" % (len(all_citekeys), aux_file))
        
        if EXTRACT_ON_BIB_FILE_BASIC:
            # Go to each .bib database to retrieve data
            for bib_file in all_bib_files:
                bib_data = read_bib_database(bib_file)
                fix_and_split_bib_database(bib_data)
                format_output_data(bib_data)
                # pprint.pprint(bib_data)
                # exit()
                keybase = [d['id'] for d in bib_data]
                for key in all_citekeys:
                    if not key['extracted']:
                        if key['id'] in keybase:
                            idx = keybase.index(key['id'])
                            extracted_data.append(bib_data[idx]['outdata'])
                            key['extracted'] = True
        else:
            # Concatenate all bib_data before extracting,
            # to help keep the ordering as in all_citekeys
            all_bib_data = []
            # Go to each .bib database to retrieve data
            for bib_file in all_bib_files:
                bib_data = read_bib_database(bib_file)
                fix_and_split_bib_database(bib_data)
                format_output_data(bib_data)
                all_bib_data += bib_data
            keybase = [d['id'] for d in all_bib_data]
            for key in all_citekeys:
                if not key['extracted']:
                    if key['id'] in keybase:
                        idx = keybase.index(key['id'])
                        extracted_data.append(all_bib_data[idx]['outdata'])
                        key['extracted'] = True
        
        print("  - Found %d citation keys in the bib databases" % len([k for k in all_citekeys if k['extracted']]))
        unresolved_keys = [k['id'] for k in all_citekeys if not k['extracted']]
        if unresolved_keys:
            print("  - Cannot resolved %d citation keys" % len(unresolved_keys))
            print("    Unresolved keys are written to 'unresolved_keys.txt'")
            with open("unresolved_keys.txt", 'wb') as f:
                f.write('\n'.join(unresolved_keys))
            if len(unresolved_keys) < 10:
                [print(k) for k in unresolved_keys]
            else:
                [print(k) for k in unresolved_keys[:10]]
                print("...")
        else:
            print("  - Successfully collected references for all citation keys")
    
    
    # Write the extracted bib data to file
    if len(aux_sources) == 1:
        outfile = aux_sources[0].replace('.aux', '.bib')
    else:
        outfile = "extract_bib.bib"
    
    with open(outfile, 'wb') as f:
        for item in extracted_data:
            # f.write(os.linesep)
            f.write('\n')
            f.write('\n'.join(item))
            f.write('\n')
    print("\nExtracted bibliography written to '%s'" % outfile)
    

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
