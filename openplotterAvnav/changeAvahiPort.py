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

import sys
from xml.etree import ElementTree as et

def main(arg):
	if len(arg)>1:
		#print(arg[1])
		xmlFile = '/etc/avahi/services/avnav-avahi.service'
		xmlDoc = et.ElementTree(file=xmlFile)
		xmlDoc.find('.//port').text = arg[1]
		xmlDoc.write(xmlFile)

if __name__ == '__main__':
	main(sys.argv)
