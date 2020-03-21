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

import os, subprocess, sys
from openplotterSettings import conf
from openplotterSettings import language

def main():
	try:
		conf2 = conf.Conf()
		currentdir = os.path.dirname(os.path.abspath(__file__))
		currentLanguage = conf2.get('GENERAL', 'lang')
		language.Language(currentdir,'openplotter-avnav',currentLanguage)
		beta = conf2.get('GENERAL', 'beta')

		print(_('Start adding sources.'))

		os.system('cp '+currentdir+'/data/sources/open-mind.list /etc/apt/sources.list.d/open-mind.list')
		print(_('Added list'))
		os.system('apt-key add - < '+currentdir+'/data/sources/open-mind.space.gpg.key')
		print(_('Added gpg.key'))
		os.system('apt update')
		print(_('app list updated'))
		print(_('Done'))

	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
