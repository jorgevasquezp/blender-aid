import unittest
import os
import settings
import serviceproduction
import servicerefactor
import indexer
import urllib
try:
    import json
except:
    import simplejson as json
REPOSITORYROOTLOCATION=os.path.abspath("../test/")
REPOSITORYLOCATION=os.path.abspath("../test/blender-aid-unittest")
REPOSITORYPACKED=os.path.abspath("../test/blender-aid-unittest.tar.gz")
REPOSITORYPACKED2=os.path.abspath("../test/blender-aid-unittest.zip")
REPOSITORYCONNECTIONURL=os.path.abspath("../test/sql.bin")

def prepareunittests():
    if os.path.exists(REPOSITORYPACKED):
        return
    os.system("rm "+REPOSITORYCONNECTIONURL)
    os.system("rm -Rf "+ REPOSITORYLOCATION)
    urllib.urlretrieve("http://download.blender.org/apricot/yofrankie_1_1b_bge.zip", REPOSITORYPACKED2)
    os.chdir(REPOSITORYROOTLOCATION)
    os.system("unzip "+REPOSITORYPACKED2)
    os.system("mv yofrankie_1_1b_bge blender-aid-unittest")
    os.system("tar -czf blender-aid-unittest.tar.gz blender-aid-unittest")
    
class TestCase(unittest.TestCase):
    pass
    
def refresh():
    settings.SQLITE3_CONNECTIONURL=REPOSITORYCONNECTIONURL
    os.chdir(REPOSITORYROOTLOCATION)
    os.system("rm "+REPOSITORYCONNECTIONURL)
    os.system("rm -Rf "+ REPOSITORYLOCATION)
    os.system("tar -xzf "+REPOSITORYPACKED)
    indexer.setup()
    
