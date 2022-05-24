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

import os, sys, subprocess, time, shutil
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from .version import version

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
							if i['pipeElements'][0]['options']['subOptions']['type'] == 'tcp':
								if i['pipeElements'][0]['options']['subOptions']['host'] == 'localhost':
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


	print(_('Install app...'))

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
	print(_('DONE'))

	try:
		if os.path.isdir('/usr/lib/avnav/plugins/openplotter'):
			shutil.rmtree('/usr/lib/avnav/plugins/openplotter')	
		print(_('Install openplotter plugin...'))
		src = currentdir+'/data/plugins/openplotter'
		dest = '/usr/lib/avnav/plugins/openplotter'
		shutil.copytree(src, dest)
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
		
	try:
	#if True:
		print(_('Editing config files...'))
		if not os.path.isdir('/usr/lib/systemd/system/avnav.service.d'):
			os.makedirs('/usr/lib/systemd/system/avnav.service.d')
		
		data= '[Service]\n'
		data+= 'User='+conf2.home.split('/')[2]+'\n'
		data+= 'ExecStart=\n'
		data+= 'ExecStart=/usr/bin/avnav -q -b ' + conf2.home + '/avnav/data -t '+currentdir+'/data/avnav_server.xml\n\n'

		fo = open('/usr/lib/systemd/system/avnav.service.d/avnav.conf', "w")
		fo.write(data)
		fo.close()
		
		print(_('DONE'))

	except Exception as e: print(_('FAILED: ')+str(e))

	try:
		print(_('Start daemon-reload...'))
		subprocess.call(['systemctl', 'daemon-reload'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		print(_('Start enable avnav autostart...'))
		subprocess.call(['systemctl', 'enable', 'avnav'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		print(_('Start avnav restart...'))
		subprocess.call(['systemctl', 'restart', 'avnav'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	try:
		print(_('Setup sound...'))
		soundSh= '/usr/lib/avnav/raspberry/sound.sh'
		raspberryDir = os.path.dirname(soundSh)
		if not os.path.exists(soundSh):
			if not os.path.exists(raspberryDir):
				os.makedirs(raspberryDir)
			try:
				os.symlink(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data','sound.sh')),soundSh)
			except:
				pass

		AVNport = 8080		
		#change avahi
		#subprocess.call(platform2.admin + ' python3 '+currentdir+'/changeAvahiPort.py ' + str(AVNport), shell=True)
		#change menu
		output = subprocess.check_output(['grep','-F','Exec=','/usr/share/applications/avnav.desktop']).decode("utf-8")
		subprocess.call(platform2.admin + ' sed -i "s#'+output[0:-1]+'#Exec=x-www-browser http://localhost:'+str(AVNport)+'#g" /usr/share/applications/avnav.desktop', shell=True)
		
		#subprocess.call(['systemctl', 'daemon-reload'])
		#subprocess.call(['systemctl', 'restart', 'avnav'])
		print(_('DONE'))
		
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
