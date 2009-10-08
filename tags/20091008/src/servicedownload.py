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
try:
    from PIL import Image
except:
    print("No Python Imaging Library found! disabling thumbnails")
    Image=None

import indexer

def handleGet(wfile, request, session):
    fileId=int(request["file_id"])
    productionId=int(request["production_id"])
    rPath=getAbsoluteFilename(productionId, fileId)

    sfile = file(rPath, "rb")
    content = sfile.read()
    wfile.write(content)
    sfile.close()
    
def handleGetThumbnail(wfile, request, session, size):
    fileId=int(request["file_id"])
    productionId=int(request["production_id"])
    rPath=getAbsoluteFilename(productionId, fileId)
    if rPath.endswith("jpg") or rPath.endswith("jpeg") or rPath.endswith("png") or rPath.endswith("gif"):
        if Image == None:
            pass
        else:
            im = Image.open(rPath)
            im.thumbnail([size,size], Image.ANTIALIAS)
            im.save(wfile, "PNG")

def getAbsoluteFilename(productionId, fileId):
    production = indexer.getProduction(productionId)
    pfile = indexer.getFile(fileId)
    return os.path.join(production[2], pfile[3])
    
    
