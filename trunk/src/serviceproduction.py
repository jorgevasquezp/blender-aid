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
import indexer
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
    
        result.append(productionToObject(production))
        result.append(filesToObject(files))
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
    
def productionToObject(production):
    """This method will convert a production record to a production object
    the result will be a dictionary containing the fields of the production
    """
    result = {}
    result["production_id"]=production[0]
    result["production_name"]=production[1]
    result["production_location"]=production[2]
    return result

def filesToObject(files):
    """This method will convert a list of file records to a list of file object
    the result will be an array
    """
    result = []
    for file in files:
        result.append(fileToObject(file))
    return result

def fileToObject(file):
    """This method will convert a file record to a file object
    """
    result = {}
    result["file_id"]=file[0]
    result["file_name"]=file[2]
    result["file_location"]=file[3]
    return result

def scenesToObject(scenes):
    """This method will convert a list of file records to a list of file object
    the result will be an array
    """
    result = []
    for scene in scenes:
        result.append(sceneToObject(scene))
    return result

def sceneToObject(scene):
    """This method will convert a scene record to a scene object
    """
    result = {}
    result["file_id"]=scene[13]
    result["blend_file"]=scene[0]
    result["blend_version"]=scene[1]
    result["blend_pointersize"]=scene[14]
    result["blend_littleendian"]=scene[15]
    result["blend_compressed"]=scene[16]
    result["scene_name"]=scene[2]
    result["scene_resolution"]=str(scene[3])+"x"+str(scene[4])
    result["scene_size"]=scene[5]
    result["scene_outputtype"]=scene[12]
    result["scene_startframe"]=scene[6]
    result["scene_endframe"]=scene[7]
    result["scene_step"]=1
#       wfile.write("\"scene_step\":"+str(scene[6])+",");
    result["scene_rt"]=1
    result["scene_xparts"]=scene[9]
    result["scene_yparts"]=scene[10]
    result["scene_active"]=scene[11]
    return result

def errorsToObject(errors):
    """This method will convert a list of error records to a list of error object
    the result will be an array
    """
    result = []
    for err in errors:
        result.append(errorToObject(err))
    return result

def errorToObject(err):
    """This method will convert a error record to a error object
    """
    result = {}
    result["file_location"]=err[1]
    result["missing_file_location"]=err[2]
    result["file_id"]=err[0]
    return result

def fileDetailToObject(file):
    result={}
    result["file_id"]=file[0]
    result["file_name"]=file[1]
    result["file_location"]=file[2]
    result["scene_name"]=file[3]
    result["scene_resolution"]=str(file[4])+"x"+str(file[5])
    result["scene_outputtype"]=file[6]
    result["scene_xparts"]=file[7]
    result["scene_yparts"]=file[8]
    result["scene_startframe"]=file[9]
    result["scene_endframe"]=file[10]
    return result

def elementsToObject(elements):
    """This method will convert a list of file records to a list of file object
    the result will be an array
    """
    result = []
    for element in elements:
        result.append(elementToObject(element))
    return result

def elementToObject(element):
    """This method will convert a file record to a file object
    """
    result = {}
    result["element_id"]=element[0]
    result["element_name"]=element[5]
    result["element_type"]=element[6]
    return result

def referencesToObject(references):
    """This method will convert a list of file records to a list of file object
    the result will be an array
    """
    result = []
    for reference in references:
        result.append(referenceToObject(reference))
    return result

def referenceToObject(reference):
    """This method will convert a file record to a file object
    """
    result = {}
    result["file_id"]=reference[3]
    result["file_location"]=reference[0]
    result["element_name"]=reference[2]
    result["element_type"]=reference[1]
    
    return result    
def usedbysToObject(usedbys):
    """This method will convert a list of file records to a list of file object
    the result will be an array
    """
    result = []
    for usedby in usedbys:
        result.append(usedbyToObject(usedby))
    return result

def usedbyToObject(usedby):
    """This method will convert a file record to a file object
    """
    result = {}
    result["file_id"]=usedby[3]
    result["file_location"]=usedby[0]
    result["element_name"]=usedby[2]
    result["element_type"]=usedby[1]
    return result   

