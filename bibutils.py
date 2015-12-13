#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import sys
import os
import shutil
import time
import csv
import re
import copy
import pprint
import requests


# EXCLUDED_FIELDS = ('note', 'isbn', 'abstract', 'keywords', 'month', 'shorttitle', 'issn', 'copyright', 'file', 'timestamp', 'language', 'urldate')
# EXCLUDED_FIELDS = ('note', 'isbn', 'keywords', 'shorttitle', 'issn', 'copyright', 'timestamp', 'language', 'urldate')


def read_bib_file(bibfile):
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


def read_zotero_localhost_bib(url):
    """Export the whole Zotero library to BibTeX using Better BibTeX and then
    read the bibtex output from Zotero localhost into a list of dictionaries,
    each dictionary has 'id' and 'raw' keys, where 'id' is the citekey
    and 'raw' contains a list of all *raw* lines of the entry 'id'.
    """
    try:
        req = requests.get(url)
    except requests.ConnectionError:
        # print("ConnectionError: Be sure you have Zotero Standalone running!", file=sys.stderr)
        # exit()
        exit("ConnectionError: Be sure you have Zotero Standalone running!")
    
    buf = []
    for line in req.content.split('\n'):
        if line.startswith("@comment{"):
            break
        buf.append(line)
    # buf = req.content.split('\n')
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


def check_duplicate_citekeys(list_of_dicts):
    list_of_citekeys = [item['id'] for item in list_of_dicts]
    if len(set(list_of_citekeys)) == len(list_of_citekeys):
        print("Perfect! No duplicate citation key.")
    else:
        print("There are duplicate citation keys:")
        for citekey in set(list_of_citekeys):
            if list_of_citekeys.count(citekey) > 1:
                print("'%s'" % citekey, "occurs", list_of_citekeys.count(citekey), "times")


def fix_and_split(list_of_dicts, omit_indecent_citekey=False):
    """list_of_dicts is a list of dictionaries, each dictionary has:
        {'id': "citekey"
         'raw': ["line", "line", ...]
         'type': "article"
         'data': {'author': "", 'journal': "", ...}
         'outdata': ["nice line", "nice line", ...]
        }
    """
    if omit_indecent_citekey:
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
                if field == 'pages' and '--' in value:
                    m = re.search(r'(.*\d+)(\s*--\s*)([a-zA-Z]?\d+.*)', value)
                    if m: value = m.groups()[0] + '--' + m.groups()[2]
                if field == 'journal' and value == "Evol. Comput.":
                    value = "Evolutionary Computation"
                if field == 'year' and len(value) != 4:
                    m = re.search(r'[1|2]\d{3}', value)
                    if m: value = m.group()
                if field == 'file':
                    m = re.search(r':(.*\.pdf):application', value)
                    if m:
                        value = m.groups()[0]
                        value = "file://" + value.replace('\:\\\\', ':/').replace('\\\\', '/').replace('\\', '/')
                if field == 'month':
                    if value == 'jan':   value = 'January'
                    elif value == 'feb': value = 'February'
                    elif value == 'mar': value = 'March'
                    elif value == 'apr': value = 'April'
                    elif value == 'may': value = 'May'
                    elif value == 'jun': value = 'June'
                    elif value == 'jul': value = 'July'
                    elif value == 'aug': value = 'August'
                    elif value == 'sep': value = 'September'
                    elif value == 'oct': value = 'October'
                    elif value == 'nov': value = 'November'
                    elif value == 'dec': value = 'December'
                if field == 'title':
                    if value and '{' in value:
                        value = format_title_brackets(value)
                if field == 'booktitle':
                    # Drop unnecessary brackets
                    if value and '{' in value:
                        value = value.replace('{\\textendash}', '--').replace('{\\textemdash}', '---')\
                                     .replace('{{', '').replace('}}', '')
                        # value = '{' + value + '}'
                    # Fix things like GECCO '10
                    value = value.replace(" '", "~'")
                if field == 'series':
                    value = value.replace(" '", "~'")
                item['data'][field] = value
            else:
                print("The following line cannot be extracted by the rule 'field = value':")
                print(line)


