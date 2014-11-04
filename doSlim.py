# -*- coding: utf-8 -*-
#!/bin/python
#数据挖掘
'''#src:http://www.jb51.net/article/50941.htm
平时打开一个网页，除了文章的正文内容，通常会有一大堆的导航，广告和其他方面的信息。
本文的目的，在于说明如何从一个网页中提取出文章的正文内容，而过渡掉其他无关的的信息。 
约定：
	   本文基于网页的不同行来进行统计，网页内容经过压缩的需要先解压，就是网页有正常的换行的。
	   有些新闻网页，可能新闻的文本内容比较短，但其中嵌入一个视频文件，因此，给予视频较高的权重；
	   这同样适用于图片，这里有一个不足，应该是要根据图片显示的大小来决定权重的，但本文的方法未能实现这一点。
	   由于广告，导航这些非正文内容通常以超链接的方式出现，因此文本将给予超链接的文本权重为零。
	   这里假设正文的内容是连续的，中间不包含非正文的内容，因此实际上，提取正文内容，就是找出正文内容的开始和结束的位置。      
步骤：
	   首先清除网页中CSS,Javascript,注释，Meta,Ins这些标签里面的内容，清除空白行。
	   计算每一个行的经过处理的数值（1）
	   计算上面得出的每行文本数的最大正子串的开始结束位置 
其中第二步需要说明一下：
	   对于每一行，我们需要计算一个数值，这个数值的计算如下：
			  一个图片标签img，相当于出现长度为50字符的文本 （给予的权重），x1,
			  一个视频标签embed，相当于出现长度为1000字符的文本, x2
			  一行内所有链接的标签 a 的文本长度 x3 ,
			  其他标签的文本长度 x4
			  每行的数值 = 50 * x1其出现次数 + 1000 * x2其出现次数 + x4 – 8
		//说明， -8 因为我们要计算一个最大正子串，因此要减去一个正数，至于这个数应该多大，我想还是按经验来吧。 
完整代码如下:'''
import re
import urllib2
import urllib
from sys import argv
from time import sleep
import os
import StringIO #used for gzip src
import gzip
def remove_js_css (content):
	""" remove the the javascript and the stylesheet and the comment content
	(<script>....</script> and <style>....</style> <!-- xxx -->) """
	r = re.compile(r'''<script.*?</script>''',re.I|re.M|re.S)
	s = r.sub ('',content) #表示将匹配到的部分替换为空
	r = re.compile(r'''<style.*?</style>''',re.I|re.M|re.S)
	s = r.sub ('', s)
	r = re.compile(r'''<!--.*?-->''', re.I|re.M|re.S)
	s = r.sub('',s)
	r = re.compile(r'''<meta.*?>''', re.I|re.M|re.S)
	s = r.sub('',s)
	r = re.compile(r'''<ins.*?</ins>''', re.I|re.M|re.S)
	s = r.sub('',s)
	return s

def remove_empty_line (content):
	"""remove multi space """
	r = re.compile(r'''^\s+$''', re.M|re.S)
	s = r.sub ('', content)
	r = re.compile(r'''\n+''',re.M|re.S)
	s = r.sub('\n',s)
	return s

def remove_any_tag (s):
	s = re.sub(r'''<[^>]+>''','',s)
	return s.strip()

def remove_any_tag_but_a (s):
	text = re.findall (r'''<a[^r][^>]*>(.*?)</a>''',s,re.I|re.S|re.S)
	text_b = remove_any_tag (s)
	return len(''.join(text)),len(text_b)

def remove_image (s,n=50):
	image = 'a' * n
	r = re.compile (r'''<img.*?>''',re.I|re.M|re.S)
	s = r.sub(image,s)
	return s

def remove_video (s,n=1000):
	video = 'a' * n
	r = re.compile (r'''<embed.*?>''',re.I|re.M|re.S)
	s = r.sub(video,s)
	return s

def sum_max (values):
	cur_max = values[0]
	glo_max = -999999
	left,right = 0,0
	for index,value in enumerate (values):
		cur_max += value
		if (cur_max > glo_max) :
			glo_max = cur_max
			right = index
		elif (cur_max < 0):
			cur_max = 0

	for i in range(right, -1, -1):
		glo_max -= values[i]
		if abs(glo_max) < 0.00001:
			left = i
			break
	return left,right+1

