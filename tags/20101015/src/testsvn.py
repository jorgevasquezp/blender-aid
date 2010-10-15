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