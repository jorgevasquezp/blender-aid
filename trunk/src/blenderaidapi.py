"""
    the Blender-aid API.
    
    example:
        server = blenderaidapi.Server(("localhost", 8080))
        productions = server.getProductions()
        for production in productions:
            print(production.name)
            files = production.getFiles()
            for file in files:
                print(file.location)
                
    example2:
        server = blenderaidapi.Server(("localhost", 8080))
        production = server.getProductions()[0]
        production.getFiles(location="chars/frankie.blend")[0].rename("momo.blend")
    
"""
# the blender-aid API
# httplib if < python 3.0
# anders http.client

import httplib
import json

class BlenderAidException:
    """
        Base Exception class to be used for exception management.
    """
    pass

def request(server, servicename, requestParams):
    """
        send a request to the servicename with the requestParams and result
        the response.
        
        this method does:
            1. translate the requestParams to a JSON string
            2. send the JSON string to the server/servicename
            3. receive the JSON response string
            4. translate the JSON response to the result
    """
    # 1
    request = json.dumps(requestParams)+"\r\n"
    # 2
    connection = httplib.HTTPConnection(server[0], server[1])
    connection.request("POST", "/service/" + servicename, request)
    # 3
    response = connection.getresponse()
    responseBytes = response.read()
    connection.close()
    # 4:
    result = json.loads(responseBytes)
    return result

class Server:
    """
        Server is the entry class to access Blender-aid functionality from
        other python sources.
        
        It can be used to automate and integrate Blender-aid into your
        production pipeline.
    """
    def __init__(self, binding):
        """
            usage:
            server = blenderaidapi.Server(("127.0.0.1", 8080))
        """
        self.binding = binding
        
    def getProductions(self, name=None, workfolder=None):
        """
            receive productions configured on the server mathing the given name and
            workfolder. when None these will be ignored.
            
            result is an array with Production classes, or an Exception
        """
        response = request(self.binding, "productions", [])
        result = []
        for jsonProduction in response:
            result.append(Production(self, jsonProduction))
        return result
    def addProduction(self, production):
        """
            register a production to blender-aid
        """
        pass
        
    def removeProduction(self, production):
        """
            unregister a production from blender-aid
        """
        pass

class RefactoringAction:
    pass

class RefactoringProcess:
    def execute(self):
        pass

class MissingLink:
    """
        object representing a missing link
    """
    pass

class PossibleLink:
    """
        object representing a possible link to solve of a missing link
    """
    def fix(self, execute=True):
        """
            fix the missing link by applying this link.
            
            execute -- boolean indicating if the refactoring process will be
                    executed immediatly by this call
        """
        pass

class Production:
    """
        object representing a production
        
        id -- id of the production (key)
        name -- name of the production
        location -- absolute path to the root of the production on the filesystem
        svnUrl -- SVN url of the production
        svnUserid -- SVN userid
        svnPassword -- SVN password
    """
    def __init__(self, server, jsonProduction):
        self.server=server
        self.id=jsonProduction["production_id"]
        self.name=jsonProduction["production_name"]
        self.location=jsonProduction["production_location"]
        self.svnUrl=jsonProduction["production_svnurl"]
        self.svnUserid=jsonProduction["production_svnuserid"]
        self.svnPassword=jsonProduction["production_svnpassword"]

    def getMissingLinks(self):
        """
            returns a list of missing links in the production.
        """
        pass
        
    def getFiles(self, name=None, location=None):
        """
            get a list of the files in the production. The list is filtered 
            with the given name and location.
            
            name -- part of the filename to be include in the list
            location -- part of the location of the file to be included in the 
                    list
        """
        pass

    def getDirectories(self):
        """
            get a list of directories in the production. Empty directories are 
            always excluded in the result
        """
        pass

class File:
    """
        object representing a file
        
        fields:
            id -- id of the file (key)
            location -- relative location from the production location of this
                file including the filename
            name -- filename of the file
            
            production -- Production where this file is part of
            server -- Server object what is used to retrieve this
                    object from the server.
    """
    def __init__(self, server, production):
        self.server = server
        self.production = production
        self.id=None
        self.location=None
        self.name=None
        
    def getElements(self, name=None, type=None):
        """
            get a list of elements of this file.
            
            fields:
                name -- name filter to use
                type -- type filter to use
        """
        pass
        
    def getReferences(self, referencesFrom=False):
        pass

    def rename(self, newFilename, execute=True):
        pass

    def move(self, directory, execute=True):
        pass
    
    def getDirectory(self):
        """
            get the directory where this file is located.
        """
        pass

class Directory:
    """
        object representing a directory
        
        fields:
            production -- production where this directory is part of
            location -- the full directory name (including parent directory)
                    from the roor location of the production
            server -- the Server object what is used to retrieve this object
    """
    def __init__(self, server, production):
        pass

    def rename(self, newName, execute=True):
        pass

    def move(self, newLocation, execute=True):
        pass
        
    def getFiles(self):
        """
            retrieve all files inside this directory (including subdirectories)
        """
        pass

class Element:
    """
        object representing an element
    """
    def __init__(self, server, production, file):
        self.server = server
        self.production = production
        self.file = file
        self.id = None
        self.name = None
        self.type = None

    def rename(self, newName, execute=True):
        """
            rename this element to newName
        """
        pass
        
    def getReferencesTo(self):
        """
            return a list with all references to this specific element.
        """
        pass
    
class Reference:
    """
        object representing a reference (link between files)
    """
    pass 
