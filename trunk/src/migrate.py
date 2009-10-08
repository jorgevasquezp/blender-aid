#!/usr/bin/python
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
import json
import sys
import servicerefactor
import serviceproduction
import os
import indexer

def migrate(args = sys.argv):
    indexer.setup()
    if "help" in args:
        printHelp(args)
    elif "rename-file" in args:
        renameFile(args)
    elif "move-file" in args:
        moveFile(args)
    elif "rename-element" in args:
        renameElement(args)
    elif "add-production" in args:
        addProduction(args)
    elif "remove-production" in args:
        removeProduction(args)
    else:
        printHelp(args)

def removeProduction(args):
    session = {}
    request = {}
    if len(args)==3:
        request["production_id"] = determineProductionByName(args[2])
    else:    
        request["production_id"] = selectProduction()
    result = out()
    serviceproduction.handleDelete(result, request, session)
    print("production removed")
        
def addProduction(args):
    session = {}
    request = {}
    if len(args)==4:
        request["production_name"] = args[2]
        request["production_location"] = args[3]
    else:    
        request["production_name"] = raw_input("Enter production name:")
        request["production_location"] = raw_input("Enter production location:")
    result = out()
    serviceproduction.handleAdd(result, request, session)
    print("production added")
    
def renameElement(args):
    session = {}
    request = {}
    if len(args)==5:
        session["production_id"] = determineProduction(args[2])
        session["file_id"] = determineFile(session["production_id"], args[2])
        request["element_id"] = determineElement(session["production_id"], session["file_id"], args[3])
        request["new_name"] = args[4]
    else:    
        session["production_id"] = selectProduction()
        session["file_id"] = selectBlendFile(session["production_id"])
        request["element_id"] = selectElement(session["production_id"], session["file_id"])
        request["new_name"] = selectNewElementName(session["production_id"], session["file_id"], request["element_id"])
    result = out()
    servicerefactor.handleStartRenameElement(result, request, session)
    performMigrate(result, request, session)

def renameFile(args):
    session = {}
    request = {}
    if len(args)==4:
        session["production_id"] = determineProduction(args[2])
        session["file_id"] = determineFile(session["production_id"], args[2])
        request["new_filename"] = args[3]
    else:
        session["production_id"] = selectProduction()
        session["file_id"] = selectFile(session["production_id"])
        request["new_filename"] = selectNewFileName(session["production_id"], session["file_id"])

    result = out()
    servicerefactor.handleStartRenameFile(result, request, session)
    performMigrate(result, request, session)

def moveFile(args):
    session = {}
    request = {}
    
    if len(args)==4:
        session["production_id"] = determineProduction(args[2])
        session["file_id"] = determineFile(session["production_id"], args[2])
        request["new_location"] = args[3]
    else:
        session["production_id"] = selectProduction()
        session["file_id"] = selectFile(session["production_id"])
        request["new_location"] = selectNewLocation(session["production_id"], session["file_id"])
        
    result = out()
    servicerefactor.handleStartMoveFile(result, request, session)
    performMigrate(result, request, session)
    
def performMigrate(result, request, session):
    
    tasks= json.loads(result.out)
    print("")
    print("The next tasks will be performed:")
    for task in tasks:
        if (task["task_important"]):
            print(" * "+ task["file_location"]+": "+task["task_description"])
    print("")
    key = ""
    while key<>"c" and key<>"q":
        key = raw_input("Press c to continue, and q to quit: ")

    if key=="q":
        return
    
    result.reset()
    servicerefactor.handleExecuteCurrentTasks(result, request, session)
    print("")
    print("Test the result. When OK commit the changes, otherwise do a rollback.")
    key = ""
    while key<>"c" and key<>"r":
        key = raw_input("Press c to commit, and r to rollback: ")

    if key=="r":
        servicerefactor.handleRollbackCurrentTasks(result, request, session)
    if key=="c":
        servicerefactor.handleCommitCurrentTasks(result, request, session)
    print("Finished!")
    
class out():
    def __init__(self):
        self.out = ""
    def write(self, s):
        self.out = self.out + s.replace("\\", "/")
    def reset(self):
        self.out = ""
        
def selectProduction():
    result = out()
    serviceproduction.handleGetAll(result, {}, {})
    productions = json.loads(result.out)
    choices=[]
    for production in productions:
        choices.append(int(production["production_id"]))
        print("("+str(len(choices))+") "+ production["production_name"])
    choice = -1
    while choice == -1:
        key = raw_input("Choose a production: ")
        choice = int(key)
        if choice <1 or choice > len(choices):
            choice=-1
        
    return choices[choice-1]

def selectNewFileName(productionId, fileId):
    result = out()
    session = {}
    session["production_id"] = productionId
    session["file_id"] = fileId
    serviceproduction.handleGetFileDetails(result, session, session)
    afile = json.loads(result.out)[0]    
    newname = raw_input("enter new filename for ["+afile["file_name"]+"]: ")
    return newname

def selectNewLocation(productionId, fileId):
    result = out()
    session = {}
    session["production_id"] = productionId
    session["file_id"] = fileId
    serviceproduction.handleGetFileDetails(result, session, session)
    afile = json.loads(result.out)[0]    
    newname = raw_input("enter new location for ["+afile["file_location"]+"]: ")
    return newname

def selectNewElementName(productionId, fileId, elementId):
    newname = raw_input("enter new name: ")
    return newname
    
