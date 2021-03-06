#!/usr/bin/python
# -*- coding: utf-8 -*-
import wx
import urllib2
import urllib
import time
import re
import httplib
import sys 
import os
import socket
import cStringIO
#import io
from PIL import Image #dont use import Image ,maybe different

socket.setdefaulttimeout(15) #global
reload(sys) 
sys.setdefaultencoding('utf-8')
#如果不设置编码，则unicode等问题较麻烦,in windows,just use u'xxx'
from gui import MsgDialog
import wx.richtext as rt
class MainFrame(wx.Frame):
	def __init__(
			self, parent=None, id=wx.ID_ANY, title='网文快存', pos=wx.DefaultPosition,
			size=(776, 480), style=wx.DEFAULT_FRAME_STYLE):#size=wx.DEFAULT
		
		wx.Frame.__init__(self, parent, id, title, pos, size, style)
		
		self.SetIcon(wx.Icon('eye.png', wx.BITMAP_TYPE_PNG))   #loadIcon.ico
		menubar=wx.MenuBar()
		file_menu=wx.Menu()  	  
		help_menu=wx.Menu()  
		set_menu=wx.Menu()  
		file_menu.Append(101,'&Open','Open a new document')  
		file_menu.Append(102,'&Save','Save the document')  
		file_menu.AppendSeparator()  
		quit=wx.MenuItem(file_menu,105,'&Quit\tCtrl+Q','Quit the Application')  
		#quit.SetBitmap(wx.Image('stock_exit-16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap())  
		file_menu.AppendItem(quit)  
		help_menu.Append(103,'&Help','Seek help')
		set_menu.Append(104,'&设置','set profiles')
		menubar.Append(file_menu,'&File')  	  
		menubar.Append(help_menu,'&Help')  
		menubar.Append(set_menu,'&Setting')  
		self.SetMenuBar( menubar )
		wx.EVT_MENU(self, 105, self.OnQuit) 
		wx.EVT_MENU(self, 101, self.OnOpenFile) 
		wx.EVT_MENU(self, 102, self.OnSaveAs) 
		wx.EVT_MENU(self, 103, self.OnHelp) 
		wx.EVT_MENU(self, 104, self.OnSet) 
		panel = wx.Panel(self, wx.ID_ANY)

		button1 = wx.Button(panel, wx.ID_ANY, '快取')
		button1.SetBackgroundColour("gray")
		button1.SetForegroundColour("Navy")
		self.Bind(wx.EVT_BUTTON, self.OnGet, button1)
		button2 = wx.Button(panel, wx.ID_ANY, '退出')    #
		self.Bind(wx.EVT_BUTTON, self.OnQuit, button2)
		button3 = wx.Button(panel, wx.ID_ANY, '保存修改')    #
		self.Bind(wx.EVT_BUTTON, self.OnSave2server, button3)
		button2.SetBackgroundColour("gray")
		button2.SetForegroundColour("Red")
		button3.SetBackgroundColour("gray")
		button3.SetForegroundColour("Navy")
		self.urlButton = wx.Button(panel, wx.ID_ANY, 'URL:',size=(50,36))
		self.urlButton.SetForegroundColour('blue')
		self.Bind(wx.EVT_BUTTON, self.OnClear, self.urlButton)
		self.Bind(wx.EVT_CLOSE, self.OnQuit)#因该是点击x按钮关闭时调用

		self.Bind(wx.EVT_ICONIZE, self.OnIconfiy) # What is the meaning?设置缩小到底部任务栏和恢复时做的动作，比如发出提示，声音等

