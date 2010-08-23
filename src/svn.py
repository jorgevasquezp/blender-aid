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
# (c) 2009, At Mind B.V. - Jeroen Bakker


######################################################
# Importing modules
######################################################
import pysvn
import os.path as path
SVNURLSAME = 0              #location exists with same svn url
SVNURLDIFF = 1              #location exists with different svn url
SVNNOWORKINGFOLDER = 2      #location does not exists
SVNNOBINDING = 3            #location exists but is not under svn-control
SVNWORKINGFOLDERISFILE = 4  #location is a file

svnUsername = "";
svnPassword = "";

 #TODO test url with file: 
def testWorkingFolder(location, url):
    client = pysvn.Client()
    try:
        if path.isdir(location):
            locationUrl = client.info(location).url;
            if url==locationUrl:
               return SVNURLSAME;
            else:
                return SVNURLDIFF, locationurl;
        elif path.exists(location):
            return SVNWORKINGFOLDERISFILE;
        else:
            return SVNNOWORKINGFOLDER;
    except pysvn.ClientError, e:
        return SVNNOBINDING
    
def login( realm, username, may_save ):
    return True, svnUsername, svnPassword, False

def svnCheckout(location, url, uname, password):
    svnUsername = uname;
    svnPassword = password;
    client = pysvn.Client();
    client.callback_notify = notify;
    client.callback_get_login = login;
    client.checkout(url, location);