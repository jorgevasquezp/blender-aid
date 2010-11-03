import unittest
import servicerefactor

class TestCase(unittest.TestCase):
    pass

class ScenarioMoveDirectory(TestCase):
    def testMoveDirectory(self):
        source = "chars"
        target= "characters"
        productionId=1
        s = {"production_id":1,
            "source_directory":"chars",
            "target_directory_name":"characters"}
        servicerefactor.handleStartRenameDirectory(None, s, s)
        
        pass
        

if __name__ =='__main__':
    unittest.main()