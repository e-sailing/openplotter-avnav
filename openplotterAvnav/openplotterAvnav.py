#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2020 by Sailoog <https://github.com/openplotter/openplotter-avnav>
# Copyright (C) 2020 by e-sailing <https://github.com/e-sailing/openplotter-avnav>
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
#from xml.etree import ElementTree as et
import lxml.etree as et
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
		toolSettings = self.toolbar1.AddTool(102, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		toolAvnav = self.toolbar1.AddTool(110, 'Avnav', wx.Bitmap(self.currentdir+"/data/sailboat24r.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolAvnav, toolAvnav)
		toolAvnavSplit = self.toolbar1.AddTool(111, 'Avnav split', wx.Bitmap(self.currentdir+"/data/sailboath24rs.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolAvnavSplit, toolAvnavSplit)
		self.toolbar1.AddSeparator()
		toolApply = self.toolbar1.AddTool(105, _('Apply Changes'), wx.Bitmap(self.currentdir+"/data/apply.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolApply, toolApply)
		toolCancel = self.toolbar1.AddTool(106, _('Cancel Changes'), wx.Bitmap(self.currentdir+"/data/cancel.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolCancel, toolCancel)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.apps = wx.Panel(self.notebook)
		self.settings = wx.Panel(self.notebook)
		self.systemd = wx.Panel(self.notebook)
		#self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.settings, _('Settings'))
		self.notebook.AddPage(self.systemd, _('Processes'))
		#self.notebook.AddPage(self.output, '')
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/settings2.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/process.png", wx.BITMAP_TYPE_PNG))
		#img2 = self.il.Add(wx.Bitmap(self.currentdir+"/data/output.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)
		#self.notebook.SetPageImage(1, img2)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.appsDict = []
		
		app = {
		'name': 'AvnavUpdater',
		'included': True,
		'show': '',
		'service': ['avnavupdater'],
		'edit': True,
		'install': '',
		'uninstall': '',
		}
		self.appsDict.append(app)		
		
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
		
		self.OCHARTSport = 8082
		self.AVNport = 8080
		self.updatePort = 8085
		self.xmlDocFile = self.conf.home +'/avnav/data/avnav_server.xml'
		self.xmlload = False
		if os.path.exists(self.xmlDocFile):
			self.xmlDoc = et.ElementTree(file=self.xmlDocFile)
			self.xmlload = True

			AVNHttpS = self.xmlDoc.find('.//AVNHttpServer')
			if AVNHttpS!=None:
				if 'httpPort' in AVNHttpS.attrib:
					try:
						self.AVNport = int(AVNHttpS.attrib['httpPort'] or 8080)
					except: pass
			sys_ocharts = self.xmlDoc.find('.//system-ocharts')
			if sys_ocharts!=None:
				if 'port' in sys_ocharts.attrib:
					try:
						self.OCHARTSport = int(sys_ocharts.attrib['port'] or 8082)
					except: pass
			output = subprocess.check_output(['grep','-F','Environment=PORT=','/etc/systemd/system/avnavupdater.service.d/override.conf']).decode("utf-8").split('=')
			if len(output) == 3:
				try:
					self.updatePort = int(output[2])
				except: pass

		
		self.pageSettings()
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
		url = "http://localhost:"+str(self.AVNport)
		webbrowser.open(url, new=2)

	def OnToolAvnavSplit(self, event):
		url = "http://localhost:"+str(self.AVNport)+"/viewer/viewer_split.html"
		webbrowser.open(url, new=2)

	def OnToolApply(self,e):
		if not self.xmlload:
			self.ShowStatusBarRED(_('There is no configuration file. Please restart start avnav process.'))
			return
        
		msg = _('Only port settings will be changed. Are you sure?')
		dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
		if dlg.ShowModal() == wx.ID_YES:
			self.AVNport = str(self.port.GetValue())
			self.OCHARTSport = str(self.port_ocharts.GetValue())
			self.updatePort = str(self.port_update.GetValue())

			self.xmlDoc.find('.//AVNHttpServer').attrib['httpPort'] = self.AVNport
			if self.xmlDoc.find('.//AVNPluginHandler') == None:
				a=et.fromstring('<AVNPluginHandler/>')
				self.xmlDoc.getroot().append(a)
				
			a = self.xmlDoc.find('.//AVNPluginHandler')
			if a.find('.//system-ocharts') == None:
				b=et.fromstring('<system-ocharts/>')
				a.append(b)
				
			b = a.find('.//system-ocharts')
			b.attrib['port'] = self.OCHARTSport

			self.ShowStatusBarYELLOW(_('Configuring AVNAV port, please wait... '))

			self.xmlDoc.write(self.xmlDocFile)
			#change avahi
            #subprocess.call(self.platform.admin + ' python3 '+self.currentdir+'/changeAvahiPort.py ' + self.AVNport, shell=True)
			#change menu
			output = subprocess.check_output(['grep','-F','Exec=','/usr/share/applications/avnav.desktop']).decode("utf-8")
			subprocess.call(self.platform.admin + ' sed -i "s#'+output[0:-1]+'#Exec=x-www-browser http://localhost:'+self.AVNport+'#g" /usr/share/applications/avnav.desktop', shell=True)
			#change avnav-updater
			output = subprocess.check_output(['grep','-F','Environment=PORT=','/etc/systemd/system/avnavupdater.service.d/override.conf']).decode("utf-8")
			subprocess.call(self.platform.admin + ' sed -i "s|'+output[0:-1]+'|Environment=PORT='+self.updatePort+'|g" /etc/systemd/system/avnavupdater.service.d/override.conf', shell=True)
			
			listCount = range(self.listSystemd.GetItemCount())
			for i in listCount:
				self.onRestart(i)
			time.sleep(2)
			self.refreshSettings()
			self.ShowStatusBarYELLOW('')
		dlg.Destroy()

	def OnToolCancel(self,e):
		self.refreshSettings()


################################################################################

	def pageSettings(self):
		portLabel = wx.StaticText(self.settings, label=_('Port'))
		self.port = wx.SpinCtrl(self.settings, 101, min=80, max=65536, initial=self.AVNport)
		self.port.Bind(wx.EVT_SPINCTRL, self.onPort)
		portText1 = wx.StaticText(self.settings, label=_('The AVNAV default port is 8080'))
		portText2 = wx.StaticText(self.settings, label=_('Port 80 does not require ":8080" in browsers and app interfaces'))

		portLabel2 = wx.StaticText(self.settings, label=_('Port'))
		self.port_ocharts = wx.SpinCtrl(self.settings, 101, min=80, max=65536, initial=self.OCHARTSport)
		self.port_ocharts.Bind(wx.EVT_SPINCTRL, self.onPort_ocharts)
		portText3 = wx.StaticText(self.settings, label=_('The AVNAV ocharts plugin default port is 8082'))

		portLabel3 = wx.StaticText(self.settings, label=_('Port'))
		self.port_update = wx.SpinCtrl(self.settings, 101, min=80, max=65536, initial=self.updatePort)
		self.port_update.Bind(wx.EVT_SPINCTRL, self.onPort_update)
		portText4 = wx.StaticText(self.settings, label=_('The AVNAV update plugin default port is 8085'))

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(portLabel, 0, wx.UP | wx.EXPAND, 5)
		hbox.Add(self.port, 0, wx.LEFT | wx.EXPAND, 10)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(portLabel2, 0, wx.UP | wx.EXPAND, 5)
		hbox2.Add(self.port_ocharts, 0, wx.LEFT | wx.EXPAND, 10)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(portLabel3, 0, wx.UP | wx.EXPAND, 5)
		hbox3.Add(self.port_update, 0, wx.LEFT | wx.EXPAND, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(20)
		vbox.Add(hbox, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(5)
		vbox.Add(portText1, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(5)
		vbox.Add(portText2, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(20)
		vbox.Add(hbox2, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(5)
		vbox.Add(portText3, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(20)
		vbox.Add(hbox3, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(5)
		vbox.Add(portText4, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddStretchSpacer(1)

		self.settings.SetSizer(vbox)

		self.refreshSettings()

	def refreshSettings(self):
		self.platform = platform.Platform()
		self.notebook.ChangeSelection(1)
		#if self.platform.skPort: self.port.SetValue(int(self.platform.skPort))
		self.toolbar1.EnableTool(105,False)
		self.toolbar1.EnableTool(106,False)

	def restart_SK(self, msg):
		if msg == 0: msg = _('Restarting AVNAV... ')
		seconds = 12
		for i in range(seconds, 0, -1):
			self.ShowStatusBarYELLOW(msg+str(i))
			time.sleep(1)
		self.ShowStatusBarGREEN(_('AVNAV server restarted'))

	def onPort(self, e):
		self.toolbar1.EnableTool(105,True)
		self.toolbar1.EnableTool(106,True)

	def onPort_ocharts(self, e):
		self.toolbar1.EnableTool(105,True)
		self.toolbar1.EnableTool(106,True)

	def onPort_update(self, e):
		self.toolbar1.EnableTool(105,True)
		self.toolbar1.EnableTool(106,True)

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
		self.onListSystemdDeselected()
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
