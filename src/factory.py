import indexer

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
    result["file_timestamp"]=file[4]*1000
    result["file_size"]=file[5]
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
    step = scene[8]
    if step==None:
        step=1
    elif step==0:
        step=1
        
    result["scene_step"] = step
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
    result["element_id"]=err[3]
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

def solutionToObject(solution, match=None) :
    obj={}
    obj["file_id"] = solution[0]
    obj["production_id"] = solution[1]
    obj["file_name"] = solution[2]
    obj["file_location"] = solution[3]
    obj["file_timestamp"]=solution[4]*1000
    obj["file_size"] = solution[5]
    if match == None:
        obj["match"] = solution[6]
    else:
        obj["match"] = match
    return obj
def solutionIDToObject(solution) :
    obj={}
    obj["file_id"] = solution[indexer.INDEX_ELEMENT_ID]
    obj["file_name"] = solution[indexer.INDEX_ELEMENT_NAME]
    obj["file_location"] = solution[indexer.INDEX_ELEMENT_NAME]
    obj["match"] = 1.0
    return obj