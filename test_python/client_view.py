#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
url="http://127.0.0.1:1366/view?dir=/home/fyk/my_httpd/my_httpd.conf"
page=urllib.urlopen(url).read()
print page
