import blendfile
import shutil
import os
import sys

materialpreview = "materialtemplate.blend"
materiallibrary = "materiallink.blend"
materialidname = "MATestMaterial"
grouppreview = "grouptemplate.blend"
grouplibrary = "materiallink.blend"
groupidname = "GRTestGroup"

tempfile = "temp.blend"
blenderlocation="d:\\blender\\blender.exe"

def trim(a):
    return a.split("\0")[0]

def generateMaterialThumbnails(filename):
    """ Generate all material thumbnails of a specific blend file
    """
    materialnames=[]
    bfile = blendfile.openBlendFile(filename)
    basename=os.path.basename(filename)
    relpath = os.path.relpath(filename)

    for block in bfile.FindBlendFileBlocksWithCode("MA\0\0"):
        materialname = trim(block.Get("id.name"))
        materialnames.append(materialname)
        
    bfile.close()
    for materialname in materialnames:
        print("""
--- Material: """+materialname+" ---")
        output = "-".join([basename,materialname, ""])
        shutil.copy(materialpreview, tempfile)
        
        bfile = blendfile.openBlendFile(tempfile, "r+b")
        address=0
        for block in bfile.FindBlendFileBlocksWithCode("LI"):
            liname = trim(block.Get("name"))
            if liname.endswith(materiallibrary):
                address = block.Header.OldAddress
                block.Set("name", "//"+relpath)

        for block in bfile.FindBlendFileBlocksWithCode("ID"):
            idname = trim(block.Get("name"))
            idlib = block.Get("lib")
            
            if idlib == address and idname == materialidname:
                block.Set("name", materialname)
            
        for block in bfile.FindBlendFileBlocksWithCode("SC"):
            
            block.Set("r.pic", "//"+output)

        bfile.close()
        
        os.system(blenderlocation+" -b "+tempfile+" -f 1")

        os.remove(tempfile)
        
def generateGroupThumbnails(filename):
    """ Generate all group thumbnails of a specific blend file
    """
    groupnames=[]
    bfile = blendfile.openBlendFile(filename)
    basename=os.path.basename(filename)
    relpath = os.path.relpath(filename)

    for block in bfile.FindBlendFileBlocksWithCode("GR\0\0"):
        groupname = trim(block.Get("id.name"))
        groupnames.append(groupname)
        
    bfile.close()
    for groupname in groupnames:
        print("""
--- Group: """+groupname+" ---")
        output = "-".join([basename,groupname, ""])
        shutil.copy(grouppreview, tempfile)
        
        bfile = blendfile.openBlendFile(tempfile, "r+b")
        address=0
        for block in bfile.FindBlendFileBlocksWithCode("LI"):
            liname = trim(block.Get("name"))
            if liname.endswith(grouplibrary):
                address = block.Header.OldAddress
                block.Set("name", "//"+relpath)

        for block in bfile.FindBlendFileBlocksWithCode("ID"):
            idname = trim(block.Get("name"))
            idlib = block.Get("lib")
            
            if idlib == address and idname == groupidname:
                block.Set("name", groupname)
            
        for block in bfile.FindBlendFileBlocksWithCode("SC"):
            block.Set("r.pic", "//"+output)

        bfile.close()
        
        os.system(blenderlocation+" -b "+tempfile+" -a")

        os.remove(tempfile)

if len(sys.argv) != 2:
    print("""Material+group preview renderer
(c) At Mind B.V. distributed under GPLv3 license
usage: python makepreviews.py <blendfile/dirname>

This util will generate material previews based on a template.""")
    
    exit();
filename = sys.argv[1]
filename = os.path.abspath(filename)

if os.path.isdir(filename):
    for dirpath, dirnames, filenames in os.walk(filename):
        for fns in filenames:
            if fns.endswith(".blend"):
                fn = os.path.join(dirpath, fns)
                generateMaterialThumbnails(fn)
                generateGroupThumbnails(fn)
            
else:
    generateMaterialThumbnails(filename)
    generateGroupThumbnails(filename)

