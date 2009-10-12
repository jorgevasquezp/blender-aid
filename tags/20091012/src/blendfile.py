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

# 06-10-2009: 
#  jbakker - adding support for python 3.0

######################################################
# Importing modules
######################################################
import os
import struct
import logging
import gzip
import tempfile

log = logging.getLogger("blendfile")

######################################################
# module global routines
######################################################
# read routines
# open a filename
# determine if the file is compressed
# and returns a handle
def openBlendFile(filename, access="rb"):
    """Opens a blend file for reading or writing pending on the access
    supports 2 kind of blend files. Uncompressed and compressed.
    Known issue: does not support packaged blend files
    """
    handle = open(filename, access)
    magic = ReadString(handle, 7)
    if magic == "BLENDER":
        log.debug("normal blendfile detected")
        handle.seek(0, os.SEEK_SET)
        res = BlendFile(handle)
        res.compressed=False
        res.originalfilename=filename
        return res
    else:
        log.debug("gzip blendfile detected?")
        handle.close()
        log.debug("decompressing started")
        fs = gzip.open(filename, "rb")
        handle = tempfile.TemporaryFile()
        data = fs.read(1024*1024) 
        while data: 
            handle.write(data) 
            data = fs.read(1024*1024) 
        log.debug("decompressing finished")
        fs.close()
        log.debug("resetting decompressed file")
        handle.seek(os.SEEK_SET, 0)
        res = BlendFile(handle)
        res.compressed=True
        res.originalfilename=filename
        return res

def closeBlendFile(afile):
    """close the blend file
    writes the blend file to disk if changes has happened"""
    handle = afile.handle
    if afile.compressed:
        log.debug("close compressed blend file")
        handle.seek(os.SEEK_SET, 0)
        log.debug("compressing started")
        fs = gzip.open(afile.originalfilename, "wb")
        data = handle.read(1024*1024) 
        while data: 
            fs.write(data) 
            data = handle.read(1024*1024) 
        fs.close()
        log.debug("compressing finished")
        
    handle.close()
    
######################################################
#    Write a string to the file.
######################################################
def WriteString(handle, astring, fieldlen):
    stringw=""
    if len(astring) >= fieldlen:
        stringw=astring[0:fieldlen]
    else:
        stringw=astring+'\0'
    handle.write(stringw.encode())

######################################################
#    ReadString reads a String of given length from a file handle
######################################################
def ReadString(handle, length):
    return handle.read(length).decode("iso-8859-1", "ignore")

######################################################
#    ReadString0 reads a zero terminating String from a file handle
######################################################
def ReadString0(handle):
    Result = ""
    S = ReadString(handle, 1)
    while S!="\0":
        Result=Result+S
        S=ReadString(handle, 1)
    return Result

######################################################
#    ReadUShort reads an unsigned short from a file handle
######################################################
def ReadUShort(handle, fileheader):
    return struct.unpack(fileheader.StructPre+"H", handle.read(2))[0]

######################################################
#    ReadUInt reads an unsigned integer from a file handle
######################################################
def ReadUInt(handle, fileheader):
    return struct.unpack(fileheader.StructPre+"I", handle.read(4))[0]

def ReadInt(handle, fileheader):
    return struct.unpack(fileheader.StructPre+"i", handle.read(4))[0]
def ReadFloat(handle, fileheader):
    return struct.unpack(fileheader.StructPre+"f", handle.read(4))[0]
def ReadShort(handle, fileheader):
    return struct.unpack(fileheader.StructPre+"h", handle.read(2))[0]

######################################################
#    ReadULong reads an unsigned long from a file handle
######################################################
def ReadULong(handle, fileheader):
    return struct.unpack(fileheader.StructPre+"Q", handle.read(8))[0]

######################################################
#    ReadPointer reads an pointerfrom a file handle
#    the pointersize is given by the header (BlendFileHeader)
######################################################
def ReadPointer(handle, header):
    if header.PointerSize == 4:
        return ReadUInt(handle, header)
    if header.PointerSize == 8:
        return ReadULong(handle, header)
    
######################################################
#    Allign alligns the filehandle on 4 bytes
######################################################
def Allign(handle):
    offset = handle.tell()
    trim = offset % 4
    if trim != 0:
        handle.read(4-trim)

######################################################
# module classes
######################################################

######################################################
#    BlendFile
#   - Header (BlendFileHeader)
#   - Blocks (FileBlockHeader)
#   - Catalog (DNACatalog)
######################################################
class BlendFile:
    
    def __init__(self, handle):
        log.debug("initializing reading blend-file")
        self.handle=handle
        self.Header = BlendFileHeader(handle)
        self.Blocks = []
        aBlock = BlendFileBlock(handle, self)
        while aBlock.Header.Code != "ENDB":
            if aBlock.Header.Code == "DNA1":
                self.Catalog = DNACatalog(self.Header, handle)
            else:
