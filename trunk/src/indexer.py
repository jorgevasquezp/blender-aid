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
import os
import settings
from settings import SQLITE3_CONNECTIONURL
import blendfile
from blendfile import BlendFile
import sqlite3
import logging

try:
    from os.path import relpath as _relpath
except:
    print("python < 2.6: import custom relpath")
    from bautil import relpath as _relpath

log = logging.getLogger("indexer")


G_FILE_COMPRESS = 1 << 1

def updateIndex(productionId):
    """Updates the index of a production

step 1a: make a list of all files inside the production directory including their last modificationtime.
    do not add hidden files (start with a dot)
step 1b: make a list of all files already indexed

step 2a: check which files needs to be updated (are changed)
step 2b: check which files are new files
step 2c: check which files have been removed

step 3a: index new files
step 3b: reindex modified files
stpe 3c: remove removed files

step 4: determine dependancies

    """
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    productionResult = connection.execute("select * from production where id=?", [productionId]).fetchone()

    if productionResult == None: 
        log.warning("production "+str(productionId)+" not found")
        return
    
    productionName= productionResult[1]
    productionDir= productionResult[2]

# step 1a: make a list of all files inside the production directory including their last modificationtime.
# do not add hidden files (start with a dot)
    filesOnFileSystem = []
    for root, dirs, files in os.walk(productionDir):
        for file in files:
            if file.endswith(".blend") or file.endswith(".png") or file.endswith(".gif") or file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".tga") or file.endswith(".exr"):
                absFile = os.path.join(root, file)
                #log.debug("adding "+absFile)
                filesOnFileSystem.append([absFile, int(os.path.getmtime(absFile))])
            else:
                #log.warning("!!!skipping:" +file);
                pass

# step 1b: make a list of all files already indexed
    fileInDatabase =[]
    for file in connection.execute("select * from file where production_id = ?", [productionId]).fetchall():
        absFile = os.path.join(productionDir, file[3])        
        #log.debug("adding "+absFile)        
        fileInDatabase.append((absFile, int(file[4])))
        
# step 2a: check which files needs to be updated (are changed)
    fileToBeUpdated=[]
    for fsFile in filesOnFileSystem:
        for dbFile in fileInDatabase:
            if fsFile[0] == dbFile[0]:
                if fsFile[1]>dbFile[1]:
                    # file has been changed
                    log.debug("modified: "+str(fsFile))
                    fileToBeUpdated.append(fsFile)
                    
# step 2b: check which files are new files
    fileToBeAdded=[]
    for fsFile in filesOnFileSystem:
        existInDb=False
        for dbFile in fileInDatabase:
            if fsFile[0] == dbFile[0]:
                existInDb=True
        if not existInDb:
            log.debug("new: "+str(fsFile))
            fileToBeAdded.append(fsFile)
    
# step 2c: check which files have been removed
    fileToBeRemoved=[]
    for dbFile in fileInDatabase:
        existOnFS=False
        for fsFile in filesOnFileSystem:
            if fsFile[0] == dbFile[0]:
                existOnFS=True
        if not existOnFS:
            log.debug("remove: "+str(dbFile))
            fileToBeRemoved.append(dbFile)

#step 3a: index new files
    for file in fileToBeAdded:
        indexNewFile(connection, productionId, productionDir, file[0]);
    connection.commit()
        
#step 3b: reindex modified files
    for file in fileToBeUpdated:
        indexExistingFile(connection, productionId, productionDir, file[0]);
    connection.commit()
#stpe 3c: remove removed files
    for file in fileToBeRemoved:
        indexOldFile(connection, productionId, productionDir, file[0]);
    connection.commit()
        
#step 4: determine dependancies
#do only when changes have happened
    if len(fileToBeAdded)+ len(fileToBeRemoved)+len(fileToBeUpdated) > 0:
        log.debug("update dependancies");
        #clear all reference file id from a production
        connection.execute("update element set reference_file_id=null where file_id in (select id from file where production_id=?)", [productionId]);
        #fill direct references
        for dbFile in connection.execute("select id, location from file where production_id=?", [productionId]).fetchall():
            #update texture
            connection.execute("update element set reference_file_id=? where li_name=? and type='IM' and file_id in (select id from file where production_id=?)", [dbFile[0], dbFile[1], productionId]);
            
            #update library
            connection.execute("update element set reference_file_id=? where li_name=? and type='LI' and file_id in (select id from file where production_id=?)", [dbFile[0], dbFile[1], productionId]);
