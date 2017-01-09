#!/usr/bin/env python2
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
# from pyzotero import zotero
import bibutils


#EXCLUDED_FIELDS = ('dateadded', 'note', 'isbn', 'keywords', 'shorttitle', 'issn', 'copyright', 'timestamp', 'language', 'urldate', 'lccn', 'pmid', 'pmcid')
EXCLUDED_FIELDS = ('dateadded', 'note',         'keywords', 'shorttitle', 'issn', 'copyright', 'timestamp', 'language', 'urldate', 'lccn', 'pmid', 'pmcid')

outfile  = "E:/Library/Biblio/liball33.bib"
# outfile = "./biblio.bib"

BIBTEX_MAX_CAPACITY = 7000

def main():
    """
    Export the whole Zotero library to BibTeX using Better BibTeX
    and use the BibTeX2HTML tool to make nicely formatted HTML files with
    with abstracts, links, etc.
    
    NOTE: This is the UPDATED VERSION which splits the large bib database
    (exceeding the Hash size of 35000) into smaller junks.
    
    UPDATE: To sort the .bib wrt "Date Added", we must have access to this field,
    which is not available by default in the Zotero Better BibTeX translator.
    Thus we need to add this field to the output by using an API of Better BibTeX
    which allows accessing the reference just before it is written out and cached.
    This can be achieved by adding the a JavaScript snippet to the Postscript box
    in the Advanced tab of the Better BibTeX preferences:
    
    if (Translator.BetterBibTeX) {
        if (this.item.dateAdded) {
            this.add({ name: 'dateadded', value: this.item.dateAdded });
        }
    }
    
    We can use this method to add any Zotero field to the Better BibTeX .bib output.
    Ref: https://github.com/retorquere/zotero-better-bibtex/wiki/Scripting
    """
    
    URL = "http://localhost:23119/better-bibtex/library?library.bibtex"
    # URL = "http://localhost:23119/better-bibtex/collection?/0/QBN8FDDA.bibtex"  # for only one collection
    # URL = "http://localhost:23119/better-bibtex/collection?/0/--GPU.bibtex"
    
    
    # Step 1: Export Zotero library/collection to a .bib file
    new_bib = bibutils.read_zotero_localhost_bib(URL)
    bibutils.fix_and_split(new_bib, omit_indecent_citekey=True)
    new_bib = sorted(new_bib, key=lambda k: k['data']['dateadded'], reverse=False)  # sort by "Date Added"
    bibutils.format_output(new_bib, excluded_fields=EXCLUDED_FIELDS, keep_both_doi_url=True)
    # bibutils.write_bib_file(new_bib, outfile)
    
    
    # Sort the database wrt 'year' for the HTML outputs
    new_bib_sorted = sorted(new_bib,
                            key=lambda k: k['data']['year'] if 'year' in k['data'].keys() else 0,
                            reverse=True)
    
    # Set filename templates
    bib_file = os.path.basename(outfile)
    html_file = bib_file[:-4] + "%s.html"
    html_abstracts_file = bib_file[:-4] + "%s_abstracts.html"
    html_bib_file = bib_file[:-4] + "%s_bib.html"
    
    
    number_of_batches, remainder = divmod(len(new_bib_sorted), BIBTEX_MAX_CAPACITY)
    
    # Process each single batch
    for i in xrange(number_of_batches):
        bibutils.write_bib_file(new_bib_sorted[i*BIBTEX_MAX_CAPACITY : (i+1)*BIBTEX_MAX_CAPACITY], outfile)
        
        # Step 2: Use BibTeX2HTML to generate a .html from the produced .bib file
        os.environ['TEMP'] = '.'
        os.system("bibtex2html.exe -s plain_boldtitle -m bibtex2html_macros.tex -both -use-keys -nf file PDF -d -r %s" % (outfile))
        
        # Step 3: Customize the .html files
        for html in [html_file, html_abstracts_file, html_bib_file]:
            format_bib_html(html % '')
        
        # Step 4: Copy the generated .html files to the same folder of 'outfile'
        if os.path.dirname(outfile) != '.':
            for f in [html_file, html_abstracts_file, html_bib_file]:
                shutil.copyfile(f % '', os.path.join(os.path.dirname(outfile), f % str(i if remainder or number_of_batches >= 2 else '')))
                os.remove(f % '')
    
    # Process the remaining entries that did not constitute a whole batch
    if remainder:
        bibutils.write_bib_file(new_bib_sorted[number_of_batches*BIBTEX_MAX_CAPACITY : ], outfile)
        
        # Step 2: Use BibTeX2HTML to generate a .html from the produced .bib file
        os.environ['TEMP'] = '.'
        os.system("bibtex2html.exe -s plain_boldtitle -m bibtex2html_macros.tex -both -use-keys -nf file PDF -d -r %s" % (outfile))
        
        # Step 3: Customize the .html files
        for html in [html_file, html_abstracts_file, html_bib_file]:
            format_bib_html(html % '')
        
        # Step 4: Copy the generated .html files to the same folder of 'outfile'
        if os.path.dirname(outfile) != '.':
            for f in [html_file, html_abstracts_file, html_bib_file]:
                shutil.copyfile(f % '', os.path.join(os.path.dirname(outfile), f % str(number_of_batches if number_of_batches >= 1 else '')))
                os.remove(f % '')
    
    # Join the separate HTLM files if they have multiple parts
    os.chdir(os.path.dirname(outfile))
    if number_of_batches >= 2 or (number_of_batches == 1 and remainder):
        number_of_files = number_of_batches + 1 if remainder else number_of_batches
        f1 = open(html_file % '', 'wb')
        f2 = open(html_abstracts_file % '', 'wb')
        f3 = open(html_bib_file % '', 'wb')
        for i in xrange(number_of_files):
            f1_i = open(html_file % str(i), 'rb')
            f2_i = open(html_abstracts_file % str(i), 'rb')
            f3_i = open(html_bib_file % str(i), 'rb')
            
            # First part
            if i == 0:
                for line in f1_i.readlines():
                    if line.splitlines()[0] != "</table>":
                        f1.write(line)
                    else:
                        f1.write('\n')
                        break
                for line in f2_i.readlines():
                    if line.splitlines()[0] != "</table>":
                        f2.write(line)
                    else:
                        f2.write('\n')
                        break
                for line in f3_i.readlines():
                    if line.splitlines()[0] != "</body>":
                        f3.write(line)
                    else:
                        f3.write('\n')
                        break
            
            # Last part
            elif i == number_of_files - 1:
                WRITING = False
                for line in f1_i.readlines():
                    if not WRITING and line.splitlines()[0] == "<table>":
                        WRITING = True
                        continue
                    if WRITING:
                        f1.write(line)
                WRITING = False
                for line in f2_i.readlines():
                    if not WRITING and line.splitlines()[0] == "<table>":
                        WRITING = True
                        continue
                    if WRITING:
                        f2.write(line)
                WRITING = False
                for line in f3_i.readlines():
                    if not WRITING and line.splitlines()[0] == "<body>":
                        WRITING = True
                        continue
                    if WRITING:
                        f3.write(line)
            
            # Middle parts
            else:
                WRITING = False
                for line in f1_i.readlines():
                    if not WRITING and line.splitlines()[0] == "<table>":
                        WRITING = True
                        continue
                    if WRITING:
                        if line.splitlines()[0] == "</table>":
                            f1.write('\n')
                            break
                        f1.write(line)
                WRITING = False
                for line in f2_i.readlines():
                    if not WRITING and line.splitlines()[0] == "<table>":
                        WRITING = True
                        continue
                    if WRITING:
                        if line.splitlines()[0] == "</table>":
                            f2.write('\n')
                            break
                        f2.write(line)
                WRITING = False
                for line in f3_i.readlines():
                    if not WRITING and line.splitlines()[0] == "<body>":
                        WRITING = True
                        continue
                    if WRITING:
                        if line.splitlines()[0] == "</body>":
                            f3.write('\n')
                            break
                        f3.write(line)
            
            f1_i.close()
            f2_i.close()
            f3_i.close()
            
            # Remove partial files that have been read
            for f in [html_file, html_abstracts_file, html_bib_file]:
                os.remove(f % str(i))
            
        f1.close()
        f2.close()
        f3.close()
    
    
    # Step 5: Format the generated .bib file to remove the fields file, abstract, ...
    # format_bib.main(infile=outfile, outfile=outfile)  # this is obsolete
    bibutils.format_output(new_bib, excluded_fields = EXCLUDED_FIELDS + ('abstract', 'month', 'file'))
    bibutils.write_bib_file(new_bib, outfile)
    
    # Step 6 (additional): Check for any duplicate citation keys
    bibutils.check_duplicate_citekeys(new_bib)
    

