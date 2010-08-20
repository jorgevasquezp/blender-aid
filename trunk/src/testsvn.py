import unittest
import pysvn

class TestCase(unittest.TestCase):
    pass

def testLogin( realm, username, may_save ):
    return True, "jbakker", "zx098zx", False

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
        
if __name__ =='__main__':
    unittest.main()