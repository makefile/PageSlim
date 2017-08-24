 # -*- encoding:utf-8 -*-  
'''''tuofang example'''  
  
import wx  
  
class MyApp(wx.App):  
  
    pass  
  
class FileDropTarget(wx.FileDropTarget):  
    def __init__(self, window):  
          wx.FileDropTarget.__init__(self)  
          self.window = window  
  
    def OnDropFiles(self,  x,  y, fileNames):  
          self.window.SetValue(str(fileNames))  
  
class MyFrame(wx.Frame):  
  
    def __init__(self, parent, id):  
  
        wx.Frame.__init__(self, parent, id, title = u'拖放例子', size = (778,494))  
        panel=wx.Panel(self)  
        textBox=wx.TextCtrl(panel, pos = (50, 50),size =(300, 200))  
        dropTarget = FileDropTarget(textBox)  
        textBox.SetDropTarget( dropTarget )  
  
if __name__=='__main__':  
    app=MyApp()  
    frame=MyFrame(parent=None,id=-1)  
    frame.Show(True)  
    app.MainLoop()  
