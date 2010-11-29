# the blender-aid API

class BlenderAidException:
    """
        Base Exception class to be used for exception management.
    """
    pass

    
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
        pass
        
    def getProductions(self, name=None, workfolder=None):
        """
            receive productions configured on the server mathing the given name and
            workfolder. when None these will be ignored.
            
            result is an array with Production classes, or an Exception
        """
        pass

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
        pass

class Production:
    """
        object representing a production
    """
    def __init__(self, server):
        self.server=server
        self.id=None
        self.name=None
        self.location=None
        self.svnUrl=None
        self.svnUserid=None
        self.svnPassword=None

    def getMissingLinks(self):
        """
            returns a list of missing links in the production.
        """
        pass
        
    def getFiles(self):
        pass

    def getDirectories(self):
        pass

    def refresh(self):
        pass

class File:
    """
        object representing a file
    """
    def __init__(self, server, production):
        pass
        
    def getElements(self):
        pass
        
    def getReferences(self, referencesFrom=False):
        pass

    def rename(self, execute=True):
        pass

    def move(self, execute=True):
        pass
    
    def getDirectory(self):
        pass

class Directory:
    """
        object representing a directory
    """
    def __init__(self, server, production):
        pass

    def rename(self, execute=True):
        pass

    def move(self, execute=True):
        pass
        
    def getFiles(self):
        pass

class Element:
    """
        object representing an element
    """
    def __init__(self, server, production, file):
        pass

    def rename(self, execute=True):
        pass
        
    def getReferencesTo(self):
        pass
    
class Reference:
    """
        object representing a reference (link between files)
    """
    pass 