#urlLabel = wx.StaticText(panel, -1, "URL:")  
		default_url='http://192.168.1.6/test.html'
		#"http://www.weixinxi.wang/blog/aitrcle.html?id=9";
		#"http://www.linuxfan.com:1366/program/pageSlimer/linux-usage.html"
		self.urlText = wx.TextCtrl(panel, -1, default_url,size=(250, 38), style=wx.TE_MULTILINE)  #创建一个文本控件
		titleLabel = wx.StaticText(panel, -1, "标题:") 
		titleLabel.SetForegroundColour('blue') 
		self.titleText = wx.TextCtrl(panel, -1, "",size=(200, 30))
		self.titleText.SetInsertionPoint(0)
		self.urlText.SetInsertionPoint(0)#设置插入点
		catalogLabel = wx.StaticText(panel, -1, "归档目录:") 
		catalogLabel.SetForegroundColour('blue') 
		self.catalogText = wx.TextCtrl(panel, -1, "default",size=(200, 30))
		richTextLabel = wx.StaticText(panel, -1, "正文(可编辑):")
		#self.richText = wx.TextCtrl(panel, -1, "\n\n\n\n\t\t\t\t\t\t\t\t\t^_^",style=wx.TE_MULTILINE|wx.TE_RICH2) #创建丰富文本控件
		self.richText = rt.RichTextCtrl(panel, -1)
		#self.richText.SetInsertionPoint(0)  
		self.richText.SetForegroundColour('blue')
		#self.richText.WriteImage(wx.Image('../core/image/UF3ui2.jpg',wx.BITMAP_TYPE_ANY))
		#self.richText.Newline()
		#self.richText.SetDefaultStyle(wx.TextAttr("blue")) #设置文本样式,从1到4的字符，前景色，背景色
		#points = self.richText.GetFont().GetPointSize()   
		#f = wx.Font(points + 3, wx.ROMAN, wx.ITALIC, wx.BOLD, True) #创建一个字体  
		#self.richText.SetStyle(68, 82, wx.TextAttr("blue", wx.NullColour, f)) #用新字体设置样式  
		#sizer = wx.FlexGridSizer(cols=3, hgap=6, vgap=6)  
		#sizer = wx.BoxSizer(wx.HORIZONTAL)	#wx.VERTICAL
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.urlButton,flag=wx.LEFT)
		hbox1.Add(self.urlText,proportion=1)
		hbox1.Add(button1,flag=wx.LEFT,border=8)
		vbox.Add(hbox1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,border=10)
		vbox.Add((-1, 10))
		hbox2.Add(titleLabel,flag=wx.LEFT,border=8)
		hbox2.Add(self.titleText,proportion=2)
		hbox2.Add(catalogLabel,flag=wx.ALIGN_LEFT,border=8)
		hbox2.Add(self.catalogText,proportion=1)
		vbox.Add(hbox2,flag=wx.EXPAND|wx.LEFT|wx.RIGHT,border=10)
		vbox.Add((-1, 10))   #25px space    
		vbox.Add(richTextLabel,flag=wx.LEFT|wx.ALIGN_LEFT,border=18)
		vbox.Add((-1, 10))
		hbox3.Add(self.richText,proportion=1, flag=wx.EXPAND)
		vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
		vbox.Add((-1, 10))
		hbox4.Add(button3,flag=wx.ALIGN_RIGHT|wx.RIGHT,border=10) #save
		hbox4.Add(button2,wx.RIGHT,border=10) #exit
		vbox.Add(hbox4,flag=wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM,border=10)
		#sizer.Add(button1, 0)   #0表示比例
		#sizer.Add(button2, 3)
		#sizer.Add(button3, 5,wx.BOTTOM|wx.LEFT,wx.ALIGN_BOTTOM)
		#sizer.Add(button4, 5,wx.RIGHT|wx.BOTTOM,wx.ALIGN_BOTTOM)
		#panel.SetSizer(sizer)

		#sizer.AddMany([urlLabel, 	self.urlText,button1,titleLabel,self.titleText,-1 ,richTextLabel,self.richText,-1])  
		panel.SetSizer(vbox)
		self.clip = wx.TheClipboard #系统剪贴板,但是用wx.Clipboard()却不正确，很奇怪
		#http://www.wxpython.org/docs/api/wx.Clipboard-class.html
		#当左键点击窗口上任意普通位置时查看系统剪贴板是否有新网址，或在重绘时wx.EVT_PAINT
		#panel.Bind(wx.EVT_LEFT_DOWN, self.OnClickCheck)#对panel有效，但不知为什么对frame无效，改成：
		self.Bind(wx.EVT_ENTER_WINDOW,self.OnEnterWin)
		self.host=''
		self.filename=''
		self.user=''
		self.pw=''
		self.readConfigure()
		
	def OnHide(self, event):
		self.Hide()
	def OnGet(self, event):
		url=self.urlText.GetValue().strip()
		catalog=self.catalogText.GetValue().strip()
#the dir and name indicate where to save in the server
		if(url==''):
			wx.MessageBox('您还没输入网址','^0^')
			return
		try:
			src=urllib.urlopen('http://'+self.host+'/doslim?url='+url+'&dir='+catalog+'&name=default'+'&uid='+self.user)
