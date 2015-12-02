#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
import time
import csv
import re
import copy
import pprint
from pyzotero import zotero
import requests
import format_bib


# EXCLUDED_FIELDS = ('note', 'isbn', 'abstract', 'keywords', 'month', 'shorttitle', 'issn', 'copyright', 'file', 'timestamp', 'language', 'urldate')
EXCLUDED_FIELDS = ('note', 'isbn', 'keywords', 'shorttitle', 'issn', 'copyright', 'timestamp', 'language', 'urldate')

outfile  = "E:/RES/Lib/Bib/zbiball.bib"
# outfile = "./biblio.bib"

def main():
    """
    """
    
    # Export the whole Zotero library to BibTeX using Better BibTeX
    URL = "http://localhost:23119/better-bibtex/library?library.bibtex"
    # URL = "http://localhost:23119/better-bibtex/collection?/0/QBN8FDDA.bibtex"  # for only one collection
    try:
        req = requests.get(URL)
    except requests.ConnectionError:
        print("Connection Error: Be sure you have Zotero Standalone running!")
        exit()
    
    new_bib = process_zotero_localhost_bib(req.content)
    fix_and_split_bib_database(new_bib)
    format_output_data(new_bib)
    
    # Write the extracted bib data to file
    with open(outfile, 'wb') as f:
        for record in new_bib:
            # f.write(os.linesep)
            f.write('\n')
            f.write('\n'.join(record['outdata']))
            f.write('\n')
    print("%s nicely formatted entries written to '%s'" % (len(new_bib), outfile))
    
    # Use BibTeX2HTML to generate a .html from the produced .bib file
    os.environ['TEMP'] = '.'
    os.system("bibtex2html.exe -s plain_boldtitle -m bibtex2html_macros.tex -both -use-keys -nf file PDF -d -r %s" % (outfile))
    
    # Copy the generated .html files to the same folder of 'outfile'
    bib_file = os.path.basename(outfile)
    html_file = bib_file[:-4] + ".html"
    html_abstracts_file = bib_file[:-4] + "_abstracts.html"
    html_bib_file = bib_file[:-4] + "_bib.html"
    if os.path.dirname(outfile) != '.':
        for f in [html_file, html_abstracts_file, html_bib_file]:
            shutil.copyfile(f, os.path.join(os.path.dirname(outfile), f))
            os.remove(f)
    
    # Customize the .html files
    os.chdir(os.path.dirname(outfile))
    for html in [html_file, html_abstracts_file, html_bib_file]:
        format_bib_html(html)
    
    # Format the generated .bib file to remove the fields file, abstract
    format_bib.main(infile=outfile, outfile=outfile)
    

def format_bib_html(html_file):
    f = open(html_file, 'rb')
    new_content = []
    for line in f.readlines():
        line = line.splitlines()[0]  # removes \r\n and takes the string
        
        # if line == "<table>":
        #     line = '<table cellpadding="2">'
        
        if re.match(r'<title>.*</title>', line):
            new_content.append(r"""<style type="text/css">
<!--
td {font-family: Verdana; font-size: 10pt; padding-bottom: 6px}
td:first-child {padding-top: 3px; padding-right: 4px; color:DarkRed; font-family: Verdana; font-size: 8pt}
blockquote {
    margin-top: 5px;
    margin-bottom: 10px;
    margin-left: 25px;
    margin-right: 50px;
    font-family: Calibri;
    font-size: 10.5pt;
}
/* unvisited link */
a:link {
    text-decoration: none;
    color: blue;
}
/* visited link */
a:visited {
    /* color: CadetBlue; */
    color: green;
}
/* mouse over link */
a:hover {
    text-decoration: none;
    /* color: red; */
}
--->
</style>""")
            if html_file.endswith("_bib.html"):
                line = "<title>Bibs</title>"
            elif html_file.endswith("_abstracts.html"):
                line = "<title>Abstracts</title>"
            else:
                line = "<title>All Refs</title>"
        
        elif html_file.endswith("_bib.html") and '.bib</h1>' in line:
            m = re.match(r'<h1>.*\.bib</h1>(.*)', line)
            if m: line = m.groups()[0]
        
        elif re.search(r'\A\s<b>', line):
            line = line.replace(' <b>', ' <font color="DarkMagenta">')
            if re.search(r'</b>\.?\Z', line):
                line = line.replace('</b>', '</font>')
        
        elif re.search(r'</b>\.?\Z', line):
            line = line.replace('</b>', '</font>')
        
        elif '>DOI<' in line:
            line = line.replace(">DOI<", ">doi<")
        
        elif '>Abstract<' in line:
            line = line.replace(">Abstract<", ">abstract<")
        
        elif '<blockquote><font size="-1">' in line:
            line = line.replace('<blockquote><font size="-1">', '<blockquote>')
        
        elif '</font></blockquote>' in line:
            line = line.replace('</font></blockquote>', '</blockquote>')
        
        elif not html_file.endswith("_bib.html") and '>http<' not in line and '>PDF<' not in line:
            m = re.search(r'(.*\d+)(--|-)(\d+.*)', line)
            if m: line = m.groups()[0] + '&ndash;' + m.groups()[2]
        elif not html_file.endswith("_bib.html") and '>http<' not in line and '>PDF<' not in line:
            m = re.search(r'(.*[a-zA-Z]\d+)(--|-)([a-zA-Z]\d+\,.*)', line)
            if m: line = m.groups()[0] + '&ndash;' + m.groups()[2]
        
        elif html_file.endswith("_bib.html") and ('file = {' in line or 'abstract = {' in line):
            if "}" in line and "}," not in line:
                new_content[-1] = new_content[-1].replace("},", "}")
            continue
        
        if line.startswith("</table><hr>"):
            line = "</table>"
        elif line.startswith("<hr><p><em>This file was generated by"):
            continue
        elif line.startswith('<a href="http://www.lri.fr/~filliatr/bibtex2html/">bibtex2html</a>'):
            continue
        
        new_content.append(line)
    f.close()
    
    with open(html_file, 'wb') as f:
        f.write('\n'.join(new_content))
        # f.write(os.linesep.join(new_content))
    

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
                if field == 'pages' and '--' in value:
                    m = re.search(r'(.*\d+)(\s*--\s*)([a-zA-Z]?\d+.*)', value)
                    if m: value = m.groups()[0] + '--' + m.groups()[2]
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
