#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import datetime


def parse_bib(list_of_dicts):
    """
    list_of_dicts is a list of dictionaries, each dictionary has
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
                
                if field == 'dateadded':  # Parse 'dateadded' value to the datetime format
                    value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')  # e.g. "2016-12-16T09:26:45Z"
                
                if field == 'publisher' and 'Wiley' in value:
                    if value in ["{John Wiley \& Sons, Inc}", "{John Wiley \& Sons Inc}"]:
                        value = "{John Wiley \& Sons, Inc.}"
                    elif value in ["{John Wiley \& Sons Ltd}"]:
                        value = "{John Wiley \& Sons, Ltd}"
                
                if field == 'doi':
                    # Extract the true DOI from the ugly value like "doi:10.1063/1.3516290" or
                    # "10.1155/2015/780352,\%002010.1155/2015/780352" or "http://dx.doi.org/10.4230/DagRep.6.3.24"
                    if not value.startswith('10.') or ',' in value:
                        m = re.match(r'(.*?)(10.\d{4}/[^,]+)(.*)', value)
                        if m: value = m.group(2)
                
                if field == 'isbn' and ' ' in value:
                    value = value.split()[0]  # Take the first ISBN as a representative
                
                if field == 'pages' and '--' in value:
                    m = re.search(r'(.*\d+)(\s*--\s*)([a-zA-Z]?\d+.*)', value)
                    if m: value = m.groups()[0] + '--' + m.groups()[2]
                    m = re.search(r'([a-zA-Z0-9]+)--([a-zA-Z0-9]+)--([a-zA-Z0-9]+)--([a-zA-Z0-9]+)', value)
                    if m:
                        value = m.groups()[0] + '-' + m.groups()[1] + '--' + m.groups()[2] + '-' + m.groups()[3]
                
                if field == 'journal':
                    if value.startswith("The Journal of") or value.startswith("The International Journal of"):
                        value = value[4:]  # Remove the starting "The" from journal name
                    elif value == "Evol. Comput.":
                        value = "Evolutionary Computation"
                
                if field == 'type' and value.lower() == "phd thesis":
                    value = "{PhD} Thesis"
                # if field == 'edition':
                #     value = '{' + value + '}'
                
                # Standardize the format for author/editor names
                if field in ['editor', 'author']:
                    value = value.replace(", Prof Dr ", ", ").replace(", Professor ", ", ").replace(", Prof ", ", ").replace(", Dr ", ", ")
                    
                    # Fix for "Kulkarni, BhaskarD" or "Marques, JorgeM C." or "Young, NealE"
                    if re.search(r' \w+[a-z][A-Z]\.?(?:\s|$)', value):
                        authors = value.split(" and ")
                        for idx, author in enumerate(authors):
                            m = re.search(r'(.+\, \w+[a-z])([A-Z]\.?)(\s.+|$)', author)
                            if m:
                                authors[idx] = m.groups()[0] + " " + m.groups()[1] + m.groups()[2]
                        value = " and ".join(authors)
                    
                    # Fix for "Hsieh, Y. -C. and You, P. -S." or "Wan, Guohua and Yen, Benjamin P. -C."
                    if ". -" in value:  # if re.search(r' [A-Z]\.? -[A-Z]\.?', value)
                        value = value.replace(". -", ".-")
                    
                    # Fix for "Talbi, E-G." or "Wong, H-Y"; not "R-Moreno, Maria D." or "Kuo, I-Hong"
                    if re.search(r' [A-Z]-[A-Z]\.?(?:\s|$)', value):
                        authors = value.split(" and ")
                        for idx, author in enumerate(authors):
                            m = re.search(r'(.*)( [A-Z])-([A-Z])\.?(\s.+|$)', author)
                            if m:
                                authors[idx] = m.groups()[0] + \
                                               m.groups()[1] + "." + "-" + m.groups()[2] + "." + \
                                               m.groups()[3]
                        value = " and ".join(authors)
                    
                    # Fix for "Suganthan, P.N." or "Price, John W.H"
                    if re.search(r'( [A-Z]\w+)* [A-Z]\.([A-Z]\.?)+', value):
                        value = format_certain_author_names(value)
                    
                    # Fix for "Dinh, Huy Q" or "Goodman, S N" or "Maderia, JFA" or "Bland, J M. and Altman, D. G"
                    #elif re.search(r'( [A-Z]\w+)* [A-Z]+ ', value) or \
                    #     re.search(r'( [A-Z]\w+)* [A-Z]+$', value):
                    elif re.search(r'( [A-Z]\w+)* [A-Z]+(?:\s|$)', value):
                        value = format_certain_author_names(value)
                    
                    # Fix for "Bland, J M." or "Francisco, AP."
                    elif re.search(r'( [A-Z]\w+)* [A-Z]+(\s?[A-Z]\.)+(?:\s|$)', value):
                        value = format_certain_author_names(value)
                    
                    # Fix for "Nebro, A.j." or "Wortel, V. a. L." or "Fatemi Ghomi, S.m.t."
                    elif re.search(r' ([A-Za-z][\.|-|\s][\s|-]?)+[a-z]\.?(?:\s|$)', value):
                        value = format_certain_author_names(value)
                    
                    # Fix for "Beck, J Christopher"
                    elif re.search(r' [A-Z] [A-Z]\w+', value):
                        #print(value)
                        value = format_certain_author_names(value)
                        #print(value)
                        #print("")
                
                if field == 'year' and len(value) != 4:
                    m = re.search(r'[1|2]\d{3}', value)
                    if m: value = m.group()
                
                if field == 'file':
                    # Deal with multiple attachments
                    if value.count(';') >= 1 and (value.count(':application/') + value.count(':image/')) > 1:
                        buffer = value.split(';')  # gets wrong if there exists ';' in the filename of
                                                # any of the multiple attachments -- but this is rare!
                    else:
                        buffer = [value]
                    
                    # Try to identify all attachments
                    if buffer:
                        value_list = []
                        for buf in buffer:
                            m = re.search(r'\.pdf:(.*\.pdf):application/', buf)
                            if not m:
                                m = re.search(r'\.djvu:(.*\.djvu):application/', buf)
                            if not m:
                                m = re.search(r'\.zip:(.*\.zip):application/', buf)
                            if not m:
                                m = re.search(r'\.docx:(.*\.docx):application/', buf)
                            if not m:
                                m = re.search(r'\.doc:(.*\.doc):application/', buf)
                            if not m:
                                m = re.search(r'\.xlsx:(.*\.xlsx):application/', buf)
                            if not m:
                                m = re.search(r'\.xls:(.*\.xls):application/', buf)
                            if not m:
                                m = re.search(r'\.jpg:(.*\.jpg):image/', buf)
                            if m:
                                buf = m.groups()[0]
                                buf = "file://" + buf.replace('\:\\\\', ':/').replace('\\\\', '/').replace('\\', '/')
                                value_list.append(buf)
                        
                        # Get the first PDF as a representative value for the field 'file'
                        pdfs = [v for v in value_list if v.endswith('.pdf')]
                        if pdfs:
                            value = pdfs[0]
                    
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
                    
                    value = re.sub(r'(^|\s|[^{}(/\$\s]+)(\b[B-Z]\b)([^{})\s]+|\s|$)', r'\1{\2}\3', value)
                    value = re.sub(r'((?:^|\s).+?/)([B-Z])(\+*(?:\s|$))', r'\1{\2}\3', value)  # Fix for "{S}/R" or "{C}/C++"
                    value = re.sub(r'(^|\s){([A-Z])}(\\&[A-Z])($|\s)', r'\1{\2\3}\4', value)  # Fix for "{B}\&B"
                    value = re.sub(r'(Part {II.} )', r'Part {II}. ', value)  # Fix for "Genetic Algorithms: Part {II.} Hybrid Genetic"
                    value = re.sub(r'\b([A-Z])({\\\'e}.+?)\b', r'{\1}\2', value)  # Fix for "L{\'e}vy" or "{B}{\'e}zier"
                    value = re.sub(r'\b(Pareto|Levy|Python|Java)\b', r'{\1}', value)  # Fix for "Python/{C}" or "{jMetal}: A Java Framework"
                    value = re.sub(r"\`\`([a-z])([a-z].*?)\'\'",
                                   lambda m: "``" + m.group(1).upper() + m.group(2) + "''", value)  # ``fuzzy Logic''
                    value = re.sub(r"(^|\s){\`\`([A-Za-z\-\/]+)\'\'}($|[\s\.\:\?\!])",
                                   lambda m: m.group(1) + "``{" + m.group(2) + "}''" + m.group(3), value) # "{``MOSS''}" or "{``hABCDE''}: Hybrid"
                    value = re.sub(r'(\A|\s)([1-6])D(\Z|\s|\-|\.|\:\?)', r'\1\2{D}\3', value)  # Fix for "3D" or "2D"
                    
                    # Capitalize after '?' or '.' in "Aleatory or epistemic? Does it matter?" or "... uncertainty. Part {II}"
                    m = re.search(r'(.+?[\?\.]\s)([A-Z][a-z]*)(.*)', value)
                    if m and not m.groups()[0].endswith(" vs. "):
                        value = m.groups()[0] + '{' + m.groups()[1] + '}' + m.groups()[2]
                
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


def format_certain_author_names(names):
    authors = names.split(" and ")
    for idx, author in enumerate(authors):
        if ", " not in author:  # author with only lastname
            continue
        lastname, firstname = author.split(", ")
        firstnames = firstname.split()
        for i, word in enumerate(firstnames):
            if re.search(r'[A-Z](-[A-Z])?[a-z]+', word):
                pass
            elif "-" in word and len(word) == 3:
                pass
            elif word.isupper() and "-" not in word:
                word = word.replace(".", "")
                firstnames[i] = " ".join([initial + "." for initial in list(word)])
            elif re.search(r' ([A-Za-z][\.|-|\s][\s|-]?)+[a-z]\.?(?:\s|$)', names) and "-" not in word:
                # Fix for "Nebro, A.j." or "Wortel, V. a. L." or "Fatemi Ghomi, S.m.t."
                word = word.upper().replace(".", "")
                firstnames[i] = " ".join([initial + "." for initial in list(word)])
            else:
                pass
        firstname = " ".join(firstnames)
        authors[idx] = lastname + ", " + firstname  # authors[idx] = ", ".join([lastname, firstname])
    names = " and ".join(authors)
    return names


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
    
    string = re.sub(r'{\(([^\s\(\){}]+?)\)}', r'({\1})', string)  # Fix for "{(MINLPs)}" or "{(MA|PM)}" or "{(I-SIBEA)}"
    string = re.sub(r'{\(([^\s\(\){}]+?)}(.+?)\)(}?)', r'({\1}\2\3)', string)  # "{(EuroGP} 2003)" or "{(P-RBF} {NNs)}"
    string = re.sub(r'{(\(.+?\)[-\s])([^\s\(\){}]+?)}', r'\1{\2}', string)  # "{(1+1)-CMA-ES}"
    # string = re.sub(r'(^|\s){(\w+)\?}($|\s)', r'\1{\2}?\3', string)  # "{OR?}" or "{DE?}"
    
    # Fix for " reasoning\textemdash{}I" or " {reasoning\textemdash{}II}"
    # or "Production\textendash{}distribution Problem" or or "Hybrid {VNS\textendash{}TS} Algorithm"
    if "\\textemdash{}" in string:
        string = format_text_around_dash_in_title(title=string, dash='em')
    if "\\textendash{}" in string:
        string = format_text_around_dash_in_title(title=string, dash='en')
    
    return string


def format_text_around_dash_in_title(title, dash):
    #m = re.search(r'(.+[\s\-]|^)\{?([\w\-\/]+?)\}?(\\text(?:%s)dash\{\})(\w+?\b)\}?(.*)' % dash, title)
    m = re.search(r'(.+[\s\-]|^){?([\w\-\/]+?)}?(\\text%sdash{})(\w+?\b)}?(.*)' % dash, title)
    if m:
        if m.groups()[1].islower():
            m_groups_1 = m.groups()[1][0].upper() + m.groups()[1][1:]
        elif m.groups()[1].isupper():
            m_groups_1 = '{' + m.groups()[1] + '}'
        else:
            m_groups_1 = m.groups()[1]
        
        if m.groups()[3].islower():
            m_groups_3 = m.groups()[3][0].upper() + m.groups()[3][1:]  # still works if m.groups()[3] = 'a'
        elif m.groups()[3].isupper() and \
             (re.search(r'[IVX]+', m.groups()[3]) or len(m.groups()[3]) > 1):
            m_groups_3 = '{' + m.groups()[3] + '}'
        else:
            m_groups_3 = m.groups()[3]
        
        title = m.groups()[0] + m_groups_1 + m.groups()[2] + m_groups_3 + m.groups()[4]
        
        # Manual fixes
        if dash == 'en':
            title = title.replace("{L}\\textendash{}R", "{L}\\textendash{}{R}")
            title = re.sub(r'(Multi|Many|Non)\\textendash{}', r'\1-', title)
            title = re.sub(r'\\textendash{}(Based)', r'-\1', title)
            title = re.sub(r'(Lin|Nelder|Hooke)(\\textendash{})(Kernighan|Mead|Jeeves)', r'{\1}\2{\3}', title)
            title = re.sub(r'(Mann|Kruskal)(\\textendash{})(Whitney|Wallis)', r'{\1}\2{\3}', title)
            title = re.sub(r'(Navier|Savage)(\\textendash{})(Stokes|Dickey)', r'{\1}\2{\3}', title)
    
    return title
