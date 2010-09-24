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
# (c) 2009, At Mind B.V. - Jeroen Bakker, M.Dewanchand


######################################################
# Importing modules
######################################################
import indexer
import svn
import pysvn
import os.path as path
from factory import *
from datetime import datetime
try:
    import json
except:
    import simplejson as json

def handleGetAll(wfile, request, session):
    """Service to retrieve a list of all available productions
    """
    productions = indexer.getAllProductions()
    list = []
    for production in productions:
        list.append(productionToObject(production))
    wfile.write(json.dumps(list).encode())

def handleSvnUpdate(wfile, request, session):
    """Service to retrieve a list of all available productions
    """
    productionId = request["production_id"]
    production = indexer.getProduction(productionId)
    svn.svnUpdate(production[2], production[5], production[6])
    wfile.write(json.dumps([]).encode())
    
def handleActivateProduction(wfile, request, session):
    productionId = request["production_id"]
    indexer.activateProduction(productionId)
    wfile.write(json.dumps(None).encode())
    
def handleGetProductionView(wfile, request, session):
    """Service to retrieve all production level information
    being:
        production
        files of the production
        scenes of the production
        missing links of the production
    """
    production = indexer.getActiveProduction()
    result = []
    if production is not None:
        productionId=production[0]
        session["production_id"]=productionId #fix for dependancy services..
        indexer.updateIndex(productionId)
        files = indexer.getProductionFiles(productionId)
        scenes = indexer.getAllScenes(productionId)
        errors = indexer.getConsistencyErrors(productionId)
        try:
            states = svn.svnStat(production[2])
        except pysvn.ClientError, e:
            states=[]
        temp = {}
        assignedFiles=[]
        for stat in states:
            if stat.entry is None:
                temp[stat.path] = [None,None,str(stat.text_status)]
            else:
                temp[stat.path] = [stat.entry.commit_revision.number,stat.entry.commit_author,str(stat.text_status)]
        for file in files:
            abspath = path.join(production[2], file[3])
            if abspath in temp:
                ass =[file, temp[abspath]]
            else:
                ass =[file, ["","","unversioned"]]
            assignedFiles.append(ass)   
        result.append(productionToObject(production))
        result.append(files2ToObject(assignedFiles))
        result.append(scenesToObject(scenes))
        result.append(errorsToObject(errors))
    wfile.write(json.dumps(result).encode())
    
def handleGetFileView(wfile, request, session):
    """Service to retrieve all file level information
    being:
        production
        file
        elements of the file
        references of the file
        used by of the file
    """
    productionId=int(request["production_id"])
    fileId=int(request["file_id"])

    indexer.updateIndex(productionId)

    production = indexer.getProduction(productionId)
    file = indexer.getFileDetails(fileId)
    elements = indexer.getFileElements(fileId)
    references = indexer.getFileReferences(fileId)
    usedby = indexer.getFileUsedBy(fileId)
    
    result = []
    result.append(productionToObject(production))
    if file != None:
        result.append(fileDetailToObject(file))
    else:
        file=indexer.getFile(fileId)
        result.append(fileToObject(file))
        
    result.append(elementsToObject(elements))
    result.append(referencesToObject(references))
    result.append(usedbysToObject(usedby))
    wfile.write(json.dumps(result).encode())
    
    
def handleDelete(wfile, request, session):
    productionId=int(request["production_id"])
    indexer.deleteProduction(productionId);
    wfile.write("[]\r\n".encode());
    
def handleAdd(wfile, request, session):
    productionName=request["production_name"]
    productionLocation=request["production_location"]
    productionSvnUrl=request["production_svnurl"]
    productionSvnUsername=request["production_svnusername"]
    productionSvnPassword=request["production_svnpassword"]
    if productionSvnUrl=="":
        if not path.isdir(productionLocation):
            wfile.write("[\"error\":\"location doe not exist or is not a directory\"]\r\n".encode());
        else:
            indexer.insertProduction(productionName, productionLocation);
            wfile.write("[]\r\n".encode());
    else:
        result, additional = svn.testWorkingFolder(productionLocation, productionSvnUrl);
        if result in [svn.SVNNOBINDING, svn.SVNNOWORKINGFOLDER]:
            #ok, checkout needed do checkout
            svn.svnCheckout(productionLocation, productionSvnUrl, productionSvnUsername, productionSvnPassword);
            indexer.insertProduction(productionName, productionLocation, productionSvnUrl, productionSvnUsername, productionSvnPassword);
            wfile.write("[]\r\n".encode());
        elif result in [svn.SVNURLSAME]:
            #ok, do nothing
            indexer.insertProduction(productionName, productionLocation, productionSvnUrl, productionSvnUsername, productionSvnPassword);
            wfile.write("[]\r\n".encode());
        elif result in [svn.SVNURLDIFF]:
            #error, user entry
            wfile.write("[\"error\":\"Working folder contains content from a different SVN URL\"]\r\n".encode());
        elif result in [svn.SVNWORKINGFOLDERISFILE]:
            #error, user entry
            wfile.write("[\"error\":\"Working folder is a file\"]\r\n".encode());

def handleSvnAdd(wfile, request, session):
    file_id = request["file_id"]
    addAll = request["add_all"]
    result = indexer.getFile(file_id)
    production_id = result[1]
    file_name = result[2]
    rel_file_path = result[3]
    production_result = indexer.getProduction(production_id)
    production_path = production_result[2]
    location = path.join(production_path, rel_file_path)
    svn.svnAdd(location)
    return

def handleSvnRevert(wfile, request, session):
    file_id = request["file_id"]
    revertAll = request["revert_all"]
    production = request["production_id"]
    if file_id==None and revertAll and production!=None:
        production_result = indexer.getProduction(production)
        production_path = production_result[2]
        svn.svnRevert(production_path)
    elif file_id!=None and not revertAll:
        result = indexer.getFile(file_id)
        production_id = result[1]
        file_name = result[2]
        rel_file_path = result[3]
        location = path.join(production_path, rel_file_path)
        svn.svnRevert(location)
    return
