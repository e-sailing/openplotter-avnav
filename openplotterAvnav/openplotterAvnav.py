#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2020 by Sailoog <https://github.com/openplotter/openplotter-sdr-vhf>
# Copyright (C) 2020 by e-sailing <https://github.com/e-sailing/openplotter-sdr-vhf>
#
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import wx, os, sys, webbrowser, subprocess, time
import wx.richtext as rt
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from openplotterSignalkInstaller import editSettings
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr':
	from .version import version
else:
	import version

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(650, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-avnav',self.currentLanguage)

		if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr': 
			v = version
		else: v = version.version

		wx.Frame.__init__(self, None, title='Avnav'+' '+v, size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/sailboat24r.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		if not self.platform.isInstalled('openplotter-doc'): self.toolbar1.EnableTool(101,False)
		toolSettings = self.toolbar1.AddTool(106, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		toolAvnav = self.toolbar1.AddTool(110, 'Avnan', wx.Bitmap(self.currentdir+"/data/sailboat24r.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolAvnav, toolAvnav)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.apps = wx.Panel(self.notebook)
		self.systemd = wx.Panel(self.notebook)		
		#self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.systemd, _('Processes'))
		#self.notebook.AddPage(self.output, '')
		self.il = wx.ImageList(24, 24)
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/process.png", wx.BITMAP_TYPE_PNG))
		#img2 = self.il.Add(wx.Bitmap(self.currentdir+"/data/output.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img1)
		#self.notebook.SetPageImage(1, img2)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.appsDict = []
		
		app = {
		'name': 'Avnav',
		'included': True,
		'show': '',
		'service': ['avnav'],
		'edit': True,
		'install': '',
		'uninstall': '',
		}
		self.appsDict.append(app)

		self.pageSystemd()
		#self.pageOutput()

		maxi = self.conf.get('GENERAL', 'maximize')
		if maxi == '1': self.Maximize()
		
		self.Centre()
		

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0))

	def onTabChange(self, event):
		try:
			self.SetStatusText('')
		except:pass

	def OnToolHelp(self, event): 
		url = "/usr/lib/python3/dist-packages/openplotterAvnav/data/help.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event=0): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def OnToolAvnav(self, event):
		url = "http://localhost:8080"
		webbrowser.open(url, new=2)

################################################################################

	def pageSystemd(self):
		self.started = False
		self.aStatusList = [_('inactive'),_('active')]
		self.bStatusList = [_('dead'),_('running')] 

		self.listSystemd = CheckListCtrl(self.systemd, 152)
		self.listSystemd.InsertColumn(0, _('Autostart'), width=90)
		self.listSystemd.InsertColumn(1, _('App'), width=90)
		self.listSystemd.InsertColumn(2, _('Process'), width=140)
		self.listSystemd.InsertColumn(3, _('Status'), width=120)
		self.listSystemd.InsertColumn(4, '  ', width=100)
		self.listSystemd.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSystemdSelected)
		self.listSystemd.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListSystemdDeselected)
		self.listSystemd.SetTextColour(wx.BLACK)

		self.listSystemd.OnCheckItem = self.OnCheckItem

		self.toolbar3 = wx.ToolBar(self.systemd, style=wx.TB_TEXT | wx.TB_VERTICAL)
		start = self.toolbar3.AddTool(301, _('Start'), wx.Bitmap(self.currentdir+"/data/start.png"))
		self.Bind(wx.EVT_TOOL, self.onStart, start)
		stop = self.toolbar3.AddTool(302, _('Stop'), wx.Bitmap(self.currentdir+"/data/stop.png"))
		self.Bind(wx.EVT_TOOL, self.onStop, stop)
		restart = self.toolbar3.AddTool(303, _('Restart'), wx.Bitmap(self.currentdir+"/data/restart.png"))
		self.Bind(wx.EVT_TOOL, self.onRestart, restart)	

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.listSystemd, 1, wx.EXPAND, 0)
		sizer.Add(self.toolbar3, 0)

		self.systemd.SetSizer(sizer)

		self.set_listSystemd()
		self.started = True

	def onListSystemdSelected(self, e):
		i = e.GetIndex()
		valid = e and i >= 0
		if not valid: return
		self.toolbar3.EnableTool(301,True)
		self.toolbar3.EnableTool(302,True)
		self.toolbar3.EnableTool(303,True)

	def onListSystemdDeselected(self, event=0):
		self.toolbar3.EnableTool(301,False)
		self.toolbar3.EnableTool(302,False)
		self.toolbar3.EnableTool(303,False)

	def OnRefreshButton(self, event=0):
		self.listSystemd.DeleteAllItems()
		self.started = False
		self.set_listSystemd()
		self.started = True

	def set_listSystemd(self):
		apps = list(reversed(self.appsDict))
		for i in apps:
			if i['service']:
				for ii in i['service']:
					index = self.listSystemd.InsertItem(sys.maxsize, '')
					self.listSystemd.SetItem(index, 1, i['name'])
					self.listSystemd.SetItem(index, 2, ii)
					command = 'systemctl show '+ii+' --no-page'
					output = subprocess.check_output(command.split(),universal_newlines=True)
				if 'UnitFileState=enabled' in output: self.listSystemd.CheckItem(index)
		self.statusUpdate()

	def statusUpdate(self):
		listCount = range(self.listSystemd.GetItemCount())
		for i in listCount:
			service = self.listSystemd.GetItemText(i, 2)
			command = 'systemctl show '+service+' --no-page'
			output = subprocess.check_output(command.split(),universal_newlines=True)
			if 'ActiveState=active' in output: self.listSystemd.SetItem(i, 3, _('active'))
			else: self.listSystemd.SetItem(i, 3, _('inactive'))
			if 'SubState=running' in output: 
				self.listSystemd.SetItem(i, 4, _('running'))
				self.listSystemd.SetItemBackgroundColour(i,(0,255,0))
			else: 
				self.listSystemd.SetItem(i, 4, _('dead'))
				self.listSystemd.SetItemBackgroundColour(i,(-1,-1,-1))

						
	def onStart(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		self.ShowStatusBarYELLOW(_('Starting process...'))
		subprocess.call((self.platform.admin + ' systemctl start ' + self.listSystemd.GetItemText(index, 2)).split())
		time.sleep(1)
		self.OnRefreshButton()
		self.ShowStatusBarGREEN(_('Done'))

	def onStop(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		self.ShowStatusBarYELLOW(_('Stopping process...'))
		subprocess.call((self.platform.admin + ' systemctl stop ' + self.listSystemd.GetItemText(index, 2)).split())
		time.sleep(1)
		self.OnRefreshButton()
		self.ShowStatusBarGREEN(_('Done'))

	def onRestart(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		self.ShowStatusBarYELLOW(_('Restarting process...'))
		subprocess.call((self.platform.admin + ' systemctl restart ' + self.listSystemd.GetItemText(index, 2)).split())
		time.sleep(1)
		self.OnRefreshButton()
		self.ShowStatusBarGREEN(_('Done'))
		
	def OnCheckItem(self, index, flag):
		if not self.started: return
		self.ShowStatusBarYELLOW(_('Enabling/Disabling process...'))
		if flag:
			subprocess.call((self.platform.admin + ' systemctl enable ' + self.listSystemd.GetItemText(index, 2)).split())
		else:
			subprocess.call((self.platform.admin + ' systemctl disable ' + self.listSystemd.GetItemText(index, 2)).split())
		self.OnRefreshButton()
		self.ShowStatusBarGREEN(_('Done'))

################################################################################

	def pageOutput(self):
		self.logger = rt.RichTextCtrl(self.output, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger.SetMargins((10,10))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.logger, 1, wx.EXPAND, 0)
		self.output.SetSizer(sizer)

def main():
	try:
		platform2 = platform.Platform()
		if not platform2.postInstall(version,'avnav'): 
			subprocess.Popen(['openplotterPostInstall', platform2.admin+' avPostInstall'])
			return
	except: pass

	app = wx.App()
	MyFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
