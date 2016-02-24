#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
VENAM WAS HERE
"""

import sys
import re
import time
import urllib
import json
import pycurl
import cStringIO
from threading import Thread

enc = json.JSONEncoder()
dec = json.JSONDecoder()
proxy_range = []
output_save = "REDDIT_LIST"
current_index = 0

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out


def create_browser(n):
    c2 = pycurl.Curl()
    c2 = create_header(c2)
    [c2, proxy] = get_proxy(c2, n)
    return [c2, proxy]

def create_header(c2):
    c2.setopt(pycurl.HTTPHEADER, [
        'user-agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0'
    ])
    return c2

def set_cookie(c, cookie, modhash):
    c.setopt(pycurl.HTTPHEADER, [
        'user-agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0',
        'cookie: reddit_session='+cookie,
        'X-Modhash: '+modhash
    ])
    return c

def get_proxy(c2, num):
    global proxy_range
    proxy = -1
    if num == 0:
        return [c2, proxy]
    c2.setopt(pycurl.PROXY, '192.168.0.12')
    proxy = proxy_range[num]
    c2.setopt(pycurl.PROXYPORT, proxy)
    c2.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
    c2.setopt(pycurl.CONNECTTIMEOUT, 6)
    c2.setopt(pycurl.TIMEOUT, 6)
    return [c2, proxy]

def upvote(link, login = False, username='', password='', p_num = 0):
    [br, proxy] = create_browser(p_num)
    print proxy
    buf = cStringIO.StringIO()
    br.setopt(br.WRITEFUNCTION, buf.write)
    user_modhash = ""
    if login:
        br.setopt(pycurl.URL, 'http://www.reddit.com/api/login')
        data = (('user', username), ('passwd', password), ('api_type','json'))
        br.setopt(pycurl.POST, 1)
        post = urllib.urlencode(data)
        br.setopt(pycurl.POSTFIELDS, post)
        br.perform()
    else:
        br.setopt(pycurl.URL, 'https://www.reddit.com/api/register/'+username)
        data = (('op', 'reg'), ('user', username), ('passwd', password), ('passwd2', password), ('api_type','json'))
        br.setopt(pycurl.POST, 1)
        post = urllib.urlencode(data)
        br.setopt(pycurl.POSTFIELDS, post)
        br.perform()
    f = buf.getvalue()
    print f
    user_data = dec.decode(f)
    if user_data['json']['errors'] == []:
        if not login:
            open(output_save, 'a').write(username+":"+password+"\n")
        user_modhash = user_data['json']['data']['modhash']
        cookie = user_data['json']['data']['cookie']
    else:
        print "Couldn't execute it, there was an error"
        print(user_data['json']['errors'])
        return

    buf = cStringIO.StringIO()
    br.setopt(br.WRITEFUNCTION, buf.write)
    br.setopt(pycurl.URL, 'http://www.reddit.com/api/vote')
    data = (('uh', user_modhash), ('dir', 1), ('id',link),  ('api_type','json'))
    br = set_cookie(br, cookie, user_modhash)
    br.setopt(pycurl.POST, 1)
    post = urllib.urlencode(data)
    br.setopt(pycurl.POSTFIELDS, post)
    br.perform()
    status_code = br.getinfo(pycurl.HTTP_CODE)
    if status_code == 200:
        print "Upvoted successfully"
    else:
        print "couldn't upvote"

def upvote_all(link, list_of_prox):
    #while 1:
    global current_index
    for prox in list_of_prox:
        try:
            current_index += 1
            upvote(link, False, 'todo'+str(current_index)+'_', 'secretodo', prox)
        except Exception,e:
            print e
            time.sleep(10)

if __name__ == '__main__':
    link = 'linktodo'
    nb_threads = sys.argv[1]
    start_proxy = int(sys.argv[2])
    end_proxy = int(sys.argv[3])
    proxy_range = range(start_proxy, end_proxy+1)
    z = chunkIt(proxy_range, nb_threads)
    for list_of_prox in z:
        Thread(target=upvote_all,
            args=(link, list_of_prox)).start()