#        connection.commit()
        #fill in-direct references
        #update id
        for libElement in connection.execute("select element.reference_file_id, element.li_name, element.li_filename, element.id from element, file where element.file_id=file.id and file.production_id=? and element.type='LI'", [productionId]):
            connection.execute("update element set reference_file_id=?, li_name=?, li_filename=? where library_id=?", libElement)

        log.debug("finished indexing");
    
    connection.commit();
    connection.close()

def indexExistingFile(connection, productionId, productionDir, file):
    """index existing file.
    TODO: make sure that file_id is same"""
    indexOldFile(connection, productionId, productionDir, file)
    indexNewFile(connection, productionId, productionDir, file)
    
def indexOldFile(connection, productionId, productionDir, file):
    """remove a file from production scope"""
    log.info("remove file "+file);
    relpath = _relpath(file, productionDir)
# find file
    dbFile = connection.execute("select id from file where location=?", [relpath]).fetchone()
    connection.execute("delete from element where file_id=?", dbFile)
    connection.execute("delete from file where id=?", dbFile)
#    connection.commit()
    

def indexNewFile(connection, productionId, productionDir, file):
    """index a new file"""
    log.info("indexing file "+file);
    newId = connection.execute("select max(id)+1 from file").fetchone()[0]
    if newId == None:
        newId=0;
    
    connection.execute("insert into file values (?,?,?,?,?)", 
        [newId, 
        productionId, 
        os.path.basename(file), 
        _relpath(file, productionDir), 
        int(os.path.getmtime(file))])

    if file.endswith(".blend"):
        bf=blendfile.openBlendFile(file)
        
