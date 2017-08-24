import wx
class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'test frame',size=(790, 524))
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
    	'''
    	self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.clip = wx.Clipboard()
        self.x = wx.BitmapDataObject()
        self.bmp = None
	'''
    def OnClick(self, evt):
    	print 'clicked'
'''    self.clip.Open()
        self.clip.GetData(self.x)
        self.clip.Close()
        self.bmp = self.x.GetBitmap()
        self.Refresh()

    def OnPaint(self, evt):
        if self.bmp:
            dc = wx.PaintDC(self)
            dc.DrawBitmap(self.bmp, 20, 20, True)
'''
if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
