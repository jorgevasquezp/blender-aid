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
        client.checkout("http://atmind/svn/yofrankie", "/tmp/yofrankie");
    
    def testUpdate(self):
        client = pysvn.Client()
        client.callback_notify = notify
        client.callback_get_login = testLogin
        client.update("/tmp/yofrankie");

    def testLog(self):
        client = pysvn.Client()
        client.callback_notify = notify
        client.callback_get_login = testLogin
        logs = client.log("/tmp/yofrankie");
        print(logs)
        
if __name__ =='__main__':
    unittest.main()