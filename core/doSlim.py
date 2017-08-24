# -*- coding: utf-8 -*-
#!/bin/python

import re
import urllib2
import urllib
from sys import argv
from time import sleep
import os
import StringIO #used for gzip src
import gzip
import chardet
import sys

from extractor import Extractor
import socket
socket.setdefaulttimeout(8.0) 
'''
'''
class PageSlimer:
	def __init__(self,page,directory,filename,page_host):
		
		self.page=page
		self.directory=directory
		self.filename=filename
		self.page_host=page_host #the host server addr of the origin page
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
#<title>标签一般在最前面，所以直接提取其内容作为文件名
#先针对以<div>标签分功能段的网页进行处理，递归进入div段，找<p>段落标签，循环处理。如果<p>中有h1,h2，br等，进行换行,<u>网址无影响，对<a xx</a>简化，替换转义字符为相应字符,之后针对无div的页面处理
		#lstrip这个字符串方法，会删除字符串s开始位置前的空格。s.rstrip()s.strip()
#os.path.exists(r'xxx'),os.path.isfile()
		#start=self.page.find('<div ')
#if not find,will return -1
		self.handleDiv()			
		self.fh.close()
	"""根据url获取文件名"""
	def getFileName(self,url):
	    if url==None: return None
	    if url=="" : return ""
	    arr=url.split("/")
	    return arr[len(arr)-1]
	def download_img(self,imgURL):
		print 'down_img:',imgURL
		try:
			r = urllib2.Request(imgURL)
			fl = urllib2.urlopen(r, data=None, timeout=4)
			data=fl.read()
			fl.close()
			saveDir=self.directory + '/image/'
			if not os.path.exists(saveDir):
				os.makedirs(saveDir)
			short_filename=self.getFileName(imgURL)
			absPath=saveDir+short_filename
			fh=open(absPath,'w+b')
			fh.write(data)
			fh.close()
			print "下载image成功："+ url
			return '/image/'+short_filename #absPath
		except Exception,e:
			print "下载失败:"+ url+'\nreason:',str(e)
			return ''
	#得到正文中图片的地址并去掉冗余信息，改成自己统一的格式
	#地址多是相对路径，也可能是绝对路径，需要分别处理
	def getImgSrc(self,lineText):
		pattern=re.compile(r'<img .*?src="(.*?)".*?>',re.I)
		imgSrc=pattern.findall(lineText)
		url_list=[]
		for url in imgSrc :
			index=url.find('://')
			if index <0 :#> -1: #URL is absolute
				#未来可能是https等，以后再说把
				url='http://'+self.page_host+'/'+url
			url_list.append(url)		
		
		return url_list	
	def handleDiv(self):
		pattern=re.compile(r'<ul.*?>(.*?)</ul>',re.S|re.M) 
		#只处理ul中的li，而先不管单独的外层的li，这估计很多类似link一样都是一些短行超链接
		#在removeMark中删掉这些。   
		#print self.page       
		ul_list=pattern.findall(self.page)
		ul_num=len(ul_list)
		if ul_num>0:
			for ul in ul_list:
				orig='<ul.*?>'+ul+'</ul>'
				dst='<p>'+ul+'</p>'
				self.page =re.sub(orig,dst,self.page)
			#	self.page=pattern.sub('<[pP]>'+ul+'</[pP]>',self.page)
			
			li_pat=re.compile(r'<li.*?>(.*?)</li>',re.S|re.M)
			li_list=li_pat.findall(self.page)
			for li in li_list:
			#	print 'get li'
				orig='<li.*?>'+li+'</li>'
				dst='\n'+'**'+li
				self.page =re.sub(orig,dst,self.page)
			#	self.page=li_pat.sub('**'+li+'\n',self.page)#item indent
		#上面将<ul>无序列表转换成了一个<p></p>
		self.page=self.remove_empty_line(self.page)
		pattern=re.compile(r'<[pP].*?>(.*?)</[pP]>',re.S)                
		para_cont=pattern.findall(self.page)   
		if len(para_cont)<1 :#目前尚未想出怎么处理大量运用div来分正文段的而不使用p
			para_cont=self.page.split('\n')
		#else :#div
		for p in para_cont:
			imgSrc_list=self.getImgSrc(p)
			if len(imgSrc_list)>0 :
				cnt=1
				for imgSrc in imgSrc_list:
			#只考虑在<p></p>之间的img，期望是有价值的大图
				#	imgFilename=self.download_img(imgSrc)
					if cnt==1:
						imgFilename='/image/UF3ui2.jpg'
					elif cnt==2:
						imgFilename='/image/rAZryu.jpg'
					cnt=cnt+1
					tag= '##<img src="'+imgFilename+ '"/>##' 
					self.writeLine(tag);
					print 'INFO>>added img path tag to text file:'
					print tag
				
			else:
					self.addPara(p)#do specific thing		
	def addPara(self,para_text):
		'''在指定的字符串或文件的末尾附加文本，如果是保存到文件，则关闭文件描述符的语句应放到doSlim的最后。'''
		para_text=self.removeMarks(para_text) #这里再次去除div的标签，<b>,<iframe src等
		para_text=self.doTrans(para_text) #针对博客之类教程类正文中有标签，转义与去除标签的顺序不能反
		self.writeLine(para_text)
	def writeLine(self,line):
		if line and line !='' and line!='\n' and line!='\r' and line!='\r\n':
			self.fh.write(line+'\n')
	#为了提高速度，应该把所有的编译后的正则表达式对象保存起来，因为要重复很多次
	def doTrans(self,para_text):#对转义字符进行替换
