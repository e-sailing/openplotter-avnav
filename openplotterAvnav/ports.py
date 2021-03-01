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
import os, subprocess, sys
import lxml.etree as et
from openplotterSettings import language

class Ports:
	def __init__(self,conf,currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-avnav',currentLanguage)
		self.connections = []

		command = 'systemctl show avnav --no-page'
		output = subprocess.check_output(command.split(),universal_newlines=True)
		if 'SubState=running' in output: self.avnav= True
		else: self.avnav= False

	def usedPorts(self):
		usedPorts = []
		if self.avnav:
			avnavPort = 8080
			oesencPort = 8082
			updatePort = 8085
			tosignalkPort = 28628
			try:
				xmlDocFile = self.conf.home +'/avnav/data/avnav_server.xml'
				xmlload = False
				if os.path.exists(xmlDocFile):
					xmlDoc = et.ElementTree(file=xmlDocFile)
					xmlload = True

					AVNHttpS = xmlDoc.find('.//AVNHttpServer')
					if AVNHttpS!=None:
						if 'httpPort' in AVNHttpS.attrib:
							avnavPort = int(AVNHttpS.attrib['httpPort'] or 8080)
							
					sys_ocharts = xmlDoc.find('.//system-ocharts')
					if sys_ocharts!=None:
						if 'port' in sys_ocharts.attrib:
							oesencPort = int(sys_ocharts.attrib['port'] or 8082)

					AVNSocketWriter = xmlDoc.find('.//AVNSocketWriter')
					if AVNSocketWriter!=None:
						if 'port' in AVNSocketWriter.attrib:
							tosignalkPort = int(AVNSocketWriter.attrib['port'] or 28628)
			except Exception as e: print(str(e))

			try:							
				output = subprocess.check_output(['grep','-F','Environment=PORT=','/etc/systemd/system/avnavupdater.service.d/override.conf']).decode("utf-8").split('=')
				if len(output) == 3:
					updatePort = int(output[2])
			except Exception as e: print(str(e))

			usedPorts.append({'id':'avnav1', 'description':_('Avnav web interface'), 'data':'', 'direction':'3', 'type':'TCP', 'mode':'server', 'address':'localhost', 'port':str(avnavPort), 'editable':'1'})
			usedPorts.append({'id':'avnav2', 'description':_('osOENC chart plugin'), 'data':'', 'direction':'3', 'type':'TCP', 'mode':'server', 'address':'localhost', 'port':str(oesencPort), 'editable':'1'})
			usedPorts.append({'id':'avnav3', 'description':_('Avnav updater'), 'data':'', 'direction':'3', 'type':'TCP', 'mode':'server', 'address':'localhost', 'port':str(updatePort), 'editable':'1'})
			usedPorts.append({'id':'avnav4', 'description':_('Avnav to Signal K'), 'data':'', 'direction':'3', 'type':'TCP', 'mode':'server', 'address':'localhost', 'port':str(tosignalkPort), 'editable':'1'})

		return usedPorts