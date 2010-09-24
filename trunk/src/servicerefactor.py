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
# (c) 2009, At Mind B.V. - Jeroen Bakker


######################################################
# Importing modules
######################################################
import logging
import indexer
from factory import solutionToObject, solutionIDToObject
import shutil
import os
import posixpath
import blendfile
import svn

log = logging.getLogger("refactor")
log.setLevel(logging.INFO)

try:
    import json
except:
    log.info("python < 2.6: using simplejson")
    import simplejson as json

try:
    from os.path import relpath as _relpath
except:
    log.info("python < 2.6: import custom relpath")
    from bautil import relpath as _relpath


######################################################
# Handlers
######################################################
def handleStartMoveFile(wfile, request, session):
    productionId=int(session["production_id"])
    production = indexer.getProduction(productionId)
    fileId=int(request["file_id"])
    fileDetails = indexer.getFile(fileId)
    newLocation = request["new_location"]
    if os.path.exists(os.path.join(production[2],newLocation,fileDetails[2])):
        wfile.write("""[{"message":"File already exists."}]""".encode())
        return

    tasks = []
    filesDone = []
    usedby = indexer.getFileUsedBy(fileId)

    bu = BackupFile()
    bu.fileId = fileId
    bu.fileDetails = indexer.getFile(fileId)
    bu.productionDetails=production
    tasks.append(bu)

    for used in usedby:
        ofileId = used[3]
        if ofileId not in filesDone:
            bu = BackupFile()
            bu.fileId = ofileId
            bu.fileDetails = indexer.getFile(ofileId)
            bu.productionDetails=production
            
            ac = MoveLibrary()
            ac.fileId = ofileId
            ac.fileDetails = indexer.getFile(ofileId)
            ac.referenceFileId = fileId
            ac.newLocation = newLocation
            ac.currentFilename = fileDetails[2]
            ac.currentFileLocation = fileDetails[3]
            ac.productionDetails=production

            filesDone.append(ofileId)
            tasks.append(bu)            
            tasks.append(ac)

    bu = MoveFile()
    bu.fileId = fileId
    bu.fileDetails = fileDetails
    bu.currentFilename = fileDetails[2]
    bu.currentFileLocation = fileDetails[3]
    bu.newLocation = newLocation
    bu.productionDetails=production
    tasks.append(bu)

    session["tasks"]=tasks
    wfile.write("""[]""".encode())
    
def handleStartRenameFile(wfile, request, session):
    productionId=int(session["production_id"])
    production = indexer.getProduction(productionId)
    fileId=int(request["file_id"])
    fileDetails = indexer.getFile(fileId)
    newFilename = request["new_filename"]
    if os.path.exists(os.path.join(os.path.dirname(os.path.join(production[2],fileDetails[3])),newFilename)):
        wfile.write("""[{"message":"File already exists."}]""".encode())
        return

    tasks = []
    filesDone = []
    usedby = indexer.getFileUsedBy(fileId)
    
    bu = BackupFile()
    bu.fileId = fileId
    bu.fileDetails = indexer.getFile(fileId)
    bu.productionDetails=production
    tasks.append(bu)
    
    for used in usedby:
        ofileId = used[3]
        if ofileId not in filesDone:
            bu = BackupFile()
            bu.fileId = ofileId
            bu.fileDetails = indexer.getFile(ofileId)
            bu.productionDetails=production
            
            ac = RenameLibrary()
            ac.fileId = ofileId
            ac.fileDetails = indexer.getFile(ofileId)
            ac.referenceFileId = fileId
            ac.newFilename = newFilename
            ac.currentFilename = fileDetails[2]
            ac.currentFileLocation = fileDetails[3]
            ac.productionDetails=production

            filesDone.append(ofileId)
            tasks.append(bu)            
            tasks.append(ac)

    bu = RenameFile()
    bu.fileId = fileId
    bu.fileDetails = fileDetails
    bu.currentFilename = fileDetails[2]
    bu.newFilename = newFilename
    bu.productionDetails=production
    tasks.append(bu)
        
    session["tasks"]=tasks
    wfile.write("""[]""".encode())
    