def method_1 (content, k=1):
	if not content:
		return None,None,None,None
	tmp = content.split('\n')
	group_value = []
	for i in range(0,len(tmp),k):
		group = '\n'.join(tmp[i:i+k])
		group = remove_image (group)
		group = remove_video (group)
		text_a,text_b= remove_any_tag_but_a (group)
		temp = (text_b - text_a) - 8 
		group_value.append (temp)
	left,right = sum_max (group_value)
	return left,right, len('\n'.join(tmp[:left])), len ('\n'.join(tmp[:right]))

def extract (content):
	content = remove_empty_line(remove_js_css(content))
	left,right,x,y = method_1 (content)
	return '\n'.join(content.split('\n')[left:right])

#代码 从最后一个函数开始调用。

class PageSlimer:
	def __init__(self,page,directory,filename):
		
		self.page=page
		self.directory=directory
		self.filename=filename
		if not os.path.exists(self.directory):
			os.makedirs(self.directory)
		elif os.path.isfile(self.directory):
			os.makedirs(self.directory)
#self.fh=None#wrong!!,can't be None
		try:
			self.fh=open(self.directory+'/'+self.filename,'w')
		except:
			print 'open file error:',filename
	def doSlim(self):
		#url=raw_input('请输入url: ')
#page=getHtmlCode(URL)
#<title>标签一般在最前面，所以直接提取其内容作为文件名
#先针对以<div>标签分功能段的网页进行处理，递归进入div段，找<p>段落标签，循环处理。如果<p>中有h1,h2，br等，进行换行,<u>网址无影响，对<a xx</a>简化，替换转义字符为相应字符,之后针对无div的页面处理
		#end=len(self.page)
		#print 'page size is:',end
		#lstrip这个字符串方法，会删除字符串s开始位置前的空格。s.rstrip()s.strip()
#os.path.exists(r'xxx'),os.path.isfile()
		#start=self.page.find('<div ')
#if not find,will return -1
		self.handleDiv()			
		self.fh.close()

	'''def getHtmlCode(self,url):	#get html code
		fl = urlopen(url)
		source=fl.read()
		fl.close()
		return source'''
	def handleDiv(self):
		
		pattern=re.compile(r'<p.*?>(.*?)</p>',re.S)                
		para_cont=pattern.findall(self.page)                
		for p in para_cont:
            #这里再次去除div的标签，<b>,<iframe src等
			self.addPara(p)#do specific thing
		
	def addPara(self,para_text):
		'''在指定的字符串或文件的末尾附加文本，如果是保存到文件，则关闭文件描述符的语句应放到doSlim的最后。'''
#print para_text+'\n'
		para_text=self.doTrans(para_text)
		para_text=self.removeMarks(para_text)
		self.writeLine(para_text)
	def writeLine(self,line):
		self.fh.write(line+'\n')
	def doTrans(self,para_text):#对转义字符进行替换
#pattern
#字符串替换 s=re.sub(x,y,s) 或s2=s.replace(x,y)
		ret =re.sub(r'&nbsp;|&#160;',' ',para_text)
		ret=re.sub(r'<br>|<br />|</br>','\n',ret)
		ret=re.sub(r'<p>|</p>','\n',ret)
#^ represents not,[^>\"\s]表示不以>开始且不以",空格开始
	#处理<a href以及<u>这种网址标签
		hyperlink_pat=re.compile('<\s*[Aa]{1}\s+[^>]*?[Hh][Rr][Ee][Ff]\s*=\s*[\"\']?([^>\"\']+)[\"\']?.*?</a>')
		hrefs=hyperlink_pat.findall(ret)
		for h in hrefs:
			ret=hyperlink_pat.sub(h,ret)
		comment_pat=re.compile(r'<!--(.*?)-->');
#remove comment
		ret=comment_pat.sub('',ret)
#simpilfy the link
		u_pat=re.compile(r'<u>(.*?)</u>');
		u_links=u_pat.findall(ret)
		for u in u_links:
			ret=u_pat.sub(u,ret)
		ret =re.sub(r'&gt;|&#62;','>',ret)
		ret =re.sub(r'&lt;|&#60;','<',ret)
		ret =re.sub(r'&amp;|&#38;','&',ret)
		ret =re.sub(r'&quot;|;&#34;','\"',ret)
		ret =re.sub(r'&amp;|&#38;','&',ret)
		ret =re.sub(r'&#161;|&iexcl;','?',ret)
		ret =re.sub(r'&#9;','    ',ret) #tab key
		return ret
	def removeMarks(self,para_text):#删除额外的标签或进行替换
		ret =re.sub(r'<div>|</div>','',para_text)
		ret=re.sub(r'<pre>|</pre>','',ret)
		ret=re.sub(r'<strong>|</strong>','',ret)
		ret=re.sub(r'<a>|</a>','',ret)
		ret=re.sub(r'<b>|</b>','',ret)
		ret=re.sub(r'<em>|</em>','',ret)
		ret=re.sub(r'<ul>|</ul>','',ret)
		ret=re.sub(r'<td>|</td>',' ',ret) #table
		div_pat=re.compile(r'<div .*?\".*?\".*?>')
		ret=div_pat.sub('',ret)
		img_pat=re.compile(r'<img src=.*?>',re.I)
		ret=img_pat.sub('',ret)
		a_pat=re.compile(r'<a name=".*?>',re.I)
		ret=a_pat.sub('',ret)
		span_pat=re.compile(r'<span .*?".*?>(.*?)</sapn>',re.I)
		ret=span_pat.sub('',ret)
		
		return ret