# index the file
        firstElementId = connection.execute("select max(id)+1 from element").fetchone()[0]
        offsetElementId=0
        if firstElementId == None:
            firstElementId=0;

        bfVersion = bf.Header.Version
        bfPointerSize = bf.Header.PointerSize
        bfLittleEndianness = bf.Header.LittleEndianness
        bfCompressed = bf.compressed
        bfCurrentScenePointer = None
        bfElementId = firstElementId
        offsetElementId = offsetElementId + 1
        
        for block in bf.FindBlendFileBlocksWithCode("GLOB"):
            bfCurrentScenePointer = block.Get("curscene")
            #flags=block.Get("fileflags")
            #bfCompressed = (flags & G_FILE_COMPRESS) == G_FILE_COMPRESS
            #print(flags, bfCompressed)

        for block in bf.FindBlendFileBlocksWithCode("SC"):
            scId = firstElementId + offsetElementId
            offsetElementId = offsetElementId + 1 
            if block.Header.OldAddress == bfCurrentScenePointer:
                bfCurrentSceneId = scId

            scName = block.Get("id.name");
            scWidth = block.Get("r.xsch");
            scHeight = block.Get("r.ysch");
            scSize = block.Get("r.size");
            scXparts = block.Get("r.xparts");
            scYparts = block.Get("r.yparts");
            scStartFrame = block.Get("r.sfra");
            scEndFrame = block.Get("r.efra");
            scStep = block.Get("frame_step");
            scImageType = formatImageType(block.Get("r.imtype"))
            
            
            connection.execute("insert into element (id, file_id, blendfile_id, name, type, sc_width, sc_height, sc_size, sc_xparts, sc_yparts, sc_startframe, sc_endframe, sc_framestep, sc_outputtype) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                [scId, 
                newId, 
                bfElementId, 
                scName, 
                scName[0:2],
                scWidth, 
                scHeight, 
                scSize, 
                scXparts, 
                scYparts, 
                scStartFrame, 
                scEndFrame,
                scStep, 
                scImageType])

        for block in bf.FindBlendFileBlocksWithCode("MA"):
            scId = firstElementId + offsetElementId
            offsetElementId = offsetElementId + 1 

            scName = block.Get("id.name");        
            
            connection.execute("insert into element (id, file_id, blendfile_id, name, type) values (?,?,?,?,?)", 
                [scId, 
                newId, 
                bfElementId, 
                scName, 
                scName[0:2],
            ])
        for block in bf.FindBlendFileBlocksWithCode("OB"):
            sdna = block.Header.SDNAIndex
            dnaIndex = block.Header.SDNAIndex
            dnaStruct = block.File.Catalog.Structs[dnaIndex]
            if dnaStruct.Type.Name == 'Object':
                scId = firstElementId + offsetElementId
                offsetElementId = offsetElementId + 1 

                scName = block.Get("id.name");        
            
                connection.execute("insert into element (id, file_id, blendfile_id, name, type) values (?,?,?,?,?)", 
                    [scId, 
                    newId, 
                    bfElementId, 
                    scName, 
                    scName[0:2],
                ])

            
            
        for type in ["GR", "ME", "TE", "WO", "IP", "PA", "LA", "CA", "AR", "AC"]:
            for block in bf.FindBlendFileBlocksWithCode(type):
                scId = firstElementId + offsetElementId
                offsetElementId = offsetElementId + 1 

                scName = block.Get("id.name");        
            
                connection.execute("insert into element (id, file_id, blendfile_id, name, type) values (?,?,?,?,?)", 
                    [scId, 
                    newId, 
                    bfElementId, 
                    scName, 
                    scName[0:2],
                ])
                
        for block in bf.FindBlendFileBlocksWithCode("IM"):
            scId = firstElementId + offsetElementId
            offsetElementId = offsetElementId + 1 

            scName = block.Get("id.name");        
            liName = block.Get("name");        
            liName = liName.split("\0")[0];
            liName = determineProductionLocation(productionDir, file, liName)
            if liName != None and liName != '':
            
                connection.execute("insert into element (id, file_id, blendfile_id, name, type, li_name, li_filename) values (?,?,?,?,?,?,?)", 
                    [scId, 
                    newId, 
                    bfElementId, 
                    scName, 
                    scName[0:2],
                    liName, 
                    liName
                ])
        
        libref = dict()
        
        for block in bf.FindBlendFileBlocksWithCode("LI"):
            scId = firstElementId + offsetElementId
            offsetElementId = offsetElementId + 1 

            liOldAddress = block.Header.OldAddress
            libref[liOldAddress] = scId
            scName = block.Get("id.name");        
            liName = block.Get("name");
            
            liName = determineProductionLocation(productionDir, file, liName)
            liFilename = block.Get("filename"); #absolute path when saved?
            connection.execute("insert into element (id, file_id, blendfile_id, name, type, li_name, li_filename) values (?,?,?,?,?,?,?)", 
                [scId, 
                newId, 
                bfElementId, 
                scName, 
                scName[0:2],
                liName,
                liFilename
            ])

        for block in bf.FindBlendFileBlocksWithCode("ID"):
            scId = firstElementId + offsetElementId
            offsetElementId = offsetElementId + 1 

            scName = block.Get("name");        
            liOldAddress = block.Get("lib")
            liId = libref[liOldAddress]
            
            connection.execute("insert into element (id, file_id, blendfile_id, name, type, library_id) values (?,?,?,?,?,?)", 
                [scId, 
                newId, 
                bfElementId, 
                scName, 
                "ID",
                liId
            ])
            
        connection.execute("insert into element (id, file_id, type, bf_current_scene_id, bf_version, bf_pointersize, bf_littleendian, bf_compressed) values (?,?,?,?,?,?,?,?)", 
            [bfElementId, 
            newId, 
            "BF", 
            bfCurrentSceneId, 
            bfVersion,
            bfPointerSize,
            bfLittleEndianness,
            bfCompressed])
        
        bf.close()
#determine the relative production location of a blender path.basename
def determineProductionLocation(productionDir, productionFile, blenderPath):
    productionFileDir=os.path.dirname(productionFile)
    if blenderPath.startswith("//"):
        relpath=os.path.normpath(blenderPath[2:].split("\0")[0]).replace("\\", "/")
        abspath = os.path.join(productionFileDir, relpath)
        return _relpath(abspath, productionDir)
    
    return blenderPath

