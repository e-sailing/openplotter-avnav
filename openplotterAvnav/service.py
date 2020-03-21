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

import sys, subprocess, os

def edit_boot(onoff):
	file = open('/boot/config.txt', 'r')
	file1 = open('config.txt', 'w')
	exists = False
	while True:
		line = file.readline()
		if not line: break
		if onoff and 'dtoverlay=pi3-disable-bt' in line: 
			file1.write('dtoverlay=pi3-disable-bt\n')
			os.system('systemctl disable hciuart')
			exists = True
		elif not onoff and 'dtoverlay=pi3-disable-bt' in line: 
			file1.write('#dtoverlay=pi3-disable-bt\n')
			os.system('systemctl enable hciuart')
			exists = True
		else: file1.write(line)
	if onoff and not exists: 
		file1.write('\ndtoverlay=pi3-disable-bt\n')
		os.system('systemctl disable hciuart')
	file.close()
	file1.close()

	file = open('/boot/cmdline.txt', 'r')
	file1 = open('cmdline.txt', 'w')
	text = file.read()
	text = text.replace('\n', '')
	text_list = text.split(' ')
	if onoff and 'console=serial0,115200' in text_list: 
		text_list.remove('console=serial0,115200')
	if not onoff and not 'console=serial0,115200' in text_list: 
		text_list.append('console=serial0,115200')
	final = ' '.join(text_list)+'\n'
	file1.write(final)
	file.close()
	file1.close()

	reset = False
	if os.system('diff config.txt /boot/config.txt > /dev/null'):
		os.system('mv config.txt /boot')
		reset = True
	else: os.system('rm -f config.txt')
	if os.system('diff cmdline.txt /boot/cmdline.txt > /dev/null'):
		os.system('mv cmdline.txt /boot')
		reset = True
	else: os.system('rm -f cmdline.txt')

	if reset == True : os.system('shutdown -r now')

if sys.argv[1]=='start':
	subprocess.call(['systemctl', 'start', 'signalk.socket'])
	subprocess.call(['systemctl', 'start', 'signalk.service'])
if sys.argv[1]=='stop':
	subprocess.call(['systemctl', 'stop', 'signalk.service'])
	subprocess.call(['systemctl', 'stop', 'signalk.socket'])
if sys.argv[1]=='restart':
	subprocess.call(['systemctl', 'stop', 'signalk.service'])
	subprocess.call(['systemctl', 'stop', 'signalk.socket'])
	subprocess.call(['systemctl', 'start', 'signalk.socket'])
	subprocess.call(['systemctl', 'start', 'signalk.service'])
if sys.argv[1]=='udev':
	path = sys.argv[2]
	os.system('mv '+path+' /etc/udev/rules.d')
	subprocess.call(['udevadm', 'control', '--reload-rules'])
	subprocess.call(['udevadm', 'trigger', '--attr-match=subsystem=tty'])
if sys.argv[1]=='uartTrue': edit_boot(True)
if sys.argv[1]=='uartFalse': edit_boot(False)
if sys.argv[1]=='pypilot':
	subprocess.call(['systemctl', 'disable', 'pypilot_boatimu'])
	subprocess.call(['systemctl', 'enable', 'pypilot'])
	subprocess.call(['systemctl', 'enable', 'openplotter-pypilot-read'])
	subprocess.call(['systemctl', 'stop', 'pypilot_boatimu'])
	subprocess.call(['systemctl', 'restart', 'pypilot'])
	subprocess.call(['systemctl', 'restart', 'openplotter-pypilot-read'])
	try: subprocess.check_output(['systemctl', 'is-enabled', 'pypilot_web']).decode(sys.stdin.encoding)
	except: pass
	else: subprocess.call(['systemctl', 'restart', 'pypilot_web'])