class SmartRedirectHandler(urllib2.HTTPRedirectHandler):     
	def http_error_301(self, req, fp, code, msg, headers):  
		result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)              
		result.status = code                
		return result                                       
	def http_error_302(self, req, fp, code, msg, headers):   
		result = urllib2.HTTPRedirectHandler.http_error_302(
		self, req, fp, code, msg, headers)              
		result.status = code                                
def getContent(url):#待解决：gzip解压及网页编码识别，第一次找到charset即可
#如果没解决gzip，就不要在Accept-Encoding中加，否则解析不了
	pattern=re.compile(r'http://(.*?)/',re.S)
	host=pattern.findall(url)
	host=host[0]
	print host
	homeReq = urllib2.Request(url)
	homeReq.add_header('Host',host)
	homeReq.add_header('Accept', 'text/html, application/xhtml+xml, */*');
	homeReq.add_header('Accept-Language', 'zh-cn;en-US')
	homeReq.add_header('Accept-Encoding', 'gzip, deflate')#gzip,deflate
	homeReq.add_header('Connection', 'Keep-Alive');
#homeReq.add_header('Referer', 'http://www.sogou.com')
	homeReq.add_header('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)');
	homeReq.add_header('Cache-Control', 'max-age=0')
	opener=urllib2.build_opener(SmartRedirectHandler())
	resp = opener.open(homeReq)
#	resp = urllib2.urlopen(homeReq)
#	print resp.headers
	encoding=(resp.headers).get('Content-Encoding', 'deflate')
#in case not found
#	encoding=resp.headers['Content-Encoding'] #前面很可能会有空格
	print 'encoding:',encoding
	data =resp.read()
	if(re.search('gzip',encoding,re.I)!=None):
		compressedstream = StringIO.StringIO(data)
		gzipper = gzip.GzipFile(fileobj=compressedstream)
		data = gzipper.read()
		print 'gzip:',data[:50]
	return data
def getCharset(page):
	pattern=re.compile(r'charset',re.S)
	charsets=pattern.findall(page)
	if len(charsets)>0:
		return charset[0]
	else return 'default'
	
if __name__=='__main__':
	#url='http://www.jb51.net/article/50941.htm'
	#url='http://news.sohu.com/20131229/n392604462.shtml'
	#url='http://tech.163.com/13/1230/10/9HB88VE600094NRG.html'
	#url='http://liyinghuan.baijia.baidu.com/article/2011'
	url=argv[1];
	realdir=argv[2];
	filename=argv[3];
#content=urllib2.urlopen(url).read()
	content=getContent(url)
'''charset=getCharset(content)
#if charset='gb2312':
	content=content.decode('gb2312').encode('utf-8') '''

#不管filename是不是default都将文本标题提取出来存至文件，返回给客户端的内容包括：文件名，标题，（大小），正文
	pattern=re.compile(r'<title>(.*?)</title>',re.S)
	title=pattern.findall(content)
	if filename=='default':
		if(len(title)>0):
			filename=title[0].strip()#s.rstrip
		else :
			pattern=re.compile(r'<h1>(.*?)</h1>',re.S)
			title=pattern.findall(content)
			if(len(title)>0):
				filename=title[0].strip()
	filename =re.sub(' ','',filename) #remove all space
	fh=open('newest','w');
	fh.write(filename);
	print 'in py,write "%s" to newest'%filename
	fh.close()
	sim=extract(content)
	print 'create in dir:',realdir
	pageslimer=PageSlimer(sim,realdir,filename) #返回的页面再交由自己的pageSlimer处理会更简单一些
#print 'title:',title
	pageslimer.writeLine(filename)
	pageslimer.doSlim()