def handleStartRenameFile(wfile, request, session):
    productionId=int(session["production_id"])
    production = indexer.getProduction(productionId)
    fileId=int(request["file_id"])
    fileDetails = indexer.getFile(fileId)
    newFilename = request["new_filename"]
    if os.path.exists(os.path.join(os.path.dirname(os.path.join(production[2],fileDetails[3])),newFilename)):
        wfile.write("""[{"message":"File already exists."}]""".encode())
        return

    tasks = []
    filesDone = []
    usedby = indexer.getFileUsedBy(fileId)
    
    bu = BackupFile()
    bu.fileId = fileId
    bu.fileDetails = indexer.getFile(fileId)
    bu.productionDetails=production
    tasks.append(bu)
    
    for used in usedby:
        ofileId = used[3]
        if ofileId not in filesDone:
            bu = BackupFile()
            bu.fileId = ofileId
            bu.fileDetails = indexer.getFile(ofileId)
            bu.productionDetails=production
            
            ac = RenameLibrary()
            ac.fileId = ofileId
            ac.fileDetails = indexer.getFile(ofileId)
            ac.referenceFileId = fileId
            ac.newFilename = newFilename
            ac.currentFilename = fileDetails[2]
            ac.currentFileLocation = fileDetails[3]
            ac.productionDetails=production

            filesDone.append(ofileId)
            tasks.append(bu)            
            tasks.append(ac)

    bu = RenameFile()
    bu.fileId = fileId
    bu.fileDetails = fileDetails
    bu.currentFilename = fileDetails[2]
    bu.newFilename = newFilename
    bu.productionDetails=production
    tasks.append(bu)
        
    session["tasks"]=tasks
    wfile.write("""[]""".encode())
    
def handleStartRenameElement(wfile, request, session):
    productionId=int(session["production_id"])
    production = indexer.getProduction(productionId)
    fileId=int(request["file_id"])
    elementId=int(request["element_id"])
    fileDetails = indexer.getFile(fileId)
    elementDetails = indexer.getElementDetails(elementId)
    newElementName = request["new_name"]
    
    for row in indexer.getFileElementByName(fileId, newElementName): 
        wfile.write("""[{"message":"Element already exists."}]""".encode())
        return
    if newElementName[0:2] != elementDetails[2][0:2]:
        wfile.write(("""[{"message":"Type of element cannot be changed.["""+elementDetails[2][0:2]+"""]"}]""").encode())
        return
        
    
    tasks = []
    filesDone = []
    usedby = indexer.getReferenceToElement(productionId, fileId, elementDetails[2])
    
    bu = BackupFile()
    bu.fileId = fileId
    bu.fileDetails = indexer.getFile(fileId)
    bu.productionDetails=production
    tasks.append(bu)
    
    for used in usedby:
        ofileId = used[0]
        if ofileId not in filesDone:
            bu = BackupFile()
            bu.fileId = ofileId
            bu.fileDetails = indexer.getFile(ofileId)
            bu.productionDetails=production
            
            ac = RenameIDElement()
            ac.fileId = ofileId
            ac.fileDetails = indexer.getFile(ofileId)
            ac.elementDetails = elementDetails
            ac.referenceFileId = fileId
            ac.newElementName = newElementName
            ac.currentElementName = elementDetails[2]
            ac.currentFilename = fileDetails[2]
            ac.currentFileLocation = fileDetails[3]
            ac.productionDetails=production

            filesDone.append(ofileId)
            tasks.append(bu)            
            tasks.append(ac)

    bu = RenameElement()
    bu.fileId = fileId
    bu.fileDetails = fileDetails
    bu.elementDetails = elementDetails
    bu.currentFilename = fileDetails[2]
    bu.newElementName = newElementName
    bu.productionDetails = production
    tasks.append(bu)
        
    session["tasks"]=tasks
    wfile.write("""[]""".encode())