class ScenarioBasicAdministration(TestCase):
    def testAddProduction(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        
    def testActivateProduction(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, {})
        
    def testScanProduction(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, {})
        serviceproduction.handleGetProductionView(Tempout(), {}, {})
        
    def testDeleteProduction(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, {})
        serviceproduction.handleGetProductionView(Tempout(), {}, {})
        serviceproduction.handleDelete(Tempout(), {"production_id":1}, {})

class ScenarioMoveFile(TestCase):
    def moveFile(self, session, location, newLocation):
        out = Tempout()
        serviceproduction.handleGetProductionView(out, {}, session)
        result = out.loads()
        files = result[1]
        fileId=None
        for file in files:
            if file["file_location"]==location:
                fileId=file["file_id"]

        self.assertFalse(fileId == None)

        servicerefactor.handleStartMoveFile(Tempout(), {"file_id":fileId,"new_location":newLocation},session)
        servicerefactor.handleExecuteCurrentTasks(Tempout(), {},session)
        
        
    def testScenarioMoveBlendCommit(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.moveFile(session, "chars/frankie_testlevel.blend", "levels")
        servicerefactor.handleCommitCurrentTasks(Tempout(), {},session)
        
    def testScenarioMoveBlendRollback(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.moveFile(session, "chars/frankie_testlevel.blend", "levels")
        servicerefactor.handleRollbackCurrentTasks(Tempout(), {},session)
        
class ScenarioRenameFile(TestCase):
    def renameFile(self, session, location, newName):
        out = Tempout()
        serviceproduction.handleGetProductionView(out, {}, session)
        result = out.loads()
        files = result[1]
        fileId=None
        for file in files:
            if file["file_location"]==location:
                fileId=file["file_id"]
        self.assertFalse(fileId == None)

        servicerefactor.handleStartRenameFile(Tempout(), {"file_id":fileId,"new_filename":newName},session)
        servicerefactor.handleExecuteCurrentTasks(Tempout(), {},session)
        
        
    def testScenarioRenameBlendCommit(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.renameFile(session, "chars/frankie.blend", "frankie_momo.blend")
        servicerefactor.handleCommitCurrentTasks(Tempout(), {},session)
        
    def testScenarioRenameBlendRollback(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.renameFile(session, "chars/frankie.blend", "frankie_momo.blend")
        servicerefactor.handleRollbackCurrentTasks(Tempout(), {},session)

    def testScenarioRenameTextureCommit(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.renameFile(session, "chars/textures/flyingsquirrel_skin_col.jpg", "frankie_skin_col.jpg")
        servicerefactor.handleCommitCurrentTasks(Tempout(), {},session)
        
    def testScenarioRenameTextureRollback(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.renameFile(session, "chars/textures/flyingsquirrel_skin_col.jpg", "frankie_skin_col.jpg")
        servicerefactor.handleRollbackCurrentTasks(Tempout(), {},session)

class ScenarioRenameElement(TestCase):
    def renameElement(self, session, location, elementName, newName):
        out = Tempout()
        out2 = Tempout()
        serviceproduction.handleGetProductionView(out, {}, session)
        result = out.loads()
        files = result[1]
        fileId=None
        for file in files:
            if file["file_location"]==location:
                fileId=file["file_id"]
                
        self.assertFalse(fileId == None)
        
        serviceproduction.handleGetFileView(out2, {"file_id":fileId, "production_id":session["production_id"]}, session)
        result = out2.loads()
        elements=result[2]
        elementId=None
        for element in elements:
            if element["element_name"]==elementName:
                elementId=element["element_id"]
        
        servicerefactor.handleStartRenameElement(Tempout(), {"production_id":session["production_id"],"file_id":fileId,"element_id":elementId, "new_name":newName},session)
        servicerefactor.handleExecuteCurrentTasks(Tempout(), {},session)
        
        
    def testScenarioRenameElementCommit(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.renameElement(session, "chars/frankie.blend", "GRFlyingSquirrel", "GRFrankie")
        servicerefactor.handleCommitCurrentTasks(Tempout(), {},session)
        
    def testScenarioRenameElementRollback(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.renameElement(session, "chars/frankie.blend", "GRFlyingSquirrel", "GRFrankie")
        servicerefactor.handleRollbackCurrentTasks(Tempout(), {},session)
        
class ScenarioSolveMissingLink(TestCase):
    def osRenameFile(self, source, target):
        os.chdir(REPOSITORYLOCATION)
        os.system("mv "+source+" "+target)

    def fix(self, missing, source, target, session):
        out = Tempout()
        out2 = Tempout()
        serviceproduction.handleGetProductionView(out, {}, session)
        result = out.loads()
        missings = result[3]
        elementId=None
        fileId=None
        newFileId=None
        for link in missings:
            if link["file_location"]==source and link["missing_file_location"]==missing:
                elementId=link["element_id"]
                fileId=link["file_id"]
        self.assertFalse(elementId==None)
        self.assertFalse(fileId==None)
        servicerefactor.handleGetMissingLinkSolutions(out2, {"production_id":session["production_id"],"element_id":elementId}, session)
        result2 = out2.loads()
        for solution in result2:
            if solution["file_location"]==target:
                newFileId=solution["file_id"]
                
        self.assertFalse(newFileId==None)
        servicerefactor.handleStartSolveMissingLink(Tempout(), {"file_id":newFileId, "element_id":elementId}, session)
        servicerefactor.handleExecuteCurrentTasks(Tempout(), {},session)

    def testMissingBlendFileCommit(self):
        refresh()
        self.osRenameFile("chars/bird.blend", "chars/birdtest.blend")
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)
        self.fix("chars/bird.blend", "levels/start_menu.blend", "chars/birdtest.blend", session)
        servicerefactor.handleCommitCurrentTasks(Tempout(), {},session)
    def testMissingBlendFileRollback(self):
        refresh()
        self.osRenameFile("chars/bird.blend", "chars/birdtest.blend")
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)
        self.fix("chars/bird.blend", "levels/start_menu.blend", "chars/birdtest.blend", session)
        servicerefactor.handleRollbackCurrentTasks(Tempout(), {},session)

        

class Tempout():
    def __init__(self):
        self.out = None
    def write(self, obj):
        if self.out == None:
            self.out = obj
        else:
            self.out += obj
    def loads(self):
        return json.loads(self.out.decode())
        
if __name__ =='__main__':
    prepareunittests()
    unittest.main()