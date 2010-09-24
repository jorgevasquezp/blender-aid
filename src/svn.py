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
# (c) 2009, At Mind B.V. - M.Dewanchand, Jeroen Bakker


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

_svnUsername = "";
_svnPassword = "";

 #TODO test url with file: 
def testWorkingFolder(location, url):
    client = pysvn.Client()
    try:
        if path.isdir(location):
            locationUrl = client.info(location).url;
            if url==locationUrl:
               return (SVNURLSAME, "");
            else:
                return (SVNURLDIFF, locationUrl);
        elif path.exists(location):
            return (SVNWORKINGFOLDERISFILE, "");
        else:
            return (SVNNOWORKINGFOLDER, "");
    except pysvn.ClientError, e:
        return (SVNNOBINDING, "");
    
def login( realm, username, may_save ):
    global _svnUsername
    global _svnPassword
    return True, _svnUsername, _svnPassword, False

def notify( event ):
    print(event["action"], event["path"])
    return

def svnCheckout(location, url, uname, password):
    global _svnUsername
    global _svnPassword
    _svnUsername = uname;
    _svnPassword = password;

    client = pysvn.Client();
    client.callback_notify = notify;
    client.callback_get_login = login;
    client.checkout(url, location);
    
def svnStat(location):
    client = pysvn.Client()
    status_list = client.status(location, True, True, False, False, False)
    return status_list

def svnAdd(path):
    client = pysvn.Client()
    client.add(path);
    return

def svnRevert(path):
    client = pysvn.Client()
    client.revert(path);
    return

# Is the given absolute filepath a known SVN file.
#   returns True is the file is known by svn
#   returns False if the file is not known by svn.
def isKnownSVNFile(filepath):
    client = pysvn.Client()
    try:
        info = client.info(filepath);
        return True
    except pysvn.ClientError, e:
        return False

# action to move a svn file to another location (rename or move)
def move(fileLocation, newFileLocation):
    client = pysvn.Client()
    client.move(fileLocation, newFileLocation)

def svnUpdate(location, username, password):
    global _svnUsername
    global _svnPassword
    _svnUsername = username;
    _svnPassword = password;
    client = pysvn.Client();
    client.callback_notify = notify;
    client.callback_get_login = login;
    client.update(location);