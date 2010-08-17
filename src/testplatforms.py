import unittest
import os


class Platform(unittest.TestCase):
    def runt(self, version):
        print("testing on python"+version+" platform.")
        self.assertTrue(os.system("python"+version+" testscenarios.py") ==0)
        self.assertTrue(os.system("python"+version+" testsvn.py") ==0)
    def testPython25(self):
        self.runt("2.5")
    def testPython26(self):
        self.runt("2.6")
    def testPython30(self):
        self.runt("3.0")
    def testPython31(self):
        self.runt("3.1")
        
        
if __name__ =='__main__':
    #os.argv.append("-v")
    unittest.main()