#pattern
#字符串替换 s=re.sub(x,y,s) 或s2=s.replace(x,y)
		ret =re.sub(r'&nbsp;|&#160;',' ',para_text)
		ret=re.sub(r'<br>|<br.*?/>|</br>','\n',ret)
	#	ret=re.sub(r'<p>|</p>','\n',ret)
#^ represents not,[^>\"\s]表示不以>开始且不以",空格开始
	#处理<a href以及<u>这种网址标签
		hyperlink_pat=re.compile('<\s*[Aa]{1}\s+[^>]*?[Hh][Rr][Ee][Ff]\s*=\s*[\"\']?([^>\"\']+)[\"\']?.*?</a>')
		hrefs=hyperlink_pat.findall(ret)
		for h in hrefs:
			ret=hyperlink_pat.sub(h,ret)
		#simpilfy the link
		u_pat=re.compile(r'<u>(.*?)</u>');
		u_links=u_pat.findall(ret)
		for u in u_links:
			ret=u_pat.sub(u,ret)
		ret =re.sub(r'&gt;|&#62;','>',ret)
		ret =re.sub(r'&lt;|&#60;','<',ret)
		ret =re.sub(r'&amp;|&#38;','&',ret)
		ret =re.sub(r'&quot;|;&#34;','\"',ret)
		ret =re.sub(r'&#161;|&iexcl;','?',ret)
		ret =re.sub(r'&#9;','    ',ret) #tab key
		ret =re.sub(r'&ndash;','--',ret)
		ret =re.sub(r'&times;|&#215;','×',ret) 
		ret =re.sub(r'&divide;|&#247;','÷',ret) 
		ret =re.sub(r'&rdquo;','"',ret) #right quoto
		ret =re.sub(r'&ldquo;','"',ret) #left quoto
		
		return ret
	def removeMarks(self,para_text):#删除额外的标签或进行替换
		ret =re.sub(r'<div>|</div>','',para_text)
		ret=re.sub(r'<pre>|</pre>','',ret)
		ret=re.sub(r'<strong>|</strong>','',ret)
		ret=re.sub(r'<wbr><b>|</b>','',ret)
		ret=re.sub(r'<em>|</em>','',ret)
		ret=re.sub(r'<ul>|</ul>','',ret)
		ret=re.sub(r'<td>|</td>',' ',ret) #table
		ret=re.sub(r'<li .*?>.*?</li>','',ret)
		ret=re.sub(r'<font .*?>|</font>','',ret)
		div_pat=re.compile(r'<div .*?\".*?\".*?>')
		ret=div_pat.sub('',ret)
		#img_pat=re.compile(r'<img .*?>',re.I)#src=
		#ret=img_pat.sub('',ret)
		#a_pat=re.compile(r'<a name=".*?>',re.I)
		#ret=a_pat.sub('',ret)
		a_pat=re.compile(r'link rel=".*?>',re.I)
		ret=a_pat.sub('',ret)
		span_pat=re.compile(r'<span .*?".*?>(.*?)',re.I)
		ret=span_pat.sub('',ret)
		ret=re.sub(r'</span>','',ret)
		tab_pat=re.compile(r'''<table\s(?=[\s])('[^']*'|"[^"]*"|[^'">])*>(.*?)</table>''',re.I)
		ret=span_pat.sub('',ret)#you can also pick the content in <td>
		
		return ret

	def remove_empty_line (self,content):
		#删除多余空行为一个换行"""remove multi space """
		r = re.compile(r'''^\s+$''', re.M|re.S)
		s = r.sub ('', content)
		r = re.compile(r'''\n+''',re.M|re.S)
		s = r.sub('\n',s)
		return s

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):     
	def http_error_301(self, req, fp, code, msg, headers):  
		result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)              
		result.status = code                
		return result                                       
	def http_error_302(self, req, fp, code, msg, headers):   
		result = urllib2.HTTPRedirectHandler.http_error_302(
		self, req, fp, code, msg, headers)              
		result.status = code                                
