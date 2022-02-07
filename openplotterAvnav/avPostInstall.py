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

import os, sys, subprocess, time
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from .version import version
import lxml.etree as et


def addSKconnection(port,platform,id):
	if platform.skDir:
		from openplotterSignalkInstaller import editSettings
		skSettings = editSettings.EditSettings()
		ID = id
		if 'pipedProviders' in skSettings.data:
			for i in skSettings.data['pipedProviders']:
				try:
					if ID in i['id']:
						skSettings.removeConnection(i['id'])
					elif port:
						if i['pipeElements'][0]['options']['type'] == 'NMEA0183':
							if i['pipeElements'][0]['options']['subOptions']['type'] == 'udp':
								if i['pipeElements'][0]['options']['subOptions']['port'] == str(port):
									ID = i['id']
				except Exception as e:
					print(str(e))
		if ID == id:
			if port: skSettings.setNetworkConnection(ID, 'NMEA0183', 'TCP', 'localhost', str(port))


def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	package = 'openplotter-avnav'
	language.Language(currentdir, package, currentLanguage)
	platform2 = platform.Platform()

	app = {
	'name': 'Avnav',
	'platform': 'both',
	'package': package,
	'preUninstall': platform2.admin+' avPreUninstall',
	'uninstall': 'openplotter-avnav',
	'sources': ['https://www.free-x.de/deb4op'],
	'dev': 'no',
	'entryPoint': 'openplotter-avnav',
	'postInstall': platform2.admin+' avPostInstall',
	'reboot': 'no',
	'module': 'openplotterAvnav',
	'conf': 'avnav'	
	}
	#gpgKey = currentdir+'/data/myapp.gpg.key' ### replace by the path to your gpg key file. Replace contents of this file by your key.
	#sourceList = currentdir+'/data/myapp.list' ### replace by the path to your sources list file. Replace contents of this file by your packages sources.

	print(_('Check for old app in OpenPlotter...'))
	try:
		externalApps1 = []
		try:
			externalApps0 = eval(conf2.get('APPS', 'external_apps'))
		except: externalApps0 = []
		for i in externalApps0:
			if i['package'] != package: externalApps1.append(i)
		#externalApps1.append(app)
		conf2.set('APPS', 'external_apps', str(externalApps1))
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	#print(_('Checking sources...'))
	#try:
	#	sources = subprocess.check_output('apt-cache policy', shell=True).decode(sys.stdin.encoding)
	#	exists = True
	#	for i in app['sources']:
	#		if not i in sources: exists = False
	#	if not exists:
	#		os.system('cp '+sourceList+' /etc/apt/sources.list.d')
	#		os.system('apt-key add - < '+gpgKey)
	#		os.system('apt update')
	#	print(_('DONE'))
	#except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Install app...'))

	cssFile = conf2.home +'/avnav/data/user/viewer/user.css'
	cssExists = os.path.exists(cssFile)

	try:
		subprocess.call(['apt', '-y', 'install', 'avnav'])
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		subprocess.call(['apt', '-y', 'install', 'avnav-history-plugin', 'avnav-update-plugin'])
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		subprocess.call(['apt', '-y', 'install', 'avnav-mapproxy-plugin'])
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		subprocess.call(['apt', '-y', 'install', 'avnav-ocharts-plugin'])
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		subprocess.call(['apt', '-y', 'install', 'avnav-ocharts'])
	except Exception as e: print(_('FAILED: ')+str(e))

	try:
		subprocess.call(['mv', '/usr/lib/avnav/viewer/layout/default.json', '/usr/lib/avnav/viewer/layout/original_default.json'])
		subprocess.call(['cp', '-av', '/usr/lib/python3/dist-packages/openplotterAvnav/data/openplotter.json', '/usr/lib/avnav/viewer/layout'])
		subprocess.call(['cp', '-av', '/usr/lib/python3/dist-packages/openplotterAvnav/data/openplotter.json', '/usr/lib/avnav/viewer/layout/default.json'])

		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
		
	try:
	#if True:
		print(_('Editing config files...'))
		if not os.path.isdir('/usr/lib/systemd/system/avnav.service.d'):
			os.makedirs('/usr/lib/systemd/system/avnav.service.d')
		
		data = '[Unit]\n'
		data+= 'Description=Browser based navigation (chart plotter)\n'
		data+= 'After=syslog.target network.target\n\n'
		data+= '[Service]\n'
		data+= 'User=pi\n'
		data+= 'ExecStart=\n'
		data+= 'ExecStart=/usr/bin/avnav -q -b ' + conf2.home + '/avnav/data -t /usr/lib/python3/dist-packages/openplotterAvnav/data/avnav_server.xml\n\n'
		data+= '[Install]\n'
		data+= 'WantedBy=multi-user.target\n'

		fo = open('/usr/lib/systemd/system/avnav.service.d/avnav.conf', "w")
		fo.write(data)
		fo.close()
		
		subprocess.call(['cp', '-av', '/usr/lib/python3/dist-packages/openplotterAvnav/data/signalk.service', '/etc/systemd/system'])
	except Exception as e: print(_('FAILED: ')+str(e))

	try:
		print(_('Setup avnav directory...'))
		subprocess.call(['systemctl', 'daemon-reload'])
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		subprocess.call(['systemctl', 'enable', 'avnav'])
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		subprocess.call(['systemctl', 'restart', 'avnav'])
	except Exception as e: print(_('FAILED: ')+str(e))
	#try:
	#	subprocess.call(['cp', '-avr', '/usr/lib/python3/dist-packages/openplotterAvnav/data/avnav-avahi.service', '/etc/avahi/services'])
	#except: pass
	try:
		print(_('Setup avnav ports...'))
		#default to port 8080 if you use pypilot you should change this port
		AVNport = 8080
		xmlDocFile = conf2.home +'/avnav/data/avnav_server.xml'
		xmlload = False
		if os.path.exists(xmlDocFile):
			xmlDoc = et.ElementTree(file=xmlDocFile)
			xmlload = True

			AVNHttpS = xmlDoc.find('.//AVNHttpServer')
			if AVNHttpS!=None:
				if 'httpPort' in AVNHttpS.attrib:
					try:
						AVNport = int(AVNHttpS.attrib['httpPort'] or 8080)
					except: pass

		soundSh= '/usr/lib/avnav/raspberry/sound.sh'
		raspberryDir = os.path.dirname(soundSh)
		if not os.path.exists(soundSh):
			if not os.path.exists(raspberryDir):
				os.makedirs(raspberryDir)
			try:
				os.symlink(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data','sound.sh')),soundSh)
			except:
				pass
		
		#change avahi
		#subprocess.call(platform2.admin + ' python3 '+currentdir+'/changeAvahiPort.py ' + str(AVNport), shell=True)
		#change menu
		output = subprocess.check_output(['grep','-F','Exec=','/usr/share/applications/avnav.desktop']).decode("utf-8")
		subprocess.call(platform2.admin + ' sed -i "s#'+output[0:-1]+'#Exec=x-www-browser http://localhost:'+str(AVNport)+'#g" /usr/share/applications/avnav.desktop', shell=True)
		
		subprocess.call(['systemctl', 'daemon-reload'])
		subprocess.call(['systemctl', 'restart', 'avnav'])
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		if not cssExists:
			while not os.path.exists(cssFile):
				time.sleep(0.1)

			subprocess.call(['cp', '/usr/lib/python3/dist-packages/openplotterAvnav/data/user.css', cssFile])
	except Exception as e: print(_('FAILED: ')+str(e))

	try:
		subprocess.call(['cp', '/usr/lib/python3/dist-packages/openplotterAvnav/data/kip.png', conf2.home +'/avnav/data/user/images'])
		subprocess.call(['cp', '/usr/lib/python3/dist-packages/openplotterAvnav/data/openplotter-48.png', conf2.home +'/avnav/data/user/images'])
	except Exception as e: print(_('FAILED: ')+str(e))

	try:
		subprocess.call(['cp', '/usr/lib/python3/dist-packages/openplotterAvnav/data/openplotter.json', '/usr/lib/avnav/viewer/layout'])
		subprocess.call(['mkdir', '-p', '/usr/lib/avnav/server/plugins/openplotter'])
		subprocess.call(['cp', '/usr/lib/python3/dist-packages/openplotterAvnav/data/index.html', '/usr/lib/avnav/server/plugins/openplotter'])
	except Exception as e: print(_('FAILED: ')+str(e))

	try:
		print(_('Setup NMEA0183 (Avnav->Signal K) for Autopilot (RMB)...'))

		addSKconnection(28628, platform2, 'fromAvnav')

		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Setting version...'))
	try:
		conf2.set('APPS', 'avnav', version)
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