def formatImageType(value):
    trans=[
        "TGA", "IRIS", "HAMX", "FTYPE", "JPEG", "MOV", "UNKOWN", "IRIZ", "UNKOWN", "UNKOWN", "UNKOWN", "UNKOWN", "UNKOWN", "UNKOWN", "TGA", "AVI", "AVI", "PNG", "AVI", "MOV", "BMP", "HDR", "TIFF",
        "EXR", "FFMPEG", "FRAMESERVER", "CINEON", "DPX", "MULTILAYER", "DDS"
    ]
    return trans[value]

def getAllScenes(productionId):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    query = """select file.location, bf.bf_version, el.name, el.sc_width, el.sc_height, el.sc_size, el.sc_startframe, el.sc_endframe, el.sc_framestep, el.sc_xparts, el.sc_yparts, bf.bf_current_scene_id=el.id, el.sc_outputtype, file.id, bf.bf_pointersize, bf.bf_littleendian, bf.bf_compressed from element el, element bf, file file where el.blendfile_id=bf.id and el.file_id=file.id and el.type='SC' and file.production_id=? order by file.location"""
    result = connection.execute(query, [productionId]).fetchall();
    connection.close()
    return result

def getProduction(productionId):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    query = """select * from production where id=?"""
    result = connection.execute(query, [productionId]).fetchone();
    connection.close()
    return result

SQL_REMOVEACTIVEFLAG="""update production set active=0"""
SQL_ACTIVATEPRODUCTION="""update production set active=1 where id=?"""
def activateProduction(productionId):
    """Set the active production"""
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    connection.execute(SQL_REMOVEACTIVEFLAG, []);
    connection.execute(SQL_ACTIVATEPRODUCTION, [productionId]);
    connection.commit()
    connection.close()
    return None

SQL_GETACTIVEPRODUCTION="""select * from production where active=1"""
def getActiveProduction():
    """Get the active production"""
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    result = connection.execute(SQL_GETACTIVEPRODUCTION, []).fetchone();
    connection.close()
    return result

def getFile(fileId):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    query = """select * from file where id=?"""
    result = connection.execute(query, [fileId]).fetchone();
    connection.close()
    return result

SQL_PRODUCTION_ALL = """select * from production order by name"""
def getAllProductions():
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)    
    result = connection.execute(SQL_PRODUCTION_ALL, []).fetchall();
    connection.close()
    return result

def insertProduction(productionName, productionLocation):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    query = """insert into production values (null, ?, ?, 0)"""
    result = connection.execute(query, [productionName, productionLocation]);
    connection.commit();
    connection.close()
    
def deleteProduction(productionId):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    query = """delete from element where element.file_id in (select id from file where production_id=?)"""
    result = connection.execute(query, [productionId]);
    query = """delete from file where production_id=?"""
    result = connection.execute(query, [productionId]);
    query = """delete from production where id=?"""
    result = connection.execute(query, [productionId]);
    connection.commit();
    connection.close()

SQL_FILE_USE_ELEMENT="""select file_id from element where type='ID' and reference_file_id=? and name=?"""
def getReferenceToElement(productionId, fileId, elementName):
    """Get all references to a blender element. (ID links)."""
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    result = connection.execute(SQL_FILE_USE_ELEMENT, [fileId, elementName]).fetchall();
    connection.close()
    return result

SQL_ELEMENT_DETAILS="""select id, type, name from element where id=?"""
def getElementDetails(elementId):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    result = connection.execute(SQL_ELEMENT_DETAILS, [elementId]).fetchone();
    connection.close()
    return result

def getProductionFiles(productionId):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    query = """select * from file where production_id=? order by location"""
    result = connection.execute(query, [productionId]).fetchall();
    connection.close()
    return result
    
def getFileDetails(fileId):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    query="select file.id, file.name, file.location, sc.name, sc.sc_width, sc.sc_height, sc.sc_outputtype, sc.sc_xparts, sc.sc_yparts, sc.sc_startframe, sc.sc_endframe from element as sc, element as bf, file where file.id=sc.file_id and sc.id=bf.bf_current_scene_id and sc.file_id=? and bf.file_id=? and file.id=?;"
    result = connection.execute(query, [fileId,fileId,fileId]).fetchone()
    connection.close()
    return result
    
