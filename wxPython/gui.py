# -*- coding: utf-8 -*-
#!/bin/python

import wx

#自定义dialog，显示n秒后消失，简单方式可以dlg = MessageDialog('Closing this dialog box in 2s...', 'Info')        
            #wx.FutureCall(2000, dlg.Destroy) #2秒后调用执行第二个参数
            #dlg.ShowModal()
class MsgDialog(wx.Dialog):
    def __init__(self, message, title, ttl=10):
        wx.Dialog.__init__(self, None, -1, title,size=(300, 150))
        self.CenterOnScreen(wx.BOTH)
        self.timeToLive = ttl

        stdBtnSizer = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL) 
        stMsg = wx.StaticText(self, -1, message)
        self.stTTLmsg = wx.StaticText(self, -1, '%ds后消失'%self.timeToLive)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(stMsg, 1, wx.ALIGN_CENTER|wx.TOP, 10)
        vbox.Add(self.stTTLmsg,1, wx.ALIGN_CENTER|wx.TOP, 10)
        vbox.Add(stdBtnSizer,1, wx.ALIGN_CENTER|wx.TOP, 10)
        self.SetSizer(vbox)

        self.timer = wx.Timer(self)
        self.timer.Start(1000)#Generate a timer event every second
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

    def onTimer(self, evt):
        self.timeToLive -= 1
        self.stTTLmsg.SetLabel('%ds后消失'%self.timeToLive)
        if self.timeToLive == 0:
            self.timer.Stop()
            self.Destroy()