#                if aBlock.Header.Code <> "DATA":
#                    log.debug(aBlock.Header.Code)
                aBlock.Header.skip(handle)
                
            self.Blocks.append(aBlock)
            aBlock = BlendFileBlock(handle, self)
        self.Modified=False
        self.Blocks.append(aBlock)
        
    def FindBlendFileBlocksWithCode(self, code):
        result = []
        for block in self.Blocks:
            if block.Header.Code.startswith(code) or block.Header.Code.endswith(code):
                result.append(block)
        return result
    
    def FindBlendFileBlockWithOffset(self, offset):
        for block in self.Blocks:
            if block.Header.OldAddress == offset:
                return block;
        return None;
    
    def close(self):
        if not self.Modified:
            self.handle.close()
        else:
            closeBlendFile(self)
        
######################################################
#    BlendFileBlock
#   File=BlendFile
#   Header=FileBlockHeader
######################################################
class BlendFileBlock:
    def __init__(self, handle, afile):
        self.File = afile
        self.Header = FileBlockHeader(handle, afile.Header)
        
    def Get(self, path):
        dnaIndex = self.Header.SDNAIndex
        dnaStruct = self.File.Catalog.Structs[dnaIndex]
        self.File.handle.seek(self.Header.FileOffset, os.SEEK_SET)
        return dnaStruct.GetField(self.File.Header, self.File.handle, path)

    def Set(self, path, value):
        dnaIndex = self.Header.SDNAIndex
        dnaStruct = self.File.Catalog.Structs[dnaIndex]
        self.File.handle.seek(self.Header.FileOffset, os.SEEK_SET)
        self.File.Modified=True
        return dnaStruct.SetField(self.File.Header, self.File.handle, path, value)

######################################################
#    BlendFileHeader allocates the first 12 bytes of a blend file
#    it contains information about the hardware architecture
#    Magic = str
#    PointerSize = int
#    LittleEndianness = bool
#    Version = int
######################################################
class BlendFileHeader:
    def __init__(self, handle):
        log.debug("reading blend-file-header")
        self.Magic = ReadString(handle, 7)
        log.debug(self.Magic)
        tPointerSize = ReadString(handle, 1)
        log.debug(tPointerSize)
        if tPointerSize=="-":
            self.PointerSize=8
        if tPointerSize=="_":
            self.PointerSize=4
        tEndianness = ReadString(handle, 1)
        log.debug(tEndianness)
        if tEndianness=="v":
            self.LittleEndianness=True
            self.StructPre="<"
        if tEndianness=="V":
            self.LittleEndianness=False
            self.StructPre=">"

        tVersion = ReadString(handle, 3)
        log.debug(tVersion)
        self.Version = int(tVersion)
        log.debug(self.Magic+" "+str(self.Version)+" "+str(self.PointerSize)+" "+str(self.LittleEndianness))


######################################################
#    FileBlockHeader contains the information in a file-block-header
#    the class is needed for searching to the correct file-block (containing Code: DNA1)
#
#    Code=str
#    Size=int
#    OldAddress=pointer
#    SDNAIndex=int
#    Count=int
#    FileOffset=file pointer of datablock
######################################################
class FileBlockHeader:

    def __init__(self, handle, header):
        self.Code = ReadString(handle, 4).strip()
        if self.Code!="ENDB":
            self.Size = ReadUInt(handle, header)
            self.OldAddress = ReadPointer(handle, header)
            self.SDNAIndex = ReadUInt(handle, header)
            self.Count = ReadUInt(handle, header)
            self.FileOffset = handle.tell()
        else:
            self.Size = ReadUInt(handle, header)
            self.OldAddress = 0
            self.SDNAIndex = 0
            self.Count = 0
            self.FileOffset = handle.tell()

    def skip(self, handle):
        handle.read(self.Size)
        
######################################################
#    DNACatalog is a catalog of all information in the DNA1 file-block
#
#    Header=None
#    Names=None
#    Types=None
#    Structs=None
######################################################
class DNACatalog:

    def __init__(self, header, handle):
        log.debug("building DNA catalog")
        self.Names=[]
        self.Types=[]
        self.Structs=[]
        self.Header = header
        SDNA = ReadString(handle, 4)
        NAME = ReadString(handle, 4)
        numberOfNames = ReadUInt(handle, header)
        log.debug("building #"+str(numberOfNames)+" names")
        for i in range(numberOfNames):
            tName = ReadString0(handle)
            self.Names.append(DNAName(tName))

        Allign(handle)
        TYPE = ReadString(handle, 4)
        numberOfTypes = ReadUInt(handle, header)
        log.debug("building #"+str(numberOfTypes)+" types")
        for i in range(numberOfTypes):
            tType = ReadString0(handle)
            self.Types.append(DNAType(tType))

        Allign(handle)
        TLEN = ReadString(handle, 4)
        log.debug("building #"+str(numberOfTypes)+" type-lengths")
        for i in range(numberOfTypes):
            tLen = ReadUShort(handle, header)
            self.Types[i].Size = tLen

        Allign(handle)
        STRC = ReadString(handle, 4)
        numberOfStructures = ReadUInt(handle, header)
        log.debug("building #"+str(numberOfStructures)+" structures")
        for structureIndex in range(numberOfStructures):
            tType = ReadUShort(handle, header)
            Type = self.Types[tType]
            structure = DNAStructure(Type)
            self.Structs.append(structure)

            numberOfFields = ReadUShort(handle, header)
            for fieldIndex in range(numberOfFields):
                fTypeIndex = ReadUShort(handle, header)
                fNameIndex = ReadUShort(handle, header)
                fType = self.Types[fTypeIndex]
                fName = self.Names[fNameIndex]
                structure.Fields.append(DNAField(fType, fName))
            
                


