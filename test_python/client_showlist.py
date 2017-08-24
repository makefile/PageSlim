import urllib

url='http://127.0.0.1:1366/showlist'
json=urllib.urlopen(url).read()
print json
'''print 'size:',len(json)
print '*******************'
url='http://127.0.0.1:8080/view?dir=/home/fyk/my_httpd/default/test.txt'
obj=urllib.urlopen(url)
print obj.info()
text=obj.read()
print text[:62]
#print 'size:',len(text) '''