def getFileElements(fileID):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    query = "select * from element where file_id=? and type not in ('BF', 'LI', 'ID', 'IM','IP')"
    result = connection.execute(query, [fileID]).fetchall()
    connection.close()
    return result

def getFileElementByName(fileId, elementName):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    query = "select * from element where file_id=? and name=?"
    result = connection.execute(query, [fileId, elementName]).fetchall()
    connection.close()
    return result

def getFileReferences(fileID):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    query = "select li_name, substr(name,0,2) as etype, name, reference_file_id from element where type in ('ID', 'IM') and file_id=?;"
    result = connection.execute(query, [fileID]).fetchall()
    connection.close()
    return result

def getFileUsedBy(fileID):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    query = "select file.location, substr(element.name,0,2) as etype, element.name, file_id from element, file where file.id=element.file_id and type in ('ID', 'IM') and reference_file_id=?;"
    result = connection.execute(query, [fileID]).fetchall()
    connection.close()
    return result

SQL_UNCOMPRESSED_FILES = """select file.* from element,file where element.file_id=file.id and element.type="BF" and not element.bf_compressed and file.production_id = ?;"""
def getUncompressedFiles(productionId):
    """ find all uncompressed blend files of a production
    """
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    result = connection.execute(SQL_UNCOMPRESSED_FILES, [productionId]).fetchall();
    connection.close()
    return result


# all dependancy queries    
def queryDependancy(productionId, filter):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    if filter=="all":
        query="select file.location, element.li_name, substr(element.name, 0, 2) as etype, element.name, element.file_id, element.reference_file_id from element, file where element.file_id =file.id and element.type in ('ID','IM') and file.production_id=?;"
    else:
        f=[]
        for t in filter.split(","):
            f.append("'"+t+"'")
        nFilter = ",".join(f)
        query="select file.location, element.li_name, substr(element.name, 0, 2) as etype, element.name, element.file_id, element.reference_file_id from element, file where element.file_id =file.id and element.type in ('ID','IM') and file.production_id=? and etype in ("+nFilter+");"
        
    result = connection.execute(query, [productionId]).fetchall()
    connection.close()
    return result

def queryDependancyUses(productionId, fileId, filter):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    todo=[fileId]
    done=[]
    result = []
    
    if filter=="all":
        query="select file.location, element.li_name, substr(element.name, 0, 2) as etype, element.name, element.file_id, element.reference_file_id from element, file where element.file_id=file.id and element.type in ('ID','IM') and file.id=?;"
    else:
        f=[]
        for t in filter.split(","):
            f.append("'"+t+"'")
        nFilter = ",".join(f)
        query="select file.location, element.li_name, substr(element.name, 0, 2) as etype, element.name, element.file_id, element.reference_file_id from element, file where element.file_id=file.id and element.type in ('ID','IM') and file.id=? and etype in ("+nFilter+");"
            
    while len(todo)!=0:
        item = todo.pop()
        if item not in done:
            done.append(item)
        
            for line in connection.execute(query, [item]).fetchall():
                result.append(line)
                if line[5]!= None:
                    todo.append(line[5])
    
    connection.close()
    return result
    
def queryDependancyUsed(productionId, fileId, filter):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    todo=[fileId]
    done=[]
    result = []
    
    if filter=="all":
        query="select file.location, element.li_name, substr(element.name, 0, 2) as etype, element.name, element.file_id, element.reference_file_id from element, file where element.file_id=file.id and element.type in ('ID','IM') and element.reference_file_id=?;"
    else:
        f=[]
        for t in filter.split(","):
            f.append("'"+t+"'")
        nFilter = ",".join(f)
        query="select file.location, element.li_name, substr(element.name, 0, 2) as etype, element.name, element.file_id, element.reference_file_id from element, file where element.file_id=file.id and element.type in ('ID','IM') and element.reference_file_id=? and etype in ("+nFilter+");"
            
    while len(todo)!=0:
        item = todo.pop()
        if item not in done:
            done.append(item)
        
            for line in connection.execute(query, [item]).fetchall():
                result.append(line)
                if line[4]!= None:
                    todo.append(line[4])
    
    connection.close()
    return result
    
