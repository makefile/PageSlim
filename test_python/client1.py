#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import httplib
import time
import re
#url='http://127.0.0.1:1366/doslim?url=http://127.0.0.1:1366/program/pageSlimer/linux-usage.html&dir=default&name=linux-tips'
url='http://127.0.0.1:1366/doslim?url=http://127.0.0.1:1366/program/pageSlimer/linux-usage.html&dir=default&name=default'
#url='http://127.0.0.1:1366/doslim?url=http://dijunzheng2008.blog.163.com/blog/static/9895989720105254255575/&dir=blog&name=default'
#url='http://127.0.0.1:1366/doslim?url=http://www.jb51.net/article/50851.htm&dir=blog&name=default'
#url='http://www.jb51.net/article/50851.htm'

#url='http://127.0.0.1:1366/doslim?url=http://justcoding.iteye.com/blog/898562&dir=blog&name=default'

#url='http://127.0.0.1:1366/doslim?url=http://blog.csdn.net/facevoid/article/details/5338048&dir=blog&name=default'
#con.set_debuglevel(1)
src=urllib.urlopen(url)
#encode('utf-8')
text=src.read()
src.close()
print text[:800]
nm=re.search(r'(?<=filename:).+?(?=$)',text,re.M)
filename=nm.group(0)
print 'size:%s,filename:%s'%(len(text),filename)
'''#x.info()
#headers
#######################
boundary='---------%s'%hex(int(time.time()*1000))
data=[]
data.append('--%s'%boundary)
#data.append('Content-Disposition:form-data;name="%s"\r\n'%'dir')
data.append('dir=default')#= not : in my server
#data.append('--%s'%boundary)
#data.append('Content-Disposition:form-data;name="%s"\r\n'%'filename')
data.append('filename=%s'%filename)
#data.append('--%s\r\n'%boundary)
data.append('\n')
#因为是自己写的服务端，所以构造的这些数据比较随意了，按服务端的要求来写
#ignore the first line:filename
content='modified by fyk!\n'+text[9+len(filename):]
data.append(content)
data.append('\n--%s--\n'%boundary)
body='\r\n'.join(data)

try:
#	req=urllib2.Request(url,body)
#	req.add_header('Content-Type','multipart/form-data;boundary=%s'%boundary)
#User-Agent etc
#	resp=urllib2.urlopen(req,timeout=5)#post	
#	rescontent=resp.read()
	print '*********************'
	conn=httplib.HTTPConnection('127.0.0.1:1366')
#print 'before post:',body
	conn.request(method="POST",url="/modify",body=body);
	response=conn.getresponse();
	if response.status==200: #302 etc
		print '发布成功!^_^!';
	else:
		print "发布失败\^0^/"
	conn.close()

except Exception,e:
	print 'http error:',e	'''
#params=urllib2.urlencode(raw_params)	
print '*********************'