#so strange that the urllib2.urlopen not work properly at times,is it beacause the server i write has problem of sending packet headers?
			text=src.read()
			src.close()
#print 'text:',text[0:40]
			#		flist=re.findall(r'^filename:(.*?)\n',text)
			nm=re.search(r'(?<=filename:).+?(?=$)',text,re.M)
			if nm!=None:
				self.filename=nm.group(0)
			#		print 'filename(0):%s<<<'%self.filename[0]
			self.filename=self.filename.strip()
			print 'read size:',len(text)
			print 'get filename:',self.filename #逗号变成空格
			#		text=re.sub('^filename:%s'%self.filename,'',text)
			text=text.replace('filename:%s'%self.filename,'')
			self.titleText.SetValue(self.filename)
			self.showContent(text.strip()) #content text has some format such as URL 
		except Exception,e:
			print e
			wx.MessageBox('请检查您的网络', '网络连接出错')
	def showContent(self,content):#解析文本内容中的特殊部分，如图片地址，显示到富文本框
		#[[<img src="/image/imgFilename">]],服务器地址因该是/uid/catagrory/image/filename
		#self.richText.WriteText(content)
		#self.richText.WriteText('-------------------\n')
		self.richText.SetValue('')
		lines=content.split('\n')
		for ln in lines:
			if ln.find('##<img src=') >=0:
				print ln
				pat=re.compile(r'##<img src="(.*?)"/>##')
				try:
					img_src=pat.findall(ln)[0]
					print 'find img_src:',img_src
					catalog=self.catalogText.GetValue().strip()
					url='http://'+self.host+'/dl?'+self.user+'/'+catalog+img_src
					img_str=urllib2.urlopen(url).read() #type str
					print 'size:',len(img_str)
					image_i = cStringIO.StringIO(img_str)
				#	print 'type of image_file:',type(image_file)
					pil_image=Image.open(image_i)
					wx_img=self.PILToWX(pil_image)
					self.richText.WriteImage(wx_img)
				#	self.richText.AddImage(image)
				except Exception,e:
					print e
			else :
				self.richText.WriteText(ln)#AppendText(ln)
			self.richText.Newline()
		#self.richText.SetValue(content)
		#self.richText.WriteImage(wx.Image('../core/image/UF3ui2.jpg',wx.BITMAP_TYPE_ANY))
	def PILToWX(self, pil_image):
		#"convert a PIL imageto a wxImage"
		if pil_image.mode != 'RGB': # SetData() requires an RGB image
			pil_image = pil_image.convert('RGB')
		imageData = pil_image.tostring('raw', 'RGB')
		imageWx = wx.EmptyImage(pil_image.size[0], pil_image.size[1])
		imageWx.SetData(imageData)
		return imageWx
		#bitmap = wx.BitmapFromImage(image)
	def OnIconfiy(self, event):
		wx.MessageBox('好好学习，天天向上!', '*送你一句良言*')
		event.Skip()
	def OnClear(self,event):
		self.urlText.Clear()
	def OnHelp(self,event):
		wx.MessageBox('1.复制粘帖网址到输入框，点击获取即可，内容会保存到云端\n2.您可以对获取到的内容进行编辑并重新保存至服务端\n3.您还可以导入导出文本文件', '*使用帮助*')

	def OnQuit(self, event):
		self.Destroy() #or close()
	
	def OnSave2server(self, event):
		text=self.richText.GetValue()
		catalog=self.catalogText.GetValue().strip()
		if text==None or catalog==None:
			wx.MessageBox('不能为空', '上传失败')
			return
		boundary='---------%s'%hex(int(time.time()*1000))
		data=[] #a list
#	data.append('\r\n')
		data.append('--%s'%boundary)
		data.append('uid=%s'%self.user)#username uid
		data.append('dir=%s'%catalog)#= not : in my server
#	print 'append data name:',self.filename
		data.append('filename=%s'%self.filename)
		data.append('\n')#因为是自己写的服务端，所以构造的这些数据比较随意了，按服务端的要求来写
		data.append('%s'%(time.asctime()))#列表在转换为字符串后会在每一项后面加换行
