# -*- coding: utf-8 -*-
#!/usr/bin/python
from sys import argv
from time import sleep
from urllib2 import urlopen
import re
class PageSlimer:
	def __init__(self,url):
		self.URL=url
		self.page=self.getHtmlCode(url)
		self.fh=0
	def doSlim(self):
    	#url=raw_input('请输入url: ')
#page=getHtmlCode(URL)
#<title>标签一般在最前面，所以直接提取其内容作为文件名
#先针对以<div>标签分功能段的网页进行处理，递归进入div段，找<p>段落标签，循环处理。如果<p>中有h1,h2，br等，进行换行,<u>网址无影响，对<a xx</a>简化，替换转义字符为相应字符,之后针对无div的页面处理
		end=len(self.page)
		print 'page size is:',end
		pattern=re.compile(r'<title>(.*?)</title>',re.S)
		title=pattern.findall(self.page)
		name=title[0]+'.txt'#trim()
		try:
			self.fh=open(name,'w')
		except:
			pass
		start=self.page.find('<div ')
#if not find,will return -1
		if start>0:
			deep=1
			self.handleDiv(start+5,deep)			
		self.fh.close()

	def getHtmlCode(self,url):	#get html code
		fl = urlopen(url)
		source=fl.read()
		fl.close()
		return source
	def handleDiv(self,start,deep):#deep is div的嵌套层次the in curse hirachy,递归时加1,可以作为段落编号
#由于要共享page这个变量，决定做成类的成员变量
#print 'in handleDiv:start=',start
		print 'deepth:',deep
		p1=self.page[start:].find('</div>')
		place=self.page[start:].find('<div ')
		if place>0 and place<p1:
			print '</div,<div',p1,place
#			sleep(2)
			place=start+place+5
			self.handleDiv(place,deep+1)
		para_s=self.page[start:].find('<p>') #start
#maybe <p class=...
		if para_s>0:
			para_s=start+para_s
		else:
	   		return
#		print 'para_s is:',para_s
		while(1):
			
			para_e=para_s+self.page[para_s:].find('</p>')
			self.slimText(para_s+3,para_e)#do specific thing
			para_s=self.page[para_e+4:].find('<p>') #start
			if para_s<0:
				break
			else:
				para_s=para_e+4+para_s
		if self.page[start:].find('</div>'):
			return

	def slimText(self,begain,end):
		'''在指定的字符串或文件的末尾附加文本，如果是保存到文件，则关闭文件描述符的语句应放到doSlim的最后。'''
#print self.page[begain:end]
		self.fh.write(self.page[begain:end])
	def doTrans(self,s,e):#对两种转义字符进行替换
#pattern
		pass
	def slimHref(self): #处理<a href以及<u>这种网址标签
#google
		pass

if __name__=='__main__' :
	url=argv[1]
	subdir=argv[2]
	filename=argv[3]
#print 'sys.argv[1]:',url
	pageslimer=PageSlimer(url)
	pageslimer.doSlim()