#def handleGet(wfile, request, session):
#    productionId=int(request["production_id"])
#    production = indexer.getProduction(productionId)
#    wfile.write("[{");
#    wfile.write("\"production_id\":\""+str(production[0])+"\",");
#    wfile.write("\"production_name\":\""+production[1]+"\",");
#    wfile.write("\"production_location\":\""+production[2]+"\"");
#    wfile.write("}]\r\n");
    
def handleDelete(wfile, request, session):
    productionId=int(request["production_id"])
    indexer.deleteProduction(productionId);
    wfile.write("[]\r\n".encode());
    
def handleAdd(wfile, request, session):
    productionName=request["production_name"]
    productionLocation=request["production_location"]
    indexer.insertProduction(productionName, productionLocation);
    wfile.write("[]\r\n".encode());
    
#def handleGetFileDetails(wfile, request, session):
#    fileId=int(request["file_id"])
#    file = indexer.getFileDetails(fileId)
#    if file != None:
#        wfile.write("[{");
#        wfile.write("\"file_id\":"+str(file[0])+",");
#        wfile.write("\"file_name\":\""+file[1]+"\",");
#        wfile.write("\"file_location\":\""+file[2]+"\",");
#        wfile.write("\"scene_name\":\""+file[3]+"\",");
#        wfile.write("\"scene_resolution\":\""+str(file[4])+"x"+str(file[5])+"\",");
#        wfile.write("\"scene_outputtype\":\""+file[6]+"\",");
#        wfile.write("\"scene_xparts\":"+str(file[7])+",");
#        wfile.write("\"scene_yparts\":"+str(file[8])+",");
#        wfile.write("\"scene_startframe\":"+str(file[9])+",");
#        wfile.write("\"scene_endframe\":"+str(file[10]));
#        wfile.write("}]\r\n");
#    else:
#        file = indexer.getFile(fileId)
#        wfile.write("[{");
#        wfile.write("\"file_id\":"+str(file[0])+",");
#        wfile.write("\"file_name\":\""+file[2]+"\",");
#        wfile.write("\"file_location\":\""+file[3]+"\"");
#        wfile.write("}]\r\n");

#def handleGetFiles(wfile, request, session):
#    productionId=int(request["production_id"])
#    indexer.updateIndex(productionId)
#    items = indexer.getProductionFiles(productionId)
#    wfile.write("[");
#    first = True;
#    for item in items:
#        if first:
#            first=False
#        else:
#            wfile.write(",");
#        
#        wfile.write("{");
#        wfile.write("\"file_id\":"+str(item[0])+",");
#        wfile.write("\"file_name\":\""+item[2]+"\",");
#        wfile.write("\"file_location\":\""+item[3]+"\"");
#        wfile.write("}\r\n");
#
#    wfile.write("]");
    
#def handleGetElements(wfile, request, session):
#    fileId=int(request["file_id"])
#    elements = indexer.getFileElements(fileId)
#    references = indexer.getFileReferences(fileId)
#    usedby = indexer.getFileUsedBy(fileId)
#    wfile.write("[[")
#    first = True;
#    for item in elements:
#        if first:
#            first=False
#        else:
#            wfile.write(",");
#        wfile.write("{")
#        wfile.write("\"element_id\":"+str(item[0])+",")
#        wfile.write("\"element_name\":\""+item[5]+"\",")
#        wfile.write("\"element_type\":\""+item[6]+"\"")
#        wfile.write("}")
#   
#    wfile.write("],[")
#    first = True;
#    for item in references:
#        if first:
#            first=False
#        else:
#            wfile.write(",");
#        wfile.write("{")
#        if item[3] != None:
#            wfile.write("\"file_id\":"+str(item[3])+",")
#        else:
#            wfile.write("\"file_id\":null,")
#            
#        wfile.write("\"file_location\":\""+item[0]+"\",")
#        wfile.write("\"element_name\":\""+item[2]+"\",")
#        wfile.write("\"element_type\":\""+item[1]+"\"")
#        wfile.write("}")
#        
#    wfile.write("],[")
#    first = True;
#    for item in usedby:
#        if first:
#            first=False
#        else:
#            wfile.write(",");
#        wfile.write("{")
#        wfile.write("\"file_id\":"+str(item[3])+",")
#        wfile.write("\"file_location\":\""+item[0]+"\",")
#        wfile.write("\"element_name\":\""+item[2]+"\",")
#        wfile.write("\"element_type\":\""+item[1]+"\"")
#        wfile.write("}")    
#    wfile.write("]]")