def handleStartSolveMissingLink(wfile, request, session):
    productionId=int(session["production_id"])
    production = indexer.getProduction(productionId)
    fileId=int(request["file_id"])
    elementId=int(request["element_id"])
    #determine original file if from elementid
    elementDetails = indexer.getElement(elementId)
    elementType=elementDetails[indexer.INDEX_ELEMENT_TYPE]
    orFileId = elementDetails[indexer.INDEX_ELEMENT_FILE_ID]
    orFileDetails = indexer.getFile(orFileId)
    tasks = []
    bu = BackupFile()
    bu.fileId = orFileId
    bu.fileDetails = orFileDetails
    bu.productionDetails=production
    tasks.append(bu)

    if elementType=='ID':
        newElementId=fileId
        newElementDetails=indexer.getElement(newElementId)
        cl = ChangeIDElement()
        cl.fileDetails = orFileDetails
        cl.fileId = orFileId
        cl.productionDetails = production
        cl.libraryDetails=indexer.getElement(elementDetails[indexer.INDEX_LIBRARY_ID])
        cl.elementDetails=elementDetails
        cl.newElementName=newElementDetails[indexer.INDEX_ELEMENT_NAME]
        tasks.append(cl)
    else:
        newFileDetails = indexer.getFile(fileId)
        cl = ChangeLibrary()
        cl.fileDetails = orFileDetails
        cl.fileId = orFileId
        cl.newFileDetails = newFileDetails
        cl.productionDetails = production
        cl.libraryDetails = elementDetails
        tasks.append(cl)
    
    session["tasks"]=tasks
    wfile.write("""[]""".encode())

def handleGetCurrentTasks(wfile, request, session):
    tasks = session["tasks"]

    wfile.write("[".encode());
    first = True
    for task in tasks:
        if first==False:
            wfile.write(",".encode())
        first=False
        wfile.write(task.json().encode())
    wfile.write("]".encode());

def handleExecuteOneTask(wfile, request, session):
    tasks = session["tasks"]
    for task in tasks:
        if task.status==INIT:
            task.status=START
            task.execute()
            task.status=FIN
            handleGetCurrentTasks(wfile, request, session)
            return
        
    handleGetCurrentTasks(wfile, request, session)
    return

def handleExecuteCurrentTasks(wfile, request, session):
    tasks = session["tasks"]
    for task in tasks:
        if task.status==INIT:
            task.status=START
            task.execute()
            task.status=FIN
    handleGetCurrentTasks(wfile, request, session)

def handleCommitCurrentTasks(wfile, request, session):
    tasks = session["tasks"]
    for task in tasks:
        if task.status==FIN:
            task.commit()
            task.status=COMMIT
    session["tasks"]=None
        
def handleRollbackCurrentTasks(wfile, request, session):
    tasks = session["tasks"]
    for task in tasks:
        if task.status==FIN:
            task.rollback()
            task.status=ROLLBACK
    session["tasks"]=None

def handleGetMissingLinkSolutions(wfile, request, session):
    productionId=int(session["production_id"])
    elementId=int(request["element_id"])
    elementDetails = indexer.getElement(elementId)
    result = []
    if elementDetails[indexer.INDEX_ELEMENT_TYPE] == 'LI':
        solutions = indexer.queryMissingLinkSolutions(productionId, elementId)
        for solution in solutions:
            result.append(solutionToObject(solution))
    elif elementDetails[indexer.INDEX_ELEMENT_TYPE] == 'ID':
        solutions = indexer.queryMissingLinkSolutionsID(productionId, elementId)
        for solution in solutions:
            result.append(solutionIDToObject(solution))        
    elif elementDetails[indexer.INDEX_ELEMENT_TYPE] == 'IM':
        files = indexer.getProductionFiles(productionId)
        sfn = os.path.basename(elementDetails[indexer.INDEX_ELEMENT_LI_NAME].replace("\\", "/"))
        extension = os.path.splitext(sfn)
        still = []
        for f in files:
            fname = f[indexer.INDEX_FILE_NAME]
            if fname == sfn:
                result.append(solutionToObject(f, 1.0))
            else:
                if not fname.endswith(".blend"):
                    still.append(f)
        files = still
        still=[]
        for f in files:            
            fname = f[indexer.INDEX_FILE_NAME]
            if fname.startswith(extension[0]):
                result.append(solutionToObject(f, 0.75))
            else:
                still.append(f)
        files = still
        still=[]
        for f in files:            
            fname = f[indexer.INDEX_FILE_NAME]
            if fname.endswith(extension[1]):
                result.append(solutionToObject(f, 0.5))
            else:
                still.append(f)
        for f in still:            
            result.append(solutionToObject(f, 0.25))
            
            
    wfile.write(json.dumps(result).encode())

    
######################################################
# Tasks
######################################################
INIT="Created"
START="Started"
FIN="Finished"
COMMIT="Commited"
ROLLBACK="Rollback"

