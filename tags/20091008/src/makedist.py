import py_compile
import os

sourcefiles=[
"blendfile.py", "migrate.py", "servicedependancy.py", "servicerefactor.py", 
"indexer.py", "server.py", "servicedownload.py", "servicescenes.py",
"serviceconsistency.py", "serviceproduction.py", "settings.py"
]

def makeDistribution():
    cleanUp()
    compileCode()
    copyResources()
    package()
    
def cleanUp():
    pass
def copyResources():
    pass
def package():
    pass

def compileCode():
    for sourcefile in sourcefiles:
        py_compile.compile(sourcefile)

if __name__ =="__main__":
    makeDistribution()