def selectFile(productionId):
    result = out()
    session = {}
    session["production_id"] = productionId
    serviceproduction.handleGetFiles(result, session, session)
    files = json.loads(result.out)
    choices=[]
    for afile in files:
        choices.append(int(afile["file_id"]))
        print("("+str(len(choices))+") "+ afile["file_location"])
    choice = -1
    while choice == -1:
        key = raw_input("Choose a file: ")
        choice = int(key)
        if choice <1 or choice>len(choices):
            choice=-1
        
    return choices[choice-1]

def selectBlendFile(productionId):
    result = out()
    session = {}
    session["production_id"] = productionId
    serviceproduction.handleGetFiles(result, session, session)
    files = json.loads(result.out)
    choices=[]
    for afile in files:
        if afile["file_name"].endswith(".blend"):
            print("("+str(afile["file_id"])+") "+ afile["file_location"])
            choices.append(int(afile["file_id"]))
    choice = -1
    while choice == -1:
        key = raw_input("Choose a file: ")
        choice = int(key)
        if choice not in choices:
            choice=-1
        
    return choice

def selectElement(productionId, fileId):
    result = out()
    session = {}
    session["production_id"] = productionId
    session["file_id"] = fileId
    serviceproduction.handleGetElements(result, session, session)
    elements = json.loads(result.out)[0]
    choices=[]
    for element in elements:
        choices.append(int(element["element_id"]))
        print("("+str(len(choices))+") "+ element["element_name"])
    choice = -1
    while choice == -1:
        key = raw_input("Choose an element: ")
        choice = int(key)
        if choice <1 or choice>len(choices):
            choice=-1
        
    return choices[choice-1]

def determineProduction(filelocation):
    rpath = os.path.abspath(filelocation)
    result=out()
    serviceproduction.handleGetAll(result, {}, {})
    productions = json.loads(result.out)
    for production in productions:
        rppath = os.path.abspath(production["production_location"])
        if rpath.startswith(rppath):
            print ("Using production: ["+production["production_name"]+"]")
            return production["production_id"]
    return -1

def determineProductionByName(name):
    result = out()
    serviceproduction.handleGetAll(result, {}, {})
    productions = json.loads(result.out)
    for production in productions:
        if production["production_name"] == name:
            print ("Using production: ["+production["production_name"]+"]")
            return production["production_id"]
    return -1

def determineFile(productionId, filelocation):
    rpath = os.path.abspath(filelocation)
    result=out()
    serviceproduction.handleGet(result, {"production_id": productionId}, {})
    production = json.loads(result.out)[0]
    result.reset()
    serviceproduction.handleGetFiles(result, {"production_id": productionId}, {})
    files = json.loads(result.out)
    
    for afile in files:
        rppath = os.path.abspath(os.path.join(production["production_location"], afile["file_location"]))
                                 
        if rpath.startswith(rppath):
            print ("Using file: ["+afile["file_location"]+"]")
            return afile["file_id"]
    return -1

def determineElement(productionId, fileId, elementName):
    result = out()
    session = {}
    session["production_id"] = productionId
    session["file_id"] = fileId
    serviceproduction.handleGetElements(result, session, session)
    elements = json.loads(result.out)[0]
    for element in elements:
        if (elementName == element["element_name"]):
            return element["element_id"]
    return -1
    
def printHelp(args):
    print("""Blender production migration tool
version 0.1 (demo) - please beware backup your files

usage:
    python migrate.py [help [action]] - displays this text when action is entered
                    additional help text is displayed concerning the action
    python migrate.py add-production - add a new production to the tool. a production has to be added
                    before any migration or refactoring can be executed. The production will also be visible
                    in the web-site when ran locally
    python migrate.py rename-file - start rename file migration
    python migrate.py rename-element - start rename a blender element (Object, Group, Mesh, Material etc)
    python migrate.py move-file - start moving a file
    
    python migrate.py remove-production - not implemented yet
    python migrate.py solve-missing - not implemented yet
    python migrate.py move-element - not implemented yet
    python migrate.py render-settings - not implemented yet

for more information please contact blender@atmind.nl
""")
    if "rename-file" in args:
        print(""" --- rename-file ---
    python migrate.py rename-file [source-file target-filename]

Parameters:
    source-file:        path to the file what needs to be renamed.
    target-filename:    the name the file needs to be renamed to.
when parameters are not given an interactive shell will start.

Note:
    this method does not support moving the file to another directory.

Example:
    python migrate.py rename-file
    python migrate.py rename-file /var/productions/yf/chars/frankie.blend frankie_momo.blend
""");
    if "rename-element" in args:
        print(""" --- rename-element ---
    python migrate.py rename-element [source-file source-elementname target-elementname]

Parameters:
    source-file:        path to the file what needs to be renamed.
    source-elementname: the name the element needs to be renamed.
    target-elementname: the name the element needs to be renamed to.
when parameters are not given an interactive shell will start.

Note:
    this method does not support renaming the type of object.

Example:
    python migrate.py rename-element
    python migrate.py rename-element /var/productions/yf/chars/frankie.blend GRFlyingSquirrel GRFrankie
""");
    if "add-production" in args:
        print(""" --- add production ---
    python migrate.py add-production [production-name production-location]

Parameters:
    production-name:     name of the production
    production-location: the location of the production
when parameters are not given an interactive shell will start.

Note:

Example:
    python migrate.py add-production
    python migrate.py add-production "Yo Frankie!" /var/productions/yf
""");
    if "remove-production" in args:
        print(""" --- remove production ---
    python migrate.py remove-production [production-name]

Parameters:
    production-name:     name of the production to be removed
when parameters are not given an interactive shell will start.

Note:
    the production files will not be removed or deleted. this task will only remove the reference from the tool
    
Example:
    python migrate.py remove-production
    python migrate.py remove-production "Yo Frankie!"
""");

if __name__ == "__main__":
    migrate()