class Task:
    """Task is a base class for migration purposes. """
    
    def __init__(self):
        self.status=INIT
        self.display=True
        
    def json(self):
        result = dict()
        result["task_display"] = self.display
        result["task_status"] = self.status
        result["file_id"] = self.fileId
        result["file_location"] = self.fileDetails[3]
        result["task_description"] = self.description()
        return json.dumps(result)
        
    def commit(self):
        pass
    def rollback(self):
        pass
    
class RenameElement(Task):
    """Migration task for renaming an blender element inside a blend file."""
    
    def description(self):
        return "Rename element ["+self.elementDetails[2]+"] to ["+self.newElementName+"]"

    def execute(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        fileLocation = os.path.join(productionLocation, fileLocation)
        handle = blendfile.openBlendFile(fileLocation, 'r+b')
        stype = self.elementDetails[1]
        
        for libraryblock in handle.FindBlendFileBlocksWithCode(stype):
            name = libraryblock.Get("id.name").split("\0")[0]
            if name == self.elementDetails[2]:
                libraryblock.Set("id.name", self.newElementName)
            
        handle.close()

class RenameIDElement(Task):
    """Migration task for renaming an ID element of a library reference.

        a sourcefile reference an element within a target file. the
        inside the sourcefile a LI exist referencing the target file and
        an ID exist referencing an element inside the target file.

        this task opens the source file. looks for the correct ID (matching ID and LI)
        and renames the name of the ID.
        """

    def description(self):
        return "Change element reference ["+self.elementDetails[2]+"] to ["+self.newElementName+"]"
    
    def execute(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        fileLocation = os.path.join(productionLocation, fileLocation)
        fileLocationDir = os.path.dirname(fileLocation)
        absRefLoc = os.path.normcase(posixpath.normpath(os.path.join(self.productionDetails[2], self.currentFileLocation)))
        handle = blendfile.openBlendFile(fileLocation, 'r+b')
        libRef = 0
        for libraryblock in handle.FindBlendFileBlocksWithCode("LI"):
            relPath = libraryblock.Get("name").split("\0")[0]
            absPath = blendfile.blendPath2AbsolutePath(fileLocation, relPath)
            normPath = os.path.normpath(absPath)
            if normPath==absRefLoc:
                libRef = libraryblock.OldAddress

        for idblock in handle.FindBlendFileBlocksWithCode("ID"):
            lib = idblock.Get("lib")
            if lib == libRef:
                name = idblock.Get("name").split("\0")[0]
                if name == self.elementDetails[2]:
                    idblock.Set("name", self.newElementName)
        
        handle.close()

class MoveLibrary(Task):
    def description(self):
        return "Move library ["+self.currentFileLocation+"] to ["+self.newLocation+"/"+self.currentFilename+"]"

    def execute(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        fileLocation = os.path.join(productionLocation, fileLocation)
        fileLocationDir = os.path.dirname(fileLocation)
        absRefLoc = os.path.normcase(posixpath.normpath(os.path.join(self.productionDetails[2], self.currentFileLocation)))
        
        absNewLoc = os.path.normcase(posixpath.normpath(os.path.join(os.path.join(self.productionDetails[2], self.newLocation), self.currentFilename)))
        newpath = "//"+_relpath(absNewLoc, fileLocationDir)
        handle = blendfile.openBlendFile(fileLocation, 'r+b')
        for libraryblock in handle.FindBlendFileBlocksWithCode("LI"):
            
            relPath = libraryblock.Get("name").split("\0")[0].replace("\\", "/")
            absPath = blendfile.blendPath2AbsolutePath(fileLocation, relPath)
            normPath = os.path.normpath(absPath)
            if normPath==absRefLoc:
                libraryblock.Set("name", newpath)

        for imageblock in handle.FindBlendFileBlocksWithCode("IM"):
            
            relPath = imageblock.Get("name").split("\0")[0].replace("\\", "/")
            absPath = blendfile.blendPath2AbsolutePath(fileLocation, relPath)
            normPath = os.path.normpath(absPath)
            if normPath==absRefLoc:
                imageblock.Set("name", newpath)
            
        handle.close()

class MoveFile(Task):
    """Refactor task for moving a blend file.
the blend file is placed in the new location and all IM and LI references are updated
if the file is a texture this action will only move the file.
"""
    def description(self):
        return "Move file ["+self.currentFileLocation+"] to ["+self.newLocation+"/"+self.currentFilename+"]"
    
    def execute(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        currentFileLocation = os.path.normcase(os.path.normpath(os.path.join(productionLocation, fileLocation)))
        newFileLocation = os.path.normcase(os.path.normpath(os.path.join(productionLocation, os.path.join(self.newLocation, self.currentFilename))))
        dirLocation = os.path.normcase(os.path.normpath(os.path.dirname(newFileLocation)))
        
        #create target directory if not existing
        if not os.path.exists(dirLocation):
            os.makedirs(dirLocation)
            
        shutil.move(currentFileLocation, newFileLocation)

        #update ID and IM tags of blend files.
        if self.currentFilename.endswith(".blend"):
            handle = blendfile.openBlendFile(newFileLocation, 'r+b')

            for libraryblock in handle.FindBlendFileBlocksWithCode("LI"):            
                relPath = libraryblock.Get("name").split("\0")[0]
                absPath = blendfile.blendPath2AbsolutePath(currentFileLocation, relPath)
                normPath = os.path.normcase(os.path.normpath(absPath))
                newRelPath = _relpath(normPath, dirLocation)
                libraryblock.Set("name", "//"+newRelPath)
    
            for libraryblock in handle.FindBlendFileBlocksWithCode("IM"):            
                relPath = libraryblock.Get("name").split("\0")[0]
                if len(relPath)>0:
                    absPath = blendfile.blendPath2AbsolutePath(currentFileLocation, relPath)
                    normPath = os.path.normcase(os.path.normpath(absPath))
                    newRelPath = _relpath(normPath, dirLocation)
                    libraryblock.Set("name", "//"+newRelPath)

            handle.close()
            
        pass
    
    def rollback(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        currentFileLocation = os.path.normcase(os.path.normpath(os.path.join(productionLocation, fileLocation)))
        newFileLocation = os.path.normcase(os.path.normpath(os.path.join(productionLocation, os.path.join(self.newLocation, self.currentFilename))))
        dirLocation = os.path.normpath(os.path.dirname(newFileLocation))
        os.remove(newFileLocation)
        
class RenameLibrary(Task):
    """ rename a library or images reference to a different one."""    
    def execute(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        fileLocation = os.path.join(productionLocation, fileLocation)
        fileLocationDir = os.path.dirname(fileLocation)
        absRefLoc = os.path.normcase(posixpath.normpath(os.path.join(self.productionDetails[2], self.currentFileLocation)))
        absNewLoc = absRefLoc[0:len(absRefLoc)-len(self.currentFilename)]+self.newFilename
        newpath = "//"+_relpath(absNewLoc, fileLocationDir)
        handle = blendfile.openBlendFile(fileLocation, 'r+b')
        for libraryblock in handle.FindBlendFileBlocksWithCode("LI"):
                
            relPath = libraryblock.Get("name").split("\0")[0].replace("\\", "/")
            absPath = blendfile.blendPath2AbsolutePath(fileLocation, relPath)
            normPath = os.path.normpath(absPath)

            if normPath==absRefLoc:
                libraryblock.Set("name", newpath)

        for imageblock in handle.FindBlendFileBlocksWithCode("IM"):
            
            relPath = imageblock.Get("name").split("\0")[0].replace("\\", "/")
            absPath = blendfile.blendPath2AbsolutePath(fileLocation, relPath)
            normPath = os.path.normpath(absPath)
            if normPath==absRefLoc:
                imageblock.Set("name", newpath)
            
        handle.close()
    
    def description(self):
        return "Change library reference ["+self.currentFilename+"] to ["+self.newFilename+"]"

class RenameFile(Task):
    def execute(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        newFileLocation = os.path.join(os.path.dirname(fileLocation),self.newFilename)
        fileLocation = os.path.join(productionLocation, fileLocation)
        newFileLocation = os.path.join(productionLocation, newFileLocation)
        if svn.isKnownSVNFile(fileLocation):
            svn.move(fileLocation, newFileLocation)
        else:
            shutil.move(fileLocation, newFileLocation)

    def rollback(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        newFileLocation = os.path.join(os.path.dirname(fileLocation),self.newFilename)
        fileLocation = os.path.join(productionLocation, fileLocation)
        newFileLocation = os.path.join(productionLocation, newFileLocation)
        shutil.move(newFileLocation, fileLocation)

    def description(self):
        return "Rename ["+self.currentFilename+"] to ["+self.newFilename+"]"
    
class ChangeIDElement(Task):
    """Migration task for renaming an ID element of a library reference.

        a sourcefile reference an element within a target file. the
        inside the sourcefile a LI exist referencing the target file and
        an ID exist referencing an element inside the target file.

        this task opens the source file. looks for the correct ID (matching ID and LI)
        and renames the name of the ID.
        """

    def description(self):
        return "Change element reference ["+self.elementDetails[indexer.INDEX_ELEMENT_NAME]+"] to ["+self.newElementName+"]"
    
    def execute(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        fileLocation = os.path.join(productionLocation, fileLocation)
        absRefLoc = self.libraryDetails[indexer.INDEX_ELEMENT_LI_FILENAME]
        handle = blendfile.openBlendFile(fileLocation, 'r+b')
        libRef = 0
        for libraryblock in handle.FindBlendFileBlocksWithCode("LI"):
            relPath = libraryblock.Get("filename").split("\0")[0]
            if relPath==absRefLoc:
                libRef = libraryblock.OldAddress

        for idblock in handle.FindBlendFileBlocksWithCode("ID"):
            lib = idblock.Get("lib")
            if lib == libRef:
                name = idblock.Get("name").split("\0")[0]
                if name == self.elementDetails[indexer.INDEX_ELEMENT_NAME]:
                    idblock.Set("name", self.newElementName)
        
        handle.close()
class ChangeLibrary(Task):
    """ change the library reference of a blend file.
    self.productionDetails
    self.fileDetails (file)
    self.libraryDetails (element type=LI)
    self.newFileDetails (file)
    """    
    def execute(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        fileLocation = os.path.join(productionLocation, fileLocation)
        fileLocationDir = os.path.dirname(fileLocation)
        absNewLoc = os.path.normcase(posixpath.normpath(os.path.join(self.productionDetails[2], self.newFileDetails[indexer.INDEX_FILE_LOCATION])))
        newpath = "//"+_relpath(absNewLoc, fileLocationDir)
        handle = blendfile.openBlendFile(fileLocation, 'r+b')
        if self.libraryDetails[indexer.INDEX_ELEMENT_TYPE] == 'LI':
            for libraryblock in handle.FindBlendFileBlocksWithCode("LI"):    
                path = libraryblock.Get("filepath").split("\0")[0].replace("\\", "/")
                if path == self.libraryDetails[indexer.INDEX_ELEMENT_LI_FILENAME]:
                    libraryblock.Set("name", newpath)
        elif self.libraryDetails[indexer.INDEX_ELEMENT_TYPE] == 'IM':
            for libraryblock in handle.FindBlendFileBlocksWithCode("IM"):    
                path = libraryblock.Get("name").split("\0")[0]
                if path == self.libraryDetails[indexer.INDEX_ELEMENT_LI_FILENAME]:
                    libraryblock.Set("name", newpath)
                
        handle.close()
    
    def description(self):
        return "Change library reference to ["+self.newFileDetails[3]+"]"

    
class BackupFile(Task):
    def __init__(self):
        Task.__init__(self)
        self.display=False
        
    def execute(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        newFileLocation = fileLocation+".bak"
        fileLocation = os.path.join(productionLocation, fileLocation)
        newFileLocation = os.path.join(productionLocation, newFileLocation)
        shutil.copy(fileLocation, newFileLocation)
    
    def description(self):
        return "Backup ["+self.fileDetails[3]+"]"

    def commit(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        newFileLocation = fileLocation+".bak"
        newFileLocation = os.path.join(productionLocation, newFileLocation)
        os.remove(newFileLocation)
        
    def rollback(self):
        productionLocation = self.productionDetails[2]
        fileLocation = self.fileDetails[3]
        newFileLocation = fileLocation+".bak"
        fileLocation = os.path.join(productionLocation, fileLocation)
        newFileLocation = os.path.join(productionLocation, newFileLocation)
        shutil.copy(newFileLocation, fileLocation)
        os.remove(newFileLocation)
    

