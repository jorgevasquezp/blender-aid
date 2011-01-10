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
# (c) 2010, At Mind B.V. - Jeroen Bakker, Monique Dewanchand
import unittest
import pysvn
import svn
import inspect
import os
import subprocess
import time

class TestCase(unittest.TestCase):
    pass

def testLogin( realm, username, may_save ):
    return True, "test", "test", False

def notify( event ):
    print(event["action"], event["path"])
    return

class ScenarioBasicSVN(TestCase):

    def testSvnCheckout(self):
        client = pysvn.Client()
        client.callback_notify = notify
        client.callback_get_login = testLogin
        client.checkout("http://atmind/svn/test", "/tmp/test");
    
    def testUpdate(self):
        client = pysvn.Client()
        client.callback_notify = notify
        client.callback_get_login = testLogin
        client.update("/tmp/test");

    def testLog(self):
        client = pysvn.Client()
        client.callback_notify = notify
        client.callback_get_login = testLogin
        logs = client.log("/tmp/test");
        print(logs)
        
    def testFileInfo(self):
        client = pysvn.Client()
        entry = client.info("/tmp/test/file1.blend")
        print(entry.url, entry.commit_author, entry.commit_revision, entry.commit_time)
        print(entry.url, entry.revision.number, entry.revision.kind)
      
    def testWorkingFolder(self):
        #test path is dir
        currentFile = inspect.currentframe().f_code.co_filename;
        result, additional = svn.testWorkingFolder(currentFile, "http://atmind/svn/test");
        self.assertEqual(result, svn.SVNWORKINGFOLDERISFILE);
        #location does not exist
        result, additional = svn.testWorkingFolder("/bladiebla", "http://atmind/svn/test");
        self.assertEqual(result, svn.SVNNOWORKINGFOLDER);
        #non existing url
        result, additional = svn.testWorkingFolder("/tmp", "http://atmind2/svn/test");
        self.assertEqual(result, svn.SVNNOBINDING);
        #different svn, make test dir
        if os.path.exists("/tmp/test"):
            retcode = subprocess.call(["rm", "-Rf", "/tmp/test"]);
        svn.svnCheckout("/tmp/test", "http://atmind/svn/test", "test", "test");
        result, additional = svn.testWorkingFolder("/tmp/test", "http://atmind/svn/yofrankie");
        self.assertEqual(result, svn.SVNURLDIFF);
        #same svn, make test dir
        if os.path.exists("/tmp/test"):
            retcode = subprocess.call(["rm", "-Rf", "/tmp/test"]);
        svn.svnCheckout("/tmp/test", "http://atmind/svn/test", "test", "test");
        result, additional = svn.testWorkingFolder("/tmp/test", "http://atmind/svn/test");
        self.assertEqual(result, svn.SVNURLSAME);
        
    def testSvnStat(location):
        client = pysvn.Client();
        location="/tmp/test"
        status_list = client.status(location, True, True, False, False, False);
        for stat in status_list:
            print(stat.entry.name, stat.prop_status)
             
        
    def testSvnAdd(path):
        client = pysvn.Client();
        location="/tmp/test"
        #TODO
    
    def testSvnRevert(location):
        client = pysvn.Client();
        location="/tmp/test"
        #TODO
        
if __name__ =='__main__':
    unittest.main()