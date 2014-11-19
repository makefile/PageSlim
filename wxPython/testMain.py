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
socket.setdefaulttimeout(10) #global
reload(sys) 
sys.setdefaultencoding('utf-8')
#如果不设置编码，则unicode等问题较麻烦,in windows,just use u'xxx'
class Frame(wx.Frame):
	def __init__(
			self, parent=None, id=wx.ID_ANY, title='网文快存', pos=wx.DefaultPosition,
			size=wx.DEFAULT, style=wx.DEFAULT_FRAME_STYLE):
		
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
		self.urlText = wx.TextCtrl(panel, -1, "http://www.linuxfan.com:1366/program/pageSlimer/linux-usage.html",size=(250, 38), style=wx.TE_MULTILINE)  #创建一个文本控件
		titleLabel = wx.StaticText(panel, -1, "标题:") 
		titleLabel.SetForegroundColour('blue') 
		self.titleText = wx.TextCtrl(panel, -1, "",size=(200, 30))
		self.titleText.SetInsertionPoint(0)
		self.urlText.SetInsertionPoint(0)#设置插入点
		catalogLabel = wx.StaticText(panel, -1, "归档目录:") 
		catalogLabel.SetForegroundColour('blue') 
		self.catalogText = wx.TextCtrl(panel, -1, "default",size=(200, 30))
		richTextLabel = wx.StaticText(panel, -1, "正文(可编辑):")
		self.richText = wx.TextCtrl(panel, -1, "\n\n\n\n\t\t\t\t\t\t\t\t\t^_^",style=wx.TE_MULTILINE|wx.TE_RICH2) #创建丰富文本控件
		self.richText.SetInsertionPoint(0)  
		self.richText.SetForegroundColour('blue')
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
		self.host=''
		self.filename=''
		self.readConfigure()
	def OnHide(self, event):
		self.Hide()
	def OnGet(self, event):
		url=self.urlText.GetValue().strip()
		if(url==''):
			wx.MessageBox('您还没输入网址','^0^')
			return
		try:
			src=urllib.urlopen('http://'+self.host+'/doslim?url='+url+'&dir=default&name=default')
#so strange that the urllib2.urlopen not work properly at times,is it beacause the server i write has problem of sending packet headers?
			text=src.read()
			src.close()
			print 'text:',text[0:40]
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
			self.richText.SetValue(text.strip())
		except Exception,e:
			print e
			wx.MessageBox('请检查您的网络', '网络连接出错')
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
		boundary='---------%s'%hex(int(time.time()*1000))
		data=[] #a list
#	data.append('\r\n')
		data.append('--%s'%boundary)
		data.append('dir=default')#= not : in my server
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
		fh.close()
		self.Destroy()
	def OnCancel(self,event):
		self.Destroy()
		#self.Hide()
		#pass
		
def TestFrame():
	app = wx.PySimpleApp()
	frame = Frame(size=(776, 480))  #640,480 #1.618:1

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