#ignore the first line:filename
#	body=''.join(data)
#	body=body.join('%s'%content)
#	body=body.join('\n--%s--\n'%boundary)
		data.append(text.encode('utf-8'))
		data.append('--%s--\n'%boundary)
		body='\r\n'.join(data) #text in textCtrl is unicode
		try:
			conn=httplib.HTTPConnection(self.host)
			conn.request(method="POST",url="/modify",body=body);
			response=conn.getresponse();
			if response.status==200: #302 etc
		#self.richText.SetValue(response)
				print '发布成功!^_^!';
				wx.MessageBox('修改已保存至云端！', '恭喜')
			else:
				wx.MessageBox('请检查您的网络', '上传失败')
				print "发布失败\^0^/"
			conn.close()

		except Exception,e:
			wx.MessageBox('请检查您的网络', '网络连接出错')
			print 'http error:',e
			#self.Hide()
	def OnCancel(self,event):
		pass    
	def readConfigure(self):
		try:
			fh=open('server.conf')
			size=len(fh.read())
			fh.seek(0)
			
			while(fh.tell()!=size):
				data=fh.readline()
				if(data[:4] == 'addr'): 
					self.host=data[5:].strip()#ip or domain,include port
				elif(data[:7]=='catalog'):
					self.catalogText.SetValue(data[8:].strip())
				elif(data[:2]=='id'):
					self.user=data[3:].strip()
				elif(data[:2]=='pw'):
					self.pw=data[3:].strip()
			fh.close()
		except:
			self.host='configuration not found!'
	def ReadFile(self,filepath):  
		if filepath:  
		    try:  
		        fh = open(filepath, 'r')  
		        data = fh.read()  
		        fh.close()  
		        self.richText.SetValue(data)  
		    except :  
                	wx.MessageBox("%s is not a expected file."  
                              % filepath, "error tip",  
                              style = wx.OK | wx.ICON_EXCLAMATION) 
	def OnOpenFile(self,event):
		file_wildcard="All files(*.*)|*.*"   
		dlg = wx.FileDialog(self,"Open file...", style = wx.OPEN,wildcard = file_wildcard)  
		if dlg.ShowModal() == wx.ID_OK:  
			filename = dlg.GetPath() 
			self.ReadFile(filename)
		dlg.Destroy()
	def SaveFile(self,filepath):
		text=self.richText.GetValue()
		fh=open(filepath,'w')
		fh.write(text)
		fh.close()
	def OnSaveAs(self, event):  
#	弹出文件保存对话框 
		file_wildcard="txt files(*.txt)|*.txt|All files(*.*)|*.*"   
		dlg = wx.FileDialog(self,"Save file as ...", style = wx.SAVE | wx.OVERWRITE_PROMPT,wildcard = file_wildcard)  
		if dlg.ShowModal() == wx.ID_OK:  
			filename = dlg.GetPath().encode('utf-8')  
			#if not os.path.splitext(filename)[1]: #如果没有文件名后缀  
			#	filename = filename + '.txt'    
			self.SaveFile(filename) 
		#self.SetTitle(self.title + '--' + self.savefilename)  
		dlg.Destroy()
		
	def OnSet(self,event):
		set_win = Setting(size=(476, 280))  #640,480 #1.618:1
		set_win.Centre()
		set_win.Show()
	def OnEnterWin(self, evt):
		#print 'on enter win'
		text_obj = wx.TextDataObject()
		if self.clip.IsOpened() or self.clip.Open():
			if self.clip.GetData(text_obj):
				text_str=text_obj.GetText()
				#print 'get text from clipboard',text_str
				#check if the text is formal URL
				if text_str !='' and re.match(r'^https?:/{2}\w.+$', text_str): #OK
					#compare with the URL in input
					old_url=self.urlText.GetValue().strip()
					if text_str !=old_url :
						self.urlText.SetValue(text_str)
					#	dlg = MsgDialog('URL已粘贴到输入框', '提示', ttl=2)               
		    		#		dlg.ShowModal()
			self.clip.Close()
	def showUp(self):
		#app = wx.PySimpleApp()
		self.Centre()
		self.Show() #可以让它设置是否在程序启动时一起显示出来
		#app.MainLoop()	
