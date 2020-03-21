#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2020 by Sailoog <https://github.com/openplotter>
#                     e-sailing <https://github.com/e-sailing/openplotter-avnav>
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

import wx, os, webbrowser, subprocess, sys, time
import wx.richtext as rt

from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from openplotterSignalkInstaller import editSettings

if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr':
	from .version import version
else:
	import version

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-avnav',currentLanguage)

		self.appsDict = []

		if self.platform.skPort:
			install = self.platform.admin+' python3 '+self.currentdir+'/installAvnav.py'
			uninstall = self.platform.admin+' python3 '+self.currentdir+'/uninstallAvnav.py'			
		self.avnavFoundUpdate()

		show = ''
		edit = ''

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
		toolSettings = self.toolbar1.AddTool(106, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		toolSources = self.toolbar1.AddTool(103, _('Add Sources'), wx.Bitmap(self.currentdir+"/data/sources.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSources, toolSources)
		if os.path.exists('/etc/apt/sources.list.d/open-mind.list'): self.toolbar1.EnableTool(103,False)
		self.refreshButton = self.toolbar1.AddTool(104, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
		self.Bind(wx.EVT_TOOL, self.OnRefreshButton, self.refreshButton)
		self.avnavWeb = self.toolbar1.AddTool(105, _('Open Avnav'), wx.Bitmap(self.currentdir+"/data/sailboat24r.png"))
		self.Bind(wx.EVT_TOOL, self.OnAvnav, self.avnavWeb)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.apps = wx.Panel(self.notebook)
		self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.apps, _('Apps'))
		self.notebook.AddPage(self.output, '')
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/sailboat24r.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/output.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.pageApps()
		self.pageOutput()

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
		
	def OnToolSources(self, e):
		self.ShowStatusBarYELLOW(_('Adding packages sources, please wait... '))
		self.logger.Clear()
		self.notebook.ChangeSelection(1)
		command = self.platform.admin+' settingsAVSourcesInstall'
		popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
		for line in popen.stdout:
			if not 'Warning' in line and not 'WARNING' in line:
				self.logger.WriteText(line)
				self.ShowStatusBarYELLOW(_('Adding packages sources, please wait... ')+line)
				self.logger.ShowPosition(self.logger.GetLastPosition())
		self.ShowStatusBarGREEN(_('Added sources.'))
		if os.path.exists('/etc/apt/sources.list.d/open-mind.list'): self.toolbar1.EnableTool(103,False)		
		self.avnavFoundUpdate()
		self.OnRefreshButton()		

	def avnavFoundUpdate(self): 
		command = 'apt-cache search avnav'
		output = subprocess.check_output(command.split(),universal_newlines=True)

		edit = ''
		install = ''
		uninstall = ''
		if self.platform.skPort:
			install = self.platform.admin+' python3 '+self.currentdir+'/installAvnav.py'
			uninstall = self.platform.admin+' python3 '+self.currentdir+'/uninstallAvnav.py'				

		if 'avnav - avnav' in output:
			self.appsDict = []
			app = {
			'name': 'Avnav',
			'show': "http://localhost:8080",
			'edit': edit,
			'included': 'no',
			'plugin': '',
			'install': install,
			'uninstall': uninstall,
			'settings': 'http://localhost:8080',
			}			
			self.appsDict.append(app)

	def OnAvnav(self,e):
		if self.platform.skPort: 
			url = self.platform.http+'localhost:8080'
			webbrowser.open(url, new=2)
		else: 
			self.ShowStatusBarRED(_('Please install "Signal K Installer" OpenPlotter app'))
			self.OnToolSettings()

	def pageApps(self):
		self.listApps = wx.ListCtrl(self.apps, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.listApps.InsertColumn(0, _('Name'), width=320)
		self.listApps.InsertColumn(1, _('status'), width=365)
		self.listApps.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListAppsSelected)
		self.listApps.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListAppsDeselected)

		self.toolbar2 = wx.ToolBar(self.apps, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.settingsButton = self.toolbar2.AddTool(204, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings2.png"))
		self.Bind(wx.EVT_TOOL, self.OnSettingsButton, self.settingsButton)
		self.showButton = self.toolbar2.AddTool(202, _('Show'), wx.Bitmap(self.currentdir+"/data/show.png"))
		self.Bind(wx.EVT_TOOL, self.OnShowButton, self.showButton)
		self.toolbar2.AddSeparator()
		toolInstall= self.toolbar2.AddTool(203, _('Install'), wx.Bitmap(self.currentdir+"/data/install.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolInstall, toolInstall)
		toolUninstall= self.toolbar2.AddTool(205, _('Uninstall'), wx.Bitmap(self.currentdir+"/data/uninstall.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolUninstall, toolUninstall)

		self.toolbar3 = wx.ToolBar(self.apps, style=wx.TB_TEXT | wx.TB_VERTICAL)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.listApps, 1, wx.EXPAND, 0)
		sizer.Add(self.toolbar2, 0)
		self.apps.SetSizer(sizer)

		self.OnRefreshButton()

	def OnRefreshButton(self, event=0):
		self.avnavFoundUpdate()
		self.notebook.ChangeSelection(0)
		self.listApps.DeleteAllItems()
		for i in self.appsDict:
			item = self.listApps.InsertItem(0, i['name'])
			if self.platform.isInstalled((i['name']).lower()):
				self.listApps.SetItem(item, 1, _('installed'))
			else:
				self.listApps.SetItem(item, 1, _('not installed'))
				self.listApps.SetItemBackgroundColour(item,(200,200,200))
		self.onListAppsDeselected()

	def OnToolInstall(self, e):
		if self.platform.skPort:
			index = self.listApps.GetFirstSelected()
			if index == -1: return
			apps = list(reversed(self.appsDict))
			name = apps[index]['name']
			command = apps[index]['install']
			if not command:
				self.ShowStatusBarRED(_('This app can not be installed'))
				return
			msg = _('Are you sure you want to install ')+name+_(' and its dependencies?')
			dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
			if dlg.ShowModal() == wx.ID_YES:
				self.logger.Clear()
				self.notebook.ChangeSelection(1)
				popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
				for line in popen.stdout:
					if not 'Warning' in line and not 'WARNING' in line:
						self.logger.WriteText(line)
						self.ShowStatusBarYELLOW(_('Installing Avnav, please wait... ')+line)
						self.logger.ShowPosition(self.logger.GetLastPosition())
				self.OnRefreshButton()
				#self.restart_SK(0)
			dlg.Destroy()
			self.goodEnd(self.platform.isInstalled(name.lower()))
		else: 
			self.ShowStatusBarRED(_('Please install "Signal K Installer" OpenPlotter app'))
			self.OnToolSettings()

	def OnToolUninstall(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		apps = list(reversed(self.appsDict))
		name = apps[index]['name']
		command = apps[index]['uninstall']
		if not command:
			self.ShowStatusBarRED(_('This app can not be uninstalled'))
			return
		msg = _('Are you sure you want to uninstall ')+name+_(' and its dependencies?')
		dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
		if dlg.ShowModal() == wx.ID_YES:
			self.logger.Clear()
			self.notebook.ChangeSelection(1)
			popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
			for line in popen.stdout:
				if not 'Warning' in line and not 'WARNING' in line:
					self.logger.WriteText(line)
					self.ShowStatusBarYELLOW(_('Uninstalling Avnav, please wait... ')+line)
					self.logger.ShowPosition(self.logger.GetLastPosition())
			self.OnRefreshButton()
		dlg.Destroy()
		self.goodEnd(not self.platform.isInstalled(name.lower()))

	def goodEnd(self, status):
		if status:
			self.ShowStatusBarGREEN(_('DONE'))
			wx.Sleep(1)
			self.ShowStatusBarGREEN('')

	def restart_SK(self, msg):
		if msg == 0: msg = _('Restarting Signal K server... ')
		seconds = 12
		subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'restart'])
		for i in range(seconds, 0, -1):
			self.ShowStatusBarYELLOW(msg+str(i))
			time.sleep(1)
		self.ShowStatusBarGREEN(_('Signal K server restarted'))

	def OnSettingsButton(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		dlg = ProcessSetting(self,_('Process management for') + ' ' + self.appsDict[index]['name'] )
		res = dlg.ShowModal()
		dlg.Destroy()

	def OnShowButton(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		apps = list(reversed(self.appsDict))
		webbrowser.open(apps[index]['show'], new=2)

	def pageOutput(self):
		self.logger = rt.RichTextCtrl(self.output, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger.SetMargins((10,10))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.logger, 1, wx.EXPAND, 0)
		self.output.SetSizer(sizer)

	def onListAppsSelected(self, e):
		i = e.GetIndex()
		valid = e and i >= 0
		if not valid: return
		self.onListAppsDeselected()
		if self.listApps.GetItemBackgroundColour(i) != (200,200,200):
			apps = list(reversed(self.appsDict))
			if self.platform.isInstalled((apps[i]['name']).lower()):
				self.toolbar2.EnableTool(205,True)
			else:
				self.toolbar2.EnableTool(203,True)
			if apps[i]['settings']: self.toolbar2.EnableTool(204,True)
			#if apps[i]['edit']: self.toolbar2.EnableTool(201,True)
			if apps[i]['show']: self.toolbar2.EnableTool(202,True)
		else: self.toolbar2.EnableTool(203,True)

	def onListAppsDeselected(self, event=0):
		self.toolbar2.EnableTool(203,False)
		self.toolbar2.EnableTool(205,False)
		self.toolbar2.EnableTool(204,False)
		#self.toolbar2.EnableTool(201,False)
		self.toolbar2.EnableTool(202,False)

class ProcessSetting(wx.Dialog): 

	def __init__(self, parent, title):
		self.conf = conf.Conf()
		self.parent = parent
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-avnav',currentLanguage)

		wx.Dialog.__init__(self, None, title=title, size=(400,320))
		pnl = wx.Panel(self)
		pnl.SetBackgroundColour(wx.Colour(230,230,230,255))
		icon = wx.Icon(self.currentdir+"/data/sailboat24r.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		
		self.lblList = [_('Enable'),_('Disable')]

		self.systemdbox = wx.RadioBox(pnl, label = 'Autostart', choices = self.lblList, majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
		self.systemdbox.Bind(wx.EVT_RADIOBOX,self.onSystemdBox)

		self.skbox = wx.RadioBox(pnl, label = 'Avnav -> SignalK', choices = self.lblList, majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
		self.skbox.Bind(wx.EVT_RADIOBOX,self.onSkBox)

		sbox0 = wx.BoxSizer(wx.VERTICAL)
		sbox0.Add(self.systemdbox, 0, wx.ALL, 5)
		sbox0.Add(self.skbox, 0, wx.ALL, 5)

		sbox = wx.StaticBox(pnl, -1, _('Status'))

		self.aStatusList = [_('active'),_('inactive')]
		self.aStatusbox = wx.RadioBox(pnl, label = _('ActiveState'), choices = self.aStatusList, majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
		self.aStatusbox.Enable(False)

		self.bStatusList = [_('running'),_('dead')] 
		self.bStatusbox = wx.RadioBox(pnl, label = _('Substate'), choices = self.bStatusList, majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
		self.bStatusbox.Enable(False)

		sbox1 = wx.StaticBoxSizer(sbox, wx.VERTICAL)
		sbox1.Add(self.aStatusbox, 0, wx.ALL, 5)
		sbox1.Add(self.bStatusbox, 0, wx.ALL, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(sbox0, 1, wx.ALL, 5)
		hbox.AddStretchSpacer(1)
		hbox.Add(sbox1, 1, wx.ALL, 5)

		self.start = wx.Button(pnl, label=_('Start'))
		self.start.Bind(wx.EVT_BUTTON, self.onStart)
		self.stop = wx.Button(pnl, label=_('Stop'))
		self.stop.Bind(wx.EVT_BUTTON, self.onStop)
		self.restart = wx.Button(pnl, label=_('Restart'))
		self.restart.Bind(wx.EVT_BUTTON, self.onRestart)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hbox, 0, wx.ALL, 0)
		vbox.AddStretchSpacer(1)
		vbox.Add(self.start, 0, wx.LEFT | wx.BOTTOM, 5)
		vbox.Add(self.stop, 0, wx.ALL, 5)
		vbox.Add(self.restart, 0, wx.ALL, 5)
		pnl.SetSizer(vbox)

		self.statusUpdate()
		self.Centre() 
		self.Show(True)

	def statusUpdate(self): 
		command = 'systemctl show avnav --no-page'
		output = subprocess.check_output(command.split(),universal_newlines=True)
		if 'UnitFileState=enabled' in output:	self.systemdbox.SetSelection(0)
		else: 									self.systemdbox.SetSelection(1)
		if 'ActiveState=active' in output:		self.aStatusbox.SetSelection(0)
		else: 									self.aStatusbox.SetSelection(1)
		if 'SubState=running' in output:		self.bStatusbox.SetSelection(0)
		else: 									self.bStatusbox.SetSelection(1)
		skSettings = editSettings.EditSettings()
		if skSettings.connectionIdExists('AvnavOut'):	 self.skbox.SetSelection(0)
		else: 										 self.skbox.SetSelection(1)
		
	def onSystemdBox(self,e):
		if self.lblList[0] == self.systemdbox.GetStringSelection():
			subprocess.call(['systemctl', 'enable', 'avnav'])
		else:
			subprocess.call(['systemctl', 'stop', 'avnav'])
			subprocess.call(['systemctl', 'disable', 'avnav'])
			
	def onSkBox(self,e):
		skSettings = editSettings.EditSettings()
		if self.lblList[0] == self.skbox.GetStringSelection():
			if not skSettings.connectionIdExists('AvnavOut'):
				# 		  def setNetworkConnection(self,ID,data,networkType,host,port):
				if skSettings.setNetworkConnection('AvnavOut', 'NMEA0183', 'TCP', 'localhost', '28628'): self.parent.restart_SK(0)
				else: self.parent.ShowStatusBarRED(_('Failed. Error creating connection in Signal K'))
		else:
			if skSettings.connectionIdExists('AvnavOut'):
				if skSettings.removeConnection('AvnavOut'): self.parent.restart_SK(0)
				else: self.parent.ShowStatusBarRED(_('Failed. Error removing connection in Signal K'))
					
	def onStart(self,e):
		subprocess.call(['systemctl', 'start', 'avnav'])
		self.statusUpdate()

	def onStop(self,e):
		subprocess.call(['systemctl', 'stop', 'avnav'])
		self.statusUpdate()

	def onRestart(self,e):
		subprocess.call(['systemctl', 'restart', 'avnav'])
		self.statusUpdate()

def main():
	app = wx.App()
	MyFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
