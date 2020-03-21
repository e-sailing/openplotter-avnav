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

from setuptools import setup
from openplotterAvnav import version

setup (
	name = 'openplotterAvnav',
	version = version.version,
	description = 'OpenPlotter app to manage avnav',
	license = 'GPLv3',
	author="E-Sailing",
	author_email='e.minus.sailing@gmail.com',
	url='https://github.com/e-sailing/openplotter-avnav',
	packages=['openplotterAvnav'],
	classifiers = ['Natural Language :: English',
	'Operating System :: POSIX :: Linux',
	'Programming Language :: Python :: 3'],
	include_package_data=True,
	entry_points={'console_scripts': ['openplotter-avnav=openplotterAvnav.openplotterAvnav:main','settingsAVSourcesInstall=openplotterAvnav.installSources:main']},
	data_files=[('share/applications', ['openplotterAvnav/data/openplotter-avnav.desktop']),('share/pixmaps', ['openplotterAvnav/data/sailboat24r.png']),],
	)