class Setting(wx.Frame):
	def __init__(
			self, parent=None, id=wx.ID_ANY, title='设置', pos=wx.DefaultPosition,
			size=wx.DEFAULT, style=wx.DEFAULT_FRAME_STYLE):
		wx.Frame.__init__(self, parent, id, title, pos, size, style)
		panel = wx.Panel(self, wx.ID_ANY)
		ipLabel = wx.StaticText(panel, -1, "服务器:")  
		ipLabel.SetForegroundColour('blue')
		self.ipText = wx.TextCtrl(panel, -1, "192.168.1.5",size=(250, 38))  #文本控件
		portLabel = wx.StaticText(panel, -1, "端口 号:") 
		portLabel.SetForegroundColour('blue') 
		self.portText = wx.TextCtrl(panel, -1, "1366",size=(200, 30))
		self.portText.SetInsertionPoint(0)
		self.ipText.SetInsertionPoint(0)#设置插入点
		catalogLabel = wx.StaticText(panel, -1, "归档目录:") 
		catalogLabel.SetForegroundColour('blue') 
		self.catalogText = wx.TextCtrl(panel, -1, "default",size=(200, 30))
		
		button1 = wx.Button(panel, wx.ID_ANY, '保存')
		button2 = wx.Button(panel, wx.ID_ANY, '取消')
		button1.SetBackgroundColour("gray")
		button1.SetForegroundColour("Navy")
		self.Bind(wx.EVT_BUTTON, self.OnSaveConf, button1)
		self.Bind(wx.EVT_BUTTON, self.OnCancel, button2)
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		
		hbox1.Add(ipLabel,flag=wx.LEFT,border=8)
		hbox1.Add(self.ipText,proportion=1)
		vbox.Add(hbox1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,border=10)
		vbox.Add((-1, 10))
		hbox2.Add(portLabel,flag=wx.LEFT,border=8)
		hbox2.Add(self.portText,proportion=1)		
		vbox.Add(hbox2,flag=wx.EXPAND|wx.LEFT|wx.RIGHT,border=10)
		vbox.Add((-1, 10))
		hbox3.Add(catalogLabel,flag=wx.LEFT,border=8)
		hbox3.Add(self.catalogText,proportion=1)		
		vbox.Add(hbox3,flag=wx.EXPAND|wx.LEFT|wx.RIGHT,border=10)
		vbox.Add((-1, 50))
		hbox4.Add(button1,flag=wx.LEFT,border=18)
		hbox4.Add(button2,flag=wx.ALIGN_LEFT|wx.LEFT,border=8)
		vbox.Add(hbox4,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.Bottom,border=10)
		panel.SetSizer(vbox)
		self.loadConf() #加载配置文件，显示在界面
	def loadConf(self):
		fh=open('server.conf')
		size=len(fh.read())
		fh.seek(0)
		while(fh.tell()!=size):
			data=fh.readline()
			if(data[:4] == 'addr'): 
				host=data[5:].strip()#ip or domain,include port
			elif(data[:7]=='catalog'):
				self.catalogText.SetValue(data[8:].strip())
						
		fh.close()
		splits=host.split(':')
		host=splits[0]
		port=splits[1]
		self.ipText.SetValue(host)
		self.portText.SetValue(port)
	def OnSaveConf(self,event):		
		host=self.ipText.GetValue()
		port=self.portText.GetValue()
		catalog=self.catalogText.GetValue()
		fh=open('server.conf','w')
		fh.write('#pageSlimer server configuration\n#addr=(ip/domain):(port)\n')
		fh.write('addr=%s:%s'%(host,port))#will not write \n to the end
		fh.write('\ncatalog=%s'%catalog)
		fh.write('\nid=%s'%self.user)
		fh.write('\npw=%s'%self.pw)
		fh.close()
		self.Destroy()
	def OnCancel(self,event):
		self.Destroy()
		#self.Hide()
		#pass
		
def TestFrame():
	app = wx.App() #wx.PySimpleApp()
	frame = MainFrame(size=(776, 480))  #640,480 #1.618:1

	frame.Centre()
	frame.Show() #可以让它设置是否在程序启动时一起显示出来
	#frame.OnHide(wx.Frame)  #让它启动时隐藏
	app.MainLoop()
if __name__ == '__main__':
#src=urllib2.urlopen('http://127.0.0.1:1366/doslim?url=http://www.linuxfan.com:1366/program/pageSlimer/linux-usage.html&dir=default&name=default')
#		text=src.read()
#		src.close()
#		print 'text:',text[0:40]
		TestFrame()
