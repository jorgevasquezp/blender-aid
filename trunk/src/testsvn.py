import pysvn

def testLogin( realm, username, may_save ):
    return True, "jbakker", "zx098zx", False

def notify( event ):
    print(event)
    return

client = pysvn.Client()
client.callback_notify = notify
client.callback_get_login = testLogin
client.checkout("http://atmind/svn/yofrankie", "/home/dev/yofrankie");