def format_bib_html(html_file):
    f = open(html_file, 'rb')
    new_content = []
    buf = [None] * 5
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
            line = line.replace(' <b>', ' <font color="MediumVioletRed">')  # DarkMagenta
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
        
        if not html_file.endswith("_bib.html"):
            if '>.pdf</a>' in line:
                line = line.replace('>.pdf</a>', '>http</a>')
            elif '>.html</a>' in line:
                line = line.replace('>.html</a>', '>http</a>')
            # elif '>http</a>' in line:
            #     line = line.replace('>http</a>', '>http</a>')
            if any(i in line for i in [">bib</a>", ">doi</a>", ">PDF</a>", ">http</a>", ">abstract</a>"]):
                s = line.strip().lstrip("[&nbsp;").rstrip("&nbsp;]").rstrip('&nbsp;|')
                s = "&#x202F;" + s + "&#x202F;"
                if ">PDF</a>" in s:         buf[0] = s
                elif ">doi</a>" in s:       buf[1] = s
                elif ">http</a>" in s:      buf[2] = s
                elif ">abstract</a>" in s:  buf[3] = s
                elif ">bib</a>" in s:       buf[4] = s
                else:                       buf.append(s)
                
                if line.endswith("</a>&nbsp;]"):
                    buf = list(filter(None, buf))
                    newline = '[' + '|'.join(buf) + ']'
                    new_content.append(newline)
                    buf = [None] * 5
                    continue
                else:
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


if __name__ == '__main__':
    startTime = time.time()
    main()
    print('Processing done. It took: %1.2f' % (time.time() - startTime), 'seconds.')
