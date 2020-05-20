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

import os, subprocess
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from .version import version

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-avnav',currentLanguage)

	try:
		print(_('Install app...'))
		platform2 = platform.Platform()

		subprocess.call(['apt', '-y', 'install', 'avnav'])
		
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
		
		
	try:
		print(_('Editing config files...'))
		if not os.path.isdir('/usr/lib/systemd/system/avnav.service.d'):
			os.makedirs('/usr/lib/systemd/system/avnav.service.d')
		
		data = '[Service]\n'
		data+= 'User=pi\n'
		data+= 'ExecStart=\n'
		data+= 'ExecStart=/usr/bin/avnav -q -b ' + conf2.home + '/avnav/data -t /usr/lib/python3/dist-packages/openplotterAvnav/data/avnav_server.xml\n'
		data+= '[Unit]\n'
		data+= 'WantedBy=multi-user.target\n'

		fo = open('/usr/lib/systemd/system/avnav.service.d/avnav.conf', "w")
		fo.write(data)
		fo.close()
		subprocess.call(['systemctl', 'daemon-reload'])
		subprocess.call(['systemctl', 'enable', 'avnav'])
		subprocess.call(['systemctl', 'restart', 'avnav'])
		subprocess.call(['cp', '-avr', '/usr/lib/python3/dist-packages/openplotterAvnav/data/avnav-avahi.service', '/etc/avahi/services'])

		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Setting version...'))
	if platform.Platform().isInstalled('avnav'):
		try:
			conf2.set('APPS', 'avnav', version)
			print(_('DONE'))
		except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
