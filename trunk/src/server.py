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
try:
    import SimpleHTTPServer
except:
    print("python 3: using http.server")
    import http.server as SimpleHTTPServer
try:    
    import SocketServer
except:
    print("python 3: using socketserver")
    import socketserver as SocketServer
    
import os
import exceptions

try:
    import json
except:
    print("python < 2.6: using simplejson")
    try:
        import simplejson as json
    except:
        print("ERROR: simplejson is not installed. Simplejson can be found at http://pypi.python.org/pypi/simplejson/")
        exit(-1)

import logging
import time
from string import Template
import indexer
import serviceproduction
import servicedependancy
import servicedownload
import servicerefactor
import settings
import sqlite3

log = logging.getLogger("server")

user_sessions = dict()
def getSession(user):
    """This functions gets the server session of a user. If the session does not exist it will be created

    Note: current implementation user is the same as ip address. not possible to support multiple users on a single ip address
    """
    if user not in user_sessions:
        session = {}
        session["css"] = settings.STYLE_SHEET
        user_sessions[user] = session
    return user_sessions[user]

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Handler of http requests for the server.

    The Handler is based on the SimpleHTTPRequestHandler. As additional the next things are added:
     1. when files ends with .html a templating will be used. The
         templating uses string substitute to change variables with session values
         example: ${production_id} will be replaced by session["production_id"]
     2. the post is rewritten to support JSON-like services.
     3. added thumbnails and svg and download file to the GET
    """
    def do_GET(self):
        if self.path.endswith(".html") or self.path.find(".html?")>0:
            self.doHandleHtml()
        elif self.path.startswith("/svg/dependancy.svg"):
            self.doHandleSVG()
        elif self.path.startswith("/svg/"):
            self.doHandleSVG2()
        elif self.path.startswith("/download/file"):
            self.doHandleDownloadFile()
        elif self.path.startswith("/thumbnail/256"):
            self.doHandleThumbnail(256)
        elif self.path.startswith("/thumbnail/512"):
            self.doHandleThumbnail(512)
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
            
    def do_POST(self):
        if self.path.startswith("/service/"):
            self.doHandleService()
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_POST(self)
    
    def handleParameters(self, url, dict):
        splitted=url.partition("?");
        url = splitted[0]
        attrline=splitted[2]
        for attr in attrline.split("&"):
            part = attr.partition("=")
            dict[part[0]]=part[2]
        
    def doHandleDownloadFile(self):
        session = getSession(self.client_address[0])
        request=dict()
        self.handleParameters(self.path,request)
        servicedownload.handleGet(self.wfile, request, session)

    def doHandleThumbnail(self, size):
        session = getSession(self.client_address[0])
        request=dict()
        self.handleParameters(self.path,request)
        servicedownload.handleGetThumbnail(self.wfile, request, session, size)
        
    def doHandleSVG(self):
        session = getSession(self.client_address[0])
        request=dict()
        self.handleParameters(self.path,request)
        servicedependancy.handleGetSVG(self.wfile, request, session)

    def doHandleSVG2(self):
        session = getSession(self.client_address[0])
        request=dict()
        res = self.path.split("/")
        #/svg/1/uses/all/detail/643
        tPath = "?view="+res[3]+"&filter="+res[4]+"&display="+res[5]+"&file_id="+res[6]+"&navigation="+res[2]
        self.handleParameters(tPath, request)
        servicedependancy.handleGetSVG(self.wfile, request, session)
        
    def doHandleHtml(self):
        session = getSession(self.client_address[0])
        self.handleParameters(self.path, session)

        filename = self.path[1:] #/index.html --> index.html
        splitted=filename.partition("?");
        filename = splitted[0]
            
        file = open(filename)
        content = file.read()
        file.close()
        template = Template(content)
        result = template.safe_substitute(session)
        self.wfile.write(result.encode())
        
        
    def doHandleService(self):
        try:
            servicename = self.path
            if servicename.find("?") != -1:
                servicename = servicename[0:servicename.find("?")]

            session = getSession(self.client_address[0])
            line = self.rfile.readline().decode();

            req = json.loads(line)
            log.info(servicename)
            if servicename=="/service/metafromproductionfiles":
                servicescenes.handleGetAll(self.wfile, req, session)

            elif servicename=="/service/productions":
                serviceproduction.handleGetAll(self.wfile, req, session)
            elif servicename=="/service/deleteproduction":
                serviceproduction.handleDelete(self.wfile, req, session)
            elif servicename=="/service/addproduction":
                serviceproduction.handleAdd(self.wfile, req, session)

            elif servicename=="/service/activateproduction":
                serviceproduction.handleActivateProduction(self.wfile, req, session)
            elif servicename=="/service/productionview":
                serviceproduction.handleGetProductionView(self.wfile, req, session)
            elif servicename=="/service/fileview":
                serviceproduction.handleGetFileView(self.wfile, req, session)
            elif servicename=="/service/dependancy":
                servicedependancy.handleGet(self.wfile, req, session)
            elif servicename=="/service/renamefile":
                servicerefactor.handleStartRenameFile(self.wfile, req, session)
            elif servicename=="/service/movefile":
                servicerefactor.handleStartMoveFile(self.wfile, req, session)
            elif servicename=="/service/renameelement":
                servicerefactor.handleStartRenameElement(self.wfile, req, session)
            elif servicename=="/service/refactoringtasks":
                servicerefactor.handleGetCurrentTasks(self.wfile, req, session)
            elif servicename=="/service/executetask":
                servicerefactor.handleExecuteOneTask(self.wfile, req, session)
            elif servicename=="/service/committasks":
                servicerefactor.handleCommitCurrentTasks(self.wfile, req, session)
            elif servicename=="/service/rollbacktasks":
                servicerefactor.handleRollbackCurrentTasks(self.wfile, req, session)
                
            elif servicename=="/service/missinglinksolutions":
                servicerefactor.handleGetMissingLinkSolutions(self.wfile, req, session)
            elif servicename=="/service/solvemissinglink":
                servicerefactor.handleStartSolveMissingLink(self.wfile, req, session)

        except sqlite3.Error:
            self.wfile.write("ERROR: A database error occured. Please check your database configuration in the settings file. Make sure you have removed the old database. If that does not solve the problem, send us an email.".encode())
        except exceptions.IndexError:
            self.wfile.write("ERROR: A database error occured. Please check your database configuration in the settings file. Make sure you have removed the old database. If that does not solve the problem, send us an email.".encode())

# if (settings.DEBUG == True):
#    traceback.print_tb()
            

# minimal web server.  serves files relative to the
# current directory.
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("blendfile").setLevel(logging.WARNING)
indexer.setup()
os.chdir("www")
httpd=None
log.info("Blender-aid "+str(settings.VERSION)+" ["+settings.VERSION_DESCRIPTION+"]")
log.info("starting server on "+str(settings.WEBSERVER_BINDING))
while httpd == None:
    try:
        httpd = SocketServer.TCPServer(settings.WEBSERVER_BINDING, MyHandler)
    except:
        httpd = None
        log.info("waiting")
        time.sleep(5)
        
log.info("server started on "+str(settings.WEBSERVER_BINDING))
log.info("browser to http://"+str(settings.WEBSERVER_BINDING[0])+":"+str(settings.WEBSERVER_BINDING[1])+"/")
httpd.serve_forever()
