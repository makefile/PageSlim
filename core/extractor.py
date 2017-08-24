# -*- coding: utf-8 -*-
#!/bin/python
import re

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
#删除多余空行为一个换行
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

def remove_image (s):
	
	r = re.compile (r'''<img.*?>''',re.I|re.M|re.S)
	s = r.sub('',s)
	return s

def remove_video (s):
	r = re.compile (r'''<embed.*?>''',re.I|re.M|re.S)
	s = r.sub('',s)
	return s
class Extractor:
	def __init__(self,page,directory,filename):
		'''
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
		'''
		'''
		/* 当待抽取的网页正文中遇到成块的新闻标题未剔除时，只要增大此阈值即可。*/
		/* 阈值增大，准确率提升，召回率下降；值变小，噪声会大，但可以保证抽到只有一句话的正文 */
		'''
		self.page=page
		self.threshold =600#140 86
		self.blocksWidth = 5 #
		self.lines=[]
		self.blockSize=[]
		self.pre_process(page)
	def pre_process(self,s): #传值方式同java
		s=remove_js_css (s)
		s=remove_video (s)
		#s=remove_empty_line(s)  
		r = re.compile (r'<!DOCTYPE.*?>',re.I|re.M|re.S)
		s = r.sub('',s)
		r = re.compile (r'<!--.*?-->',re.I|re.M|re.S) #remove html comment
		s = r.sub('',s)
		r = re.compile (r'<link .*?rel=.*?/>',re.I|re.M|re.S)
		s = r.sub('',s)
		r = re.compile (r'<input type=.*?/>',re.I|re.M|re.S)
		s = r.sub('',s)
		#r = re.compile (r'<.*?>',re.I|re.S) #remove any tag
		#s = r.sub('',s)
		self.page=s
		#r = re.compile (r'&.{2,5};|&#.{2,5};',re.I|re.M|re.S) #special char,转义字符，需要转义，不能删除
		fh=open('pre_process','w');
		fh.write(s)
		fh.close()
	'''
	得到正文部分，对于图片只保留正文中的图片链接，只保留地址信息，<img开头的可能在单独一行也可能在一行文字的后边，只考虑单行的，而藏身在行后的是一些小的资源图片。
	'''
	def get_spec_text(self):
		
		self.lines=self.page.split('\n')
		line_num=len(self.lines)
		block_num=line_num - self.blocksWidth
		print 'line_num:',line_num
		#hasImage_line=[]
		wordsNum = 0
		for j in range (0,self.blocksWidth):#calc first block
		#剔除多余的空格，影响值的计算
			wordsNum += len(self.lines[j])
		self.blockSize.append(wordsNum)
		for i in range (1,block_num):#Dynamic Programming
			wordsNum =self.blockSize[i-1]-len(self.lines[i-1])+len(self.lines[i-1+self.blocksWidth])
			self.blockSize.append(wordsNum)
			#if '<img ' in self.lines[i] :
			#	hasImage_line.append(True)
			#else :
			#	hasImage_line.append(False)
		isStart=False
		isEnd=False
		start=-1
		end=-1
		text=''
		for i in range (0,block_num-1):
			
			if self.blockSize[i] > self.threshold and isStart==False :
				#if self.blockSize[i+1] !=0 or self.blockSize[i+2] !=0 or self.blockSize[i+3] !=0 :
				if self.blockSize[i+1]>self.threshold/2:# or self.blockSize[i+2] >15 :
					#print 'start'
					isStart=True
					start=i;
					continue
				#else 单独
			if (isStart==True):
				#网页后面部分可能有很多链接，评论等，因此将阈值减半
				if (self.blockSize[i] < self.threshold/2 or self.blockSize[i+1]< self.threshold/2) :#==0
					end = i; 
					isEnd = True;
			if (isEnd==True) :
				text+=self.get_part(start,end)
				isStart = isEnd = False;
		if isStart==True: #isEnd=False
			text+=self.get_part(start,line_num-1)
		text=remove_empty_line(text)
		#print 'extractor:',text
		return text
	
	def get_part(self,start_line,end_line):
				tmp=''
				for ii in range (start_line,end_line+1):
					if (len(self.lines[ii]) < 5) :
						continue;
					else :
						tmp+=(self.lines[ii])+("\n");
				#print 'start,end:',start,' ',end
				return tmp
