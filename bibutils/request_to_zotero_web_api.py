#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import requests


def request_to_zotero_web_api(limit, start):
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
