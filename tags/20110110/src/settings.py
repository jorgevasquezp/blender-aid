# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
#
# (c) 2009, At Mind B.V. - Jeroen Bakker, Monique Dewanchand

# where is the webserver binding
# do not use port less than 1024 as they need to be created with more privileged than
# normal users.
WEBSERVER_BINDING=("localhost", 8080)

# location of the sql database binary.
# this file will be created when not exists
SQLITE3_CONNECTIONURL="/var/tmp/sql102010.bin"

import platform
if platform.system() in ('Windows', 'Microsoft'):
    import os.path as path
    SQLITE3_CONNECTIONURL=path.abspath("sql102010.bin")
    print("using database located at "+SQLITE3_CONNECTIONURL)

#Stylesheet to use in html
STYLE_SHEET="site.css"

#release version of the system
VERSION="20101015"

#additional description of the release
VERSION_DESCRIPTION="October 2010 - svn integration"

#debug flag
DEBUG=False