def getContent(url):#已解决：gzip解压及网页编码识别，第一次找到charset即可
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
#	resp = urllib2.urlopen(homeReq)
#	print resp.headers
#in case not found
#	encoding=resp.headers['Content-Encoding'] #前面很可能会有空格
	try:
		resp = opener.open(homeReq)
		encoding=(resp.headers).get('Content-Encoding', 'deflate')
		print 'encoding:',encoding
		data =resp.read()
		if(re.search('gzip',encoding,re.I)!=None):
			compressedstream = StringIO.StringIO(data)
			gzipper = gzip.GzipFile(fileobj=compressedstream)
			data = gzipper.read()
			#print 'gzip:',data[:50]
			print 'gunzip data succ!'
		return data,host
	except Exception,e:
		print 'fetch web content:',e
		return None,host
def getCharset(page):
	try:
		charset=chardet.detect(page)
		return charset['encoding']#map
	except:
		return 'default'
#	pattern=re.compile(r'charset',re.S)
#	charsets=pattern.findall(page)
#	if len(charsets)>0:
#		return charsets[0]
#	else:
#		return 'default'
	
'''param: 'url' realdir filename 
'''
if __name__=='__main__':
	#url='http://www.jb51.net/article/50941.htm'
	#url='http://news.sohu.com/20131229/n392604462.shtml'
	#url='http://tech.163.com/13/1230/10/9HB88VE600094NRG.html'
	#url='http://liyinghuan.baijia.baidu.com/article/2011'
	
	if len(argv) <3 :
		print 'ERROR:param should be '+"'url' realdir filename"
		sys.exit(1);#如果参数个数太小，则
	url=argv[1].strip('\'');
	realdir=argv[2];
	filename=argv[3];
	
	#url='http://news.sohu.com/20131229/n392604462.shtml'
	#url='http://www.weixinxi.wang/blog/aitrcle.html?id=9'
	#realdir='/home/fyk/program/pageSlimer/core'
	#filename='default';
#content=urllib2.urlopen(url).read()
		
	content,host=getContent(url)
	if content ==None :
		sys.exit(2);
	charset=getCharset(content)
#	if charset!='utf8':
	#decode默认的参数就是strict，代表遇到非法字符时抛出异常； 
	#如果设置为ignore，则会忽略非法字符； 
	#如果设置为replace，则会用?号取代非法字符； 
	#如果设置为xmlcharrefreplace，则使用XML的字符引用。
	content=content.decode(charset,'ignore').encode('utf-8') 
	print 'charset:',charset
#不管filename是不是default都将文本标题提取出来存至文件，返回给客户端的内容包括：文件名，标题，（大小），正文
	pattern=re.compile(r'(?i)<title>(.*?)</title>',re.S)#?i equal re.I
	title=pattern.findall(content)
	if filename=='default':
		if(len(title)>0):
			filename=title[0].strip()#s.rstrip
		else :
			pattern=re.compile(r'<h1>(.*?)</h1>',re.I)
			title=pattern.findall(content)
			if(len(title)>0):
				filename=title[0].strip()
	filename =re.sub(' ','',filename) #remove all space
	
	#fh=open('/tmp/newest','w');
	#fh.write(filename);
	#fh.write(content)
	#fh.close()
	try:
		fh=open('/dev/shm/newest','w');#/tmp/newest,共享区域，提取出的文件名在doSlim.c中需要使用发送给客户端
		fh.write(filename);
		print 'in py,write "%s" to newest'%filename
		fh.close()
	except:
		print 'tmp dir not exist,check the OS enviroment or modify this'
		
	'''fh=open('/tmp/newest','r');
	content=fh.read();
	fh.close()
	'''
	print 'CHANGE:in py,write "%s" to newest'%filename
	#sim=extract(content)
	#print len(content)
	extractor=Extractor(content,realdir,filename)
	sim=extractor.get_spec_text()
	fh=open('extractor_mid','w');
	fh.write(sim)
	fh.close()
	print 'text:',sim[:50]
	print 'create in dir:',realdir
	pageslimer=PageSlimer(sim,realdir,filename,host) #返回的页面再交由自己的pageSlimer处理会更简单一些
#print 'title:',title
	pageslimer.writeLine(filename)
	pageslimer.doSlim()
	sys.exit(0);