######################################################
#    DNAName is a C-type name stored in the DNA
#   Name=str
######################################################
class DNAName:

    def __init__(self, aName):
        self.Name = aName
        
    def AsReference(self, parent):
        if parent == None:
            Result = ""
        else:
            Result = parent+"."
            
        Result = Result + self.ShortName()
        return Result

    def ShortName(self):
        Result = self.Name;
        Result = Result.replace("*", "")
        Result = Result.replace("(", "")
        Result = Result.replace(")", "")
        Index = Result.find("[")
        if Index != -1:
            Result = Result[0:Index]
        return Result
        
    def IsPointer(self):
        return self.Name.find("*")>-1

    def IsMethodPointer(self):
        return self.Name.find("(*")>-1

    def ArraySize(self):
        Result = 1
        Temp = self.Name
        Index = Temp.find("[")

        while Index != -1:
            Index2 = Temp.find("]")
            Result*=int(Temp[Index+1:Index2])
            Temp = Temp[Index2+1:]
            Index = Temp.find("[")
        
        return Result

######################################################
#    DNAType is a C-type stored in the DNA
#
#    Name=str
#    Size=int
#    Structure=DNAStructure
######################################################
class DNAType:
    def __init__(self, aName):
        self.Name = aName
        self.Structure=None

######################################################
#    DNAType is a C-type structure stored in the DNA
#
#    Type=DNAType
#    Fields=[DNAField]
######################################################
class DNAStructure:

    def __init__(self, aType):
        self.Type = aType
        self.Type.Structure = self
        self.Fields=[]
        
    def GetField(self, header, handle, path):
        splitted = path.partition(".")
        name = splitted[0]
        rest = splitted[2]
        offset = 0;
        for field in self.Fields:
            if field.Name.ShortName() == name:
                handle.seek(offset, os.SEEK_CUR)
                return field.DecodeField(header, handle, rest)
            else:
                offset += field.Size(header)

        return None
                            
    def SetField(self, header, handle, path, value):
        splitted = path.partition(".")
        name = splitted[0]
        rest = splitted[2]
        offset = 0;
        for field in self.Fields:
            if field.Name.ShortName() == name:
                handle.seek(offset, os.SEEK_CUR)
                return field.EncodeField(header, handle, rest, value)
            else:
                offset += field.Size(header)

        return None
                
            
        
######################################################
#    DNAField is a coupled DNAType and DNAName
#    Type=DNAType
#    Name=DNAName
######################################################
class DNAField:

    def __init__(self, aType, aName):
        self.Type = aType
        self.Name = aName
        
    def Size(self, header):
        if self.Name.IsPointer() or self.Name.IsMethodPointer():
            return header.PointerSize*self.Name.ArraySize()
        else:
            return self.Type.Size*self.Name.ArraySize()

    def DecodeField(self, header, handle, path):
        if path == "":
            if self.Name.IsPointer():
                return ReadPointer(handle, header)
            if self.Type.Name=="int":
                return ReadInt(handle, header)
            if self.Type.Name=="short":
                return ReadShort(handle, header)
            if self.Type.Name=="float":
                return ReadFloat(handle, header)
            if self.Type.Name=="char":
                return ReadString(handle, self.Name.ArraySize())
        else:
            return self.Type.Structure.GetField(header, handle, path)

    def EncodeField(self, header, handle, path, value):
        if path == "":
            if self.Type.Name=="char":
                return WriteString(handle, value, self.Name.ArraySize())
        else:
            return self.Type.Structure.SetField(header, handle, path, value)

#determine the relative production location of a blender path.basename
def blendPath2AbsolutePath(productionFile, blenderPath):
    productionFileDir=os.path.dirname(productionFile)
    if blenderPath.startswith("//"):
        relpath=blenderPath[2:]
        abspath = os.path.join(productionFileDir, relpath)
        return abspath
        
    
    return blenderPath
