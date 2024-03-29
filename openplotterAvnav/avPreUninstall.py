#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2023 by Sailoog <https://github.com/openplotter/openplotter-avnav>
# Copyright (C) 2023 by e-sailing <https://github.com/e-sailing/openplotter-avnav>
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

import os, subprocess, shutil
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSignalkInstaller import editSettings

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	package = 'openplotter-avnav'
	language.Language(currentdir, package, currentLanguage)

	print(_('Removing avnav service...'))
	try:
		subprocess.call(['systemctl', 'disable', 'avnav'])
		subprocess.call(['systemctl', 'stop', 'avnav'])
		if os.path.isfile('/usr/lib/systemd/system/avnav.service.d/avnav.conf'):
			os.remove('/usr/lib/systemd/system/avnav.service.d/avnav.conf')
		if os.path.isfile('/etc/avahi/services/avnav-avahi.service'):
			os.remove('/etc/avahi/services/avnav-avahi.service')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Removing SignalK avnav connection...'))
	try:
		skSettings = editSettings.EditSettings()
		if skSettings.connectionIdExists('fromAvnav'):
			skSettings.removeConnection('fromAvnav')			
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Removing avnav...'))
	try:
		if os.path.isdir('/usr/lib/avnav/plugins/openplotter'):
			shutil.rmtree('/usr/lib/avnav/plugins/openplotter')
		if os.path.isdir('/usr/lib/avnav/raspberry'):
			shutil.rmtree('/usr/lib/avnav/raspberry')	
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		subprocess.call(['apt', '-y', 'autoremove', 'avnav'])
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		subprocess.call(['apt', '-y', 'autoremove', 'avnav-history-plugin', 'avnav-update-plugin'])
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		subprocess.call(['apt', '-y', 'autoremove', 'avnav-mapproxy-plugin'])
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		subprocess.call(['apt', '-y', 'autoremove', 'avnav-ocharts-plugin'])
	except Exception as e: print(_('FAILED: ')+str(e))
	try:
		subprocess.call(['apt', '-y', 'autoremove', 'avnav-ocharts'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))


	print(_('Removing version...'))
	try:
		conf2.set('APPS', 'avnav', '')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