def format_title_brackets(inpstring):
    buf = inpstring.replace('{\\textendash}', '--').replace('{\\textemdash}', '---')
    # buf = inpstring.replace('{\\textendash}', '--').replace('{\\textemdash}', '---').replace('{\\backslash}', '\\').replace('\\{', '{').replace('\\}', '}')
    string = ''
    m = re.search(r'(.*?)\{\{(.+?)\}\}(.*)', buf)
    while m:
        string += m.groups()[0]
        if m.groups()[1].startswith('\\'):
            string += '{' + m.groups()[1] + '}'
        else:
            string += m.groups()[1]
        buf = m.groups()[2]
        m = re.search(r'(.*?)\{\{(.+?)\}\}(.*)', buf)
    string += buf
    
    # string = " ".join(['{' + w + '}' if re.search(r'[A-Z]{2,}', w) else w for w in string.split()])
    list_of_words = []
    for w in string.split():
        if re.search(r'[A-Z]{2,}', w) or re.search(r'[a-z]+[A-Z]{1,}', w):
            if '-' in w and re.search(r'[a-zA-Z][a-z]{1,}', w):
                # Like NSGA-Based --> {NSGA}-Based instead of {NSGA-Based}
                # or QoS-ware --> {QoS}-aware instead of {QoS-aware}
                word = '-'.join(['{' + g + '}' if re.search(r'[A-Z]{2,}', g) or re.search(r'[a-z]+[A-Z]{1,}', g)
                                               else g for g in w.split('-')])
            else:
                # NSGA-II --> {NSGA-II} or PSO-NSGA-II --> {PSO-NSGA-II}
                if w.endswith(':') or w.endswith(','):
                    word = '{' + w[:-1] + '}' + w[-1]
                else:
                    word = '{' + w + '}'
        else:
            word = w
        list_of_words.append(word)
    string = " ".join(list_of_words)
    
    # Capitalize 'I' in "Part I"
    m = re.search(r'(.+?\s)([B-Z]\b)(.*)', string)
    if m: string = m.groups()[0] + '{' + m.groups()[1] + '}' + m.groups()[2]
    
    # Capitalize after '?' / '.', eg, Aleatory or epistemic? Does it matter? / Cogeneration planning under uncertainty. Part {II}
    m = re.search(r'(.+?[\?\.]\s)([A-Z][a-z]*)(.*)', string)
    if m: string = m.groups()[0] + '{' + m.groups()[1] + '}' + m.groups()[2]
    
    return string


def format_output(list_of_dicts, excluded_fields=[], keep_both_doi_url=False):
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
                    'month',
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
                    'abstract',
                    'file',
                    'note']
    
    for item in list_of_dicts:
        item['outdata'] = []
        item['outdata'].append("@%s{%s," % (item['type'], item['id']))
        available_fields = item['data'].keys()
        for field in OUTPUT_ORDER:
            if not available_fields: break
            if field in available_fields:
                if field in excluded_fields: continue
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
                if field == 'url' and 'doi' in item['data'].keys():
                    if not keep_both_doi_url or\
                       item['data']['doi'] in item['data']['url'] or\
                       any(s in item['data']['url'] for s in ["sciencedirect.com", "linkinghub.elsevier.com", "link.springer.com", "springerlink.com", "ieeexplore"]):
                        continue
                item['outdata'].append("  %s = {%s}," % (field, item['data'][field]))
        
        item['outdata'][-1] = item['outdata'][-1][:-1]  # remove comma seperator for the last record
        item['outdata'].append("}")


def add_new_entries_to_basebib(basebib, newbib):
    all_basebib_citekeys = [item['id'] for item in basebib]
    new_entries = []
    for entry in newbib:
        if entry['id'] not in all_basebib_citekeys:
            new_entries.append(entry)
    basebib += new_entries
    print("%d new entries found and added to the basebib" % len(new_entries))


def write_bib_file(list_of_bibs, outfile):
    """Write the extracted bib data to file
    """
    with open(outfile, 'wb') as f:
        for record in list_of_bibs:
            # f.write(os.linesep)
            f.write('\n')
            f.write('\n'.join(record['outdata']))
            f.write('\n')
    print("%s nicely formatted entries written to '%s'" % (len(list_of_bibs), outfile))
