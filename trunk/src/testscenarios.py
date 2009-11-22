import unittest
import os
import settings
import serviceproduction
import servicerefactor
import indexer
try:
    import json
except:
    import simplejson as json
REPOSITORYROOTLOCATION=os.path.abspath("../test/")
REPOSITORYLOCATION=os.path.abspath("../test/blender-aid-unittest")
REPOSITORYPACKED=os.path.abspath("../test/blender-aid-unittest.tar.gz")
REPOSITORYCONNECTIONURL=os.path.abspath("../test/sql.bin")

class TestCase(unittest.TestCase):
    pass
    
def refresh():
    settings.SQLITE3_CONNECTIONURL=REPOSITORYCONNECTIONURL
    os.chdir(REPOSITORYROOTLOCATION)
    os.system("rm "+REPOSITORYCONNECTIONURL)
    os.system("rm -Rf "+ REPOSITORYLOCATION)
    os.system("tar -xzf "+REPOSITORYPACKED)
    indexer.setup()
    
class Scenario1(TestCase):
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
        servicerefactor.handleStartMoveFile(Tempout(), {"file_id":fileId,"new_location":newLocation},session)
        servicerefactor.handleExecuteCurrentTasks(Tempout(), {},session)
        
        
    def testScenarioMoveBlend1(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.moveFile(session, "chars/frankie_testlevel.blend", "levels")
        servicerefactor.handleCommitCurrentTasks(Tempout(), {},session)
        
    def testScenarioMoveBlend2(self):
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
        servicerefactor.handleStartRenameFile(Tempout(), {"file_id":fileId,"new_filename":newName},session)
        servicerefactor.handleExecuteCurrentTasks(Tempout(), {},session)
        
        
    def testScenarioRenameBlend1(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.renameFile(session, "chars/frankie.blend", "frankie_momo.blend")
        servicerefactor.handleCommitCurrentTasks(Tempout(), {},session)
        
    def testScenarioRenameBlend2(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.renameFile(session, "chars/frankie.blend", "frankie_momo.blend")
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
        serviceproduction.handleGetFileView(out2, {"file_id":fileId}, session)
        result = out.loads()
        elements=result[1]
        elementId=None
        for element in elements:
            if element["element_name"]==elementName:
                elementId=element["element_id"]
        
        servicerefactor.handleStartRenameElement(Tempout(), {"production_id":session["production_id"],"file_id":fileId,"element_id":elementId, "new_name":newName},session)
        servicerefactor.handleExecuteCurrentTasks(Tempout(), {},session)
        
        
    def testScenarioRenameElement1(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.renameElement(session, "chars/frankie.blend", "GRFlyingSquirrel", "GRFrankie")
        servicerefactor.handleCommitCurrentTasks(Tempout(), {},session)
        
    def testScenarioRenameElement2(self):
        refresh()
        serviceproduction.handleAdd(Tempout(), {"production_location":REPOSITORYLOCATION, "production_name":"unittest"}, {})
        session ={}
        serviceproduction.handleActivateProduction(Tempout(), {"production_id":1}, session)

        self.renameElement(session, "chars/frankie.blend", "GRFlyingSquirrel", "GRFrankie")
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
        
unittest.main()