def queryDependancyNeighbour(productionId, fileId, filter):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)

    result = []
    
    if filter=="all":
        query1="select file.location, element.li_name, substr(element.name, 0, 2) as etype, element.name, element.file_id, element.reference_file_id from element, file where element.file_id=file.id and element.type in ('ID','IM') and element.reference_file_id=?;"
        query2="select file.location, element.li_name, substr(element.name, 0, 2) as etype, element.name, element.file_id, element.reference_file_id from element, file where element.file_id=file.id and element.type in ('ID','IM') and file.id=?;"
    else:
        f=[]
        for t in filter.split(","):
            f.append("'"+t+"'")
        nFilter = ",".join(f)
        query1="select file.location, element.li_name, substr(element.name, 0, 2) as etype, element.name, element.file_id, element.reference_file_id from element, file where element.file_id=file.id and element.type in ('ID','IM') and element.reference_file_id=? and etype in ("+nFilter+");"
        query2="select file.location, element.li_name, substr(element.name, 0, 2) as etype, element.name, element.file_id, element.reference_file_id from element, file where element.file_id=file.id and element.type in ('ID','IM') and file.id=? and etype in ("+nFilter+");"
            
    
    for line in connection.execute(query1, [fileId]).fetchall():
        result.append(line)
    for line in connection.execute(query2, [fileId]).fetchall():
        result.append(line)
    
    connection.close()
    return result
    
#consistency errors    
def getConsistencyErrors(productionId):
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    result = []
    #missing libraries.
    query = """select file.location, element.li_name, element.file_id from element, file where element.type='LI' and element.reference_file_id is null and element.file_id=file.id and file.production_id=?"""
    tempresult = connection.execute(query, [productionId]).fetchall();
    for line in tempresult:
        result.append([line[2],line[0],line[1]])

    query = """select file.location, element.li_name, element.file_id, element.name from element, file where element.type='ID' and element.reference_file_id is null and element.file_id=file.id and file.production_id=?"""
    tempresult = connection.execute(query, [productionId]).fetchall();
    for line in tempresult:
        result.append([line[2],line[0],line[1]+"#"+line[3]])

    query = """select file.location, element.li_name, element.file_id from element, file where element.type='IM' and element.reference_file_id is null and element.file_id=file.id and file.production_id=?"""
    tempresult = connection.execute(query, [productionId]).fetchall();
    for line in tempresult:
        if line[1] != None and len(line[1])>0:
            if line[1]!='Untitled':
                result.append([line[2],line[0],line[1]])
    
    connection.close()
    return result


# setup database
def setup():
    connection = sqlite3.connect(settings.SQLITE3_CONNECTIONURL)
    connection.execute("""create table if not exists production (
        id integer primary key autoincrement,
        name text,
        location text,
        active int
    )""")
    connection.execute("""create table if not exists file (
        id int primary key,
        production_id int,
        name text,
        location text,
        lastupdate bigint
    )""")
    connection.execute("""create table if not exists element (
        id int primary key,
        file_id int,
        blendfile_id int,
        library_id int,
        reference_file_id int,
        name text,
        type text,
        bf_current_scene_id int,
        bf_pointersize int,
        bf_littleendian bool,
        bf_version int,
        bf_compressed bool,
        sc_width int,
        sc_height int, 
        sc_size int,
        sc_xparts int,
        sc_yparts int, 
        sc_outputtype text,
        sc_outputlocation text,
        sc_startframe int,
        sc_endframe int,
        sc_framestep int,
        sc_layers int, 
        li_name text, 
        li_filename text
        
    )""")
    
    connection.execute("""create index if not exists IN_EL_NAME on element (name, type)""");
    connection.execute("""create index if not exists IN_EL_LI_NAME on element (li_name)""");
    connection.execute("""create index if not exists IN_EL_LIB_ID on element (library_id)""");
    connection.execute("""create index if not exists IN_EL_BF_ID on element (blendfile_id)""");
    connection.execute("""create index if not exists IN_EL_FILE_ID on element (file_id)""");
    connection.execute("""create index if not exists IN_FI_LOCATION on file (location)""");

    connection.commit()
    connection.close()
    
