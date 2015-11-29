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
from pyzotero import zotero
import requests


EXCLUDED_FIELDS = ('note', 'isbn', 'abstract', 'keywords', 'month', 'shorttitle', 'issn', 'copyright', 'file', 'timestamp', 'language', 'urldate')

infile  = "E:\\RES\\Lib\\Bib\\JabRef\\allZotero.bib"
outfile = "./biblio.bib"

def main():
    """
    This script will read your persistent/long-running bib database and then
    pull new entries from your Zotero to create a joint, newer bib file.
    
    You need to specify your existing .bib database as a base bib database
    and specify the output .bib file to store the new database.
    
    Note: As it is time consuming to pull items from the Zotero Web API
    (either with HTTP request or with the help of the "pyzotero" library),
    and it is also tough (yet possible) to read from the local "zotero.sqlite"
    [see, http://www.texmacs.org/tmweb/miguel/task-zotero.en.html
          https://github.com/smathot/qnotero/blob/master/libzotero/libzotero.py]
    I decided to use the Zotero localhost utility along with Better BibTeX.
    """
    
    # Export the whole Zotero library to BibTeX using Better BibTeX
    URL = "http://localhost:23119/better-bibtex/library?library.bibtex"
    # URL = "http://localhost:23119/better-bibtex/collection?/0/QBN8FDDA.bibtex"
    try:
        req = requests.get(URL)
    except requests.ConnectionError:
        print("Connection Error: Be sure your Zotero Standalone is running!")
        exit()
    
    new_bib = process_zotero_localhost_bib(req.content)
    fix_and_split_bib_database(new_bib)
    format_output_data(new_bib)
    
    bib_data = read_bib_database(infile)
    fix_and_split_bib_database(bib_data)
    format_output_data(bib_data)
    
    add_new_entries_to_basebib(basebib=bib_data, newbib=new_bib)
    
    # Write the extracted bib data to file
    with open(outfile, 'wb') as f:
        for record in bib_data:
            # f.write(os.linesep)
            f.write('\n')
            f.write('\n'.join(record['outdata']))
            f.write('\n')
    print("%s nicely formatted entries written to '%s'" % (len(bib_data), outfile))
    
    
    """
    # Using pyzotero library, instead of making direct HTTP request to Zotero Web API
    zot = zotero.Zotero(library_id='1123907',
                        library_type='user',
                        api_key='E2DDvV8ONTGhpSBsL3S2YCPs')
    # zot.add_parameters(format='bibtex', sort='dateAdded', direction='desc', limit=100, start=3000)
    # items = zot.top()
    # print(items[-1000:])
    # pprint.pprint(items[-1]['data'])
    """
    # max_limit = 100
    # i = 0
    # raw_data = ""
    # while i >= 0:
    #     """
    #     # Using pyzotero library, instead of making direct HTTP request to Zotero Web API
    #     zot.add_parameters(format='bibtex', sort='dateAdded', direction='desc', limit=max_limit, start=i*max_limit)
    #     buf = zot.top()
    #     """
    #     buf = request_to_zotero_web_api(limit=max_limit, start=i*max_limit)
    #     raw_data = raw_data + '\n' + buf
    #     print(i)
    #     i = i + 1 if buf else -1
    # # Write to text file
    # with open('zotero_web_api.bib', 'wb') as f:
    #     f.write(raw_data)
    

def request_to_zotero_web_api(limit, start):
    import requests
    # URL = 'https://api.zotero.org/users/1123907/items?format=bibtex&v=3&key=E2DDvV8ONTGhpSBsL3S2YCPs'
    base_URL     = 'https://api.zotero.org'
    library_type = 'user'
    library_id   = '1123907'
    api_key      = 'E2DDvV8ONTGhpSBsL3S2YCPs'
    
    http_header = {'Zotero-API-Version': 3,
                   'Authorization'     : 'Bearer %s' % api_key}
    
    prefix = '/%ss/%s/items' % (library_type, library_id)
    params = '?format=bibtex&sort=dateAdded&direction=asc&limit=%d&start=%d' % (limit, start)
    URL = base_URL + prefix + params
    
    try:
        req = requests.get(URL, headers=http_header)
        if req.status_code == 200:
            # print("Successfull request")
            pass
        else:
            print("Request failed (%d): %s" % (req.status_code, req.content))
    except requests.ConnectionError:
        print("Connection failed!")
        exit()
    
    # print(req.content)
    # print(len(req.content))
    string_data = req.content
    return string_data


def add_new_entries_to_basebib(basebib, newbib):
    all_basebib_citekeys = [item['id'] for item in basebib]
    new_entries = []
    for entry in newbib:
        if entry['id'] not in all_basebib_citekeys:
            new_entries.append(entry)
    basebib += new_entries
    print("%d new entries found and added to the basebib" % len(new_entries))


def process_zotero_localhost_bib(string):
    """Read the bibtex output from Zotero localhost into a list of dictionaries,
    each dictionary has 'id' and 'raw' keys, where 'id is the citekey
    and 'raw' contains a list of all *raw* lines of the entry 'id'.
    """
    buf = []
    for line in string.split('\n'):
        if line.startswith("@comment{"):
            break
        buf.append(line)
    # buf = string.split('\n')
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


def fix_and_split_bib_database(list_of_dicts):
    """list_of_dicts is a list of dictionaries, each dictionary has:
        {'id': "citekey"
         'raw': ["line", "line", ...]
         'type': "article"
         'data': {'author': "", 'journal': "", ...}
         'outdata': ["nice line", "nice line", ...]
        }
    """
    # Omit non-official references (those without a decent citekey)
    for idx, item in reversed(list(enumerate(list_of_dicts))):
        if not re.search(r'[a-z]{2,}', item['id']):
            del list_of_dicts[idx]
    
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
    print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
