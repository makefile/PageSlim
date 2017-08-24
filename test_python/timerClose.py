import wx
import os

class MessageDialog(wx.Dialog):
    def __init__(self, message, title, ttl=10):
        wx.Dialog.__init__(self, None, -1, title,size=(400, 150))
        self.CenterOnScreen(wx.BOTH)
        self.timeToLive = ttl

        stdBtnSizer = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL) 
        stMsg = wx.StaticText(self, -1, message)
        self.stTTLmsg = wx.StaticText(self, -1, 'Closing this dialog box in %ds...'%self.timeToLive)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(stMsg, 1, wx.ALIGN_CENTER|wx.TOP, 10)
        vbox.Add(self.stTTLmsg,1, wx.ALIGN_CENTER|wx.TOP, 10)
        vbox.Add(stdBtnSizer,1, wx.ALIGN_CENTER|wx.TOP, 10)
        self.SetSizer(vbox)

        self.timer = wx.Timer(self)
        self.timer.Start(1000)#Generate a timer event every second
        self.timeToLive = 10 
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

    def onTimer(self, evt):
        self.timeToLive -= 1
        self.stTTLmsg.SetLabel('Closing this dialog box in %ds...'%self.timeToLive)

        if self.timeToLive == 0:
            self.timer.Stop()
            self.Destroy()

class Frame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(100, 100),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        host=os.system('hostname')
        if host!='superman':
            dlg = MessageDialog('The host name should be superman', 'Info', ttl=10)               
            dlg.ShowModal()
        else:
            self.Center()
            self.Show()

if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = Frame(None, -1, "") 
    frame.Show(1)
    app.MainLoop()
