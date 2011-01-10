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
# (c) 2009, At Mind B.V. - Jeroen Bakker, Monique Dewanchand


######################################################
# Importing modules
######################################################
import indexer
import os
try:
    import json
except:
    import simplejson as json

RT_BLEND="resourcetype-blend"
RT_IMAGE="resourcetype-image"
RS_NORMAL="resourcestate-normal"
RS_MISSING="resourcestate-missing"
# request["navigation"]=="1" --> display navigation layer & enable a-refs to other files
# request["navigation"]=="0" --> hide navigation layer & disable a-refs to other files (default)
# request["view"]= "production" --> display total production
# request["view"] = "uses" --> only display used libraries from the current location (default)
# request["view"] = "user" --> only display files what uses the current location
# request["view"] = "neighbour" --> only display direct users and uses
# request["display"] = "detail" --> show all detail relations (default)
# request["display"] = "global" --> show only file dependancies
# request["filter"] = "ob,sc,ma,gr" --> filter on these elements
# request["filter"] = "" --> do not display anything?
# request["filter"] = "all" --> show everything
# request["file_id"] <-- if exist use this one, otherwise the session value
# session["file_id"] <-- will only be used, when request variant is not filed
# session["production_id"]
def handleGet(wfile, request, session):
    factory=DependanciesSVGFactory()
    # productionId, fileId
    productionId=session["production_id"]
    indexer.updateIndex(productionId)
    production = indexer.getProduction(productionId)
    fileId=request.get("file_id", session.get("file_id",None))
    
    detail = request.get("display", "detail") == "detail"
    view = request.get("view", "uses")
    factory.RenderNavigation=request.get("navigation", "0")=="1"
    factory.Detail = detail
    filter = request.get("filter", "all")

    factory.Production=production
    
    result=[]

    if fileId == None:
        view="production"
        
    if view == "production":
        result = indexer.queryDependancy(productionId, filter)
    if view == "uses":
        result = indexer.queryDependancyUses(productionId, fileId, filter)
    if view == "used":
        result = indexer.queryDependancyUsed(productionId, fileId, filter)
    if view == "neighbour":
        result = indexer.queryDependancyNeighbour(productionId, fileId, filter)

    items = []
    
    for item in result:
        rec = {}
        rec["source_file_id"]=item[4]
        rec["source_file_location"]=item[0]
        rec["target_file_id"]=item[5]
        rec["target_file_location"]=item[1]
        rec["element_name"]=item[3]
        rec["element_type"]=item[2]
        items.append(rec)

    wfile.write(json.dumps(items).encode());


def handleGetSVG(wfile, request, session):
    factory=DependanciesSVGFactory()
    # productionId, fileId
    productionId=session["production_id"]
    indexer.updateIndex(productionId)
    production = indexer.getProduction(productionId)
    fileId=request.get("file_id", session.get("file_id",None))
    
    detail = request.get("display", "detail") == "detail"
    view = request.get("view", "uses")
    factory.RenderNavigation=request.get("navigation", "0")=="1"
    factory.Detail = detail
    filter = request.get("filter", "all")

    factory.Production=production
    
    result=[]

    if fileId == None:
        view="production"
        
    if view == "production":
        result = indexer.queryDependancy(productionId, filter)
    if view == "uses":
        result = indexer.queryDependancyUses(productionId, fileId, filter)
    if view == "used":
        result = indexer.queryDependancyUsed(productionId, fileId, filter)
    if view == "neighbour":
        result = indexer.queryDependancyNeighbour(productionId, fileId, filter)

    if detail:
        display="detail"
    else:
        display="global"
    factory.URLTemplate = "/".join(["svg", "1", view, filter, display])

    factory.Render(wfile, result)

class Relative:
    def __init__(self):
        self.Name = None
        self.Uses=[]
        self.UsedBy=[]
        self.Level=0
        self.FileId=None
        self.x = 0
        self.y = 0
        self.ConnectionPoints = None
        
    def Height(self):
        temp=[]
        for relation in self.UsedBy:
            res = relation.Type+relation.Name
            if res not in temp:
                temp.append(res)
        ho = len(temp)
        if ho == 0:
            ho = 1
        return 25+(10*(ho-1))

    def GetConnectionPoint(self, relation):
        if self.ConnectionPoints == None:
            self.ConnectionPoints=[]
            for relation1 in self.UsedBy:
                res = relation1.Type+relation1.Name
                if res not in self.ConnectionPoints:
                    self.ConnectionPoints.append(res)
            self.ConnectionPoints = sorted(self.ConnectionPoints)
        key = relation.Type+relation.Name
        res = self.ConnectionPoints.index(key)+1
        return self.y+(res*10)
        
    def Type(self):
        if self.Name.endswith(".blend"):
            return RT_BLEND
        else:
            return RT_IMAGE
        
    def State(self):
        if self.Name.startswith("../../../"):
            return RS_MISSING
        else:
            if os.path.exists(os.path.join(self.Production[2], self.Name)):
                return RS_NORMAL
            else:
                return RS_MISSING
        
class Relation:
    def __init__(self):
        self.Source=None
        self.Target=None
        self.Type=""
        self.Name=""
        
class Level:
    def __init__(self):
        self.Relatives=[]
        
    def append(self, relative):
        if len(self.Relatives) == 0:
            relative.y = 0
        else:
            previous = self.Relatives[len(self.Relatives)-1]
            relative.y = previous.y + previous.Height() + 10

        self.Relatives.append(relative)
        
    def Height(self):
        result = 0;
        for relative in self.Relatives:
            result = result + relative.Height()
            result = result + 10
        result = result - 10
        return result
        
class Levels:
    def __init__(self):
        self.Levels=[]
        
    def append(self, relative):
        levno = relative.Level
        while len(self.Levels) <levno+1:
            self.Levels.append(Level())
        level = self.Levels[levno]
        level.append(relative)
        
    def lineout(self):
        hei = 0
        for level in self.Levels:
            nhei = level.Height()
            if nhei> hei:
                hei = nhei
        
        for level in self.Levels:
            nhei = level.Height()
            dif = hei-nhei
            dif = dif / 2
            for relative in level.Relatives:
                relative.y = relative.y + dif
            
            
NAVIGATION="""<g id="controls" transform="translate(50,50) scale(0.5, 0.5)"><circle cx="0" cy="0" r="86" style="fill:#ffffff;stroke:#000000;stroke-width:1;"></circle>
    <rect transform="rotate(-45,0,0)"
       style="fill:none;stroke:#000000;stroke-width:1"
       id="rect2383"
       width="128"
       height="128"
       x="-64"
       y="-64"
       rx="32"
       ry="32"
 />

    <rect
       style="fill:none;stroke:#000000;stroke-width:1"
       id="rect2383"
       width="128"
       height="32"
       x="-64"
       y="-16"
       rx="32"
       ry="32"
 />
    <rect
       style="fill:none;stroke:#000000;stroke-width:1"
       id="rect2383"
       width="32"
       height="128"
       x="-16"
       y="-64"
       rx="32"
       ry="32"
 />
<circle cx="0" cy="48" r="20" style="fill:#a0a0a0;stroke:#000000;stroke-width:1;" onclick="doMoveY(evt, -100)"></circle>
<circle cx="0" cy="-48" r="20" style="fill:#a0a0a0;stroke:#000000;stroke-width:1;" onclick="doMoveY(evt, 100)"></circle>
<circle cx="48" cy="0" r="20" style="fill:#a0a0a0;stroke:#000000;stroke-width:1;" onclick="doMoveX(evt, -100)"></circle>
<circle cx="-48" cy="0" r="20" style="fill:#a0a0a0;stroke:#000000;stroke-width:1;" onclick="doMoveX(evt, 100)"></circle>

    <rect
       style="fill:#ffffff;stroke:#000000;stroke-width:1"
   
       width="32"
       height="128"
       x="134"
       y="-64"
       rx="32"
       ry="32"
 />

<circle cx="150" cy="-48" r="25" style="fill:#a0a0a0;stroke:#000000;stroke-width:1;" onclick="doZoomOut(evt)"></circle>
<circle cx="150" cy="48" r="15" style="fill:#a0a0a0;stroke:#000000;stroke-width:1;" onclick="doZoomIn(evt)"></circle>

""".encode()        

HEADER="""<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg width="100%" height="100%" version="1.1"
xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
	<defs>
		<linearGradient id="normal" x1="0%" y1="0%" x2="100%" y2="100%">
			<stop offset="0%" style="stop-color:rgb(255,255,0);stop-opacity:1"/>
			<stop offset="100%" style="stop-color:rgb(255,0,0);stop-opacity:1"/>
		</linearGradient>
		<linearGradient id="selected" x1="0%" y1="0%" x2="100%" y2="100%">
			<stop offset="0%" style="stop-color:rgb(0,255,0);stop-opacity:1"/>
			<stop offset="100%" style="stop-color:rgb(0,0,255);stop-opacity:1"/>
		</linearGradient>
		<linearGradient id="selected2" x1="0%" y1="0%" x2="100%" y2="100%">
			<stop offset="0%" style="stop-color:rgb(128,255,0);stop-opacity:1"/>
			<stop offset="100%" style="stop-color:rgb(128,0,128);stop-opacity:1"/>
		</linearGradient>

        <filter id="shadowblur">
            <feGaussianBlur in="SourceGraphic" stdDeviation="5"/>
        </filter>
	</defs>
	<script type="text/ecmascript"> <![CDATA[

function selectRect(document, fileid) {
   var element = document.getElementById(fileid);
   element.setAttribute("class", "selected2");
}
function selectText(document, textid) {
   var element = document.getElementById(textid);
    var cl = element.getAttribute("class")
    if (cl == null || cl == "") {
        element.setAttribute("class", "selected");
    }
}

function selectPaths(document, fileid) {
   var elements = document.getElementsByTagName("path");
   for (i = 0 ; i < elements.length ; i ++) {
       var element = elements.item(i);
       var sfi = element.getAttribute("sourcefileid");
       var tfi = element.getAttribute("targetfileid");
       if (fileid == sfi ||
           fileid == tfi) {
           element.setAttribute("class", "selected");
            selectText(document, element.getAttribute("textid"))
           selectRect(document, sfi)
           selectRect(document, tfi)
       } else {
           element.setAttribute("class", "");
       }
   }
}

function selectPathsFromTextId(document, textid) {
   var elements = document.getElementsByTagName("path");
   for (i = 0 ; i < elements.length ; i ++) {
       var element = elements.item(i);
        var text = element.getAttribute("textid")
        if (text == textid) {
            var sfi = element.getAttribute("sourcefileid");
            var tfi = element.getAttribute("targetfileid");
           element.setAttribute("class", "selected");
           selectRect(document, sfi)
           selectRect(document, tfi)
       } else {
           element.setAttribute("class", "");
       }
   }
}

function mouseoverfile(evt) {
   var rect = evt.target;
   var document = rect.ownerDocument;
   var fileid = rect.getAttribute("id")
   selectPaths(document, fileid);
   rect.setAttribute("class", "selected");
}
function mouseoutfile(evt) {
   var rect = evt.target;
   var document = rect.ownerDocument;
   selectPaths(document, "");
   rect.setAttribute("class", "file");
   var elements = document.getElementsByTagName("rect");
   for (i = 0 ; i < elements.length ; i ++) {
       var element = elements.item(i);
       element.setAttribute("class", "file");
    }
   var elements = document.getElementsByTagName("text");
   for (i = 0 ; i < elements.length ; i ++) {
       var element = elements.item(i);
        if (element.getAttribute("class")=="selected") {
            element.setAttribute("class", "");
        }
    }
}
function mouseovertext(evt) {
    return;
   var text = evt.target;
   var document = text.ownerDocument;
   var textid = text.getAttribute("id")
    selectPathsFromTextId(document, textid);
   text.setAttribute("class", "selected");
}
function mouseouttext(evt) {
    return;
   var text = evt.target;
   var document = text.ownerDocument;
   var textid = text.getAttribute("id")

   var elements = document.getElementsByTagName("rect");
   for (i = 0 ; i < elements.length ; i ++) {
       var element = elements.item(i);
       element.setAttribute("class", "file");
    }

   var elements = document.getElementsByTagName("text");
   for (i = 0 ; i < elements.length ; i ++) {
       var element = elements.item(i);
        if (element.getAttribute("class")=="selected") {
            element.setAttribute("class", "");
        }
    }
   text.setAttribute("class", "");
}

var scale = 1.0
var translateX = 0.0
var translateY = 0.0

function updateGroup(doc) {
	group = doc.getElementById("dependancies");
	group.setAttribute("transform", "translate("+translateX+","+translateY+") scale("+scale+")");
}
function doZoomIn(event) {
	scale = scale - 0.1;
	updateGroup(event.target.ownerDocument);
}
function doZoomOut(event) {
	scale = scale +0.1;
	updateGroup(event.target.ownerDocument);
}
function doMoveX(event, amount) {
	translateX = translateX + amount;
	updateGroup(event.target.ownerDocument);
}
function doMoveY(event, amount) {
	translateY = translateY + amount;
	updateGroup(event.target.ownerDocument);
}
]]>
</script>
	<style type="text/css">

rect.file {
      fill:url(#normal);
	stroke:black;
	stroke-width:5;
	filter:url(#Gaussian_Blur);
    }
    rect.selected {
	stroke:black;
	stroke-width:5;
	filter:url(#Gaussian_Blur);
      fill:url(#selected);
    }
    rect.selected2 {
	stroke:black;
	stroke-width:5;
	filter:url(#Gaussian_Blur);
      fill:url(#selected2);
    }
path.connector {
	fill:none;
	stroke:rgb(255,0,0);
	stroke-width:1
}
path.selected {
	fill:none;
	stroke:rgb(0,128,0);
	stroke-width:2
}
text {
    font-family:verdana;
	font-size:10px;
}
text.file {
    font-family:verdana;
	font-size:10px;
}
path.shadow {
    filter:url(#shadowblur);
	fill:#000000;
    stoke-width:0px;
}

path.border {
    fill:none;
    stroke-width:1;
    stroke:#000000;
}

path.resourcetype-blend {
    fill:orange
}
path.resourcetype-image {
    fill:#8080FF;
}

path.resourcestate-normal {
    fill:grey
}
path.resourcestate-missing {
    fill:red
}

text.selected {
    font-family:verdana;
	font-size:10px;
    stroke:rgb(0,0,0);
    stroke-width:1.2;
}
	</style>""".encode()
    
class DependanciesSVGFactory():
    def Render(self, out, rels):
        relatives = dict()
        done=[]
        
        for line in rels:
            relName1 = line[0] #target/blend
            relName2 = line[1] #source/lib
            testName = relName1+"|"+relName2
            if testName not in done:
                
                if relName1 not in relatives:
                    rel = Relative()
                    rel.Name = relName1
                    rel.Production=self.Production
                    rel.FileId=line[4]
                    relatives[relName1] = rel

                if relName2 not in relatives:
                    rel = Relative()
                    rel.Name = relName2
                    rel.Production=self.Production
                    rel.FileId=line[5]
                    relatives[relName2] = rel

                rel1 = relatives[relName1]
                rel2 = relatives[relName2]
                relation = Relation()
                relation.Target = rel1
                relation.Source = rel2
                if self.Detail:
                    relation.Type = line[2]
                    relation.Name = line[3]
                else:
                    relation.Type=""
                    relation.Name=""
                rel1.Uses.append(relation)
                rel2.UsedBy.append(relation)

                if not self.Detail:
                    done.append(testName)
            
            
        out.write(HEADER)

#First pass. Just make an initial tree        
        for i in range(100):
            for relative in relatives.values():
                for relation in relative.Uses:
                    if relation.Target.Level<=relation.Source.Level:
                        relation.Source.Level = relation.Target.Level-1
                    
                    
        for i in range(100):
#Second pass. make all higher level adjust to max uses.Level                     
            for relative in relatives.values():
                if len(relative.Uses)>0:
                    max = -10000000
                    for relation in relative.Uses:
                        if relation.Source.Level>max:
                            max = relation.Source.Level
                    relative.Level = max + 1
                    
#Third pass. make all higher level adjust to max uses.Level
            for relative in relatives.values():
                if len(relative.UsedBy)>0:
                    min = 10000000
                    for relation in relative.UsedBy:
                        if relation.Target.Level<min:
                            min = relation.Target.Level
                    relative.Level = min - 1

#find min level
        minLevel = 0
        for relative in relatives.values():
            if relative.Level < minLevel:
                minLevel = relative.Level

#make x coordinates
        y = 0
        levels = Levels()
        for relative in relatives.values():
            relative.Level = relative.Level - minLevel
            relative.x = 10+relative.Level*400
            levels.append(relative)
            
        levels.lineout()
        
        out.write("<g id=\"dependancies\" onload=\"initialize(evt)\">".encode())
        #lines        
        for relative in relatives.values():
            for relation in relative.Uses:
                sx = relation.Source.x+200
                sy = relation.Source.GetConnectionPoint(relation)
                tx = relation.Target.x
                ty = relation.Target.y+10
                sfi = relation.Source.Name
                tfi = relation.Target.Name
                dx = (sx+tx)/2
                textid = relation.Source.Name+"#"+relation.Type+relation.Name
                out.write(("<g><path class=\"connector\" textid=\""+textid+"\" sourcefileid=\""+sfi+"\" targetfileid=\""+tfi+"\" object=\"\" d=\"M"+str(sx)+" "+str(sy)+" C"+str(dx)+" "+str(sy)+" "+str(dx)+" "+str(ty)+" "+str(tx)+" "+str(ty)+"\" /></g>").encode())
                out.write("\r\n".encode())
        #text
        if self.Detail:
            for relative in relatives.values():
                temp = []
                for relation in relative.UsedBy:
                    sx = relation.Source.x+200
                    sy = relation.Source.GetConnectionPoint(relation)
                    text = "["+relation.Type+"] "+relation.Name
                    textid = relation.Source.Name+"#"+relation.Type+relation.Name
                    if text not in temp:
                        out.write(("<g><text id=\""+textid+"\" onmouseover=\"mouseovertext(evt)\" onmouseout=\"mouseouttext(evt)\" x=\""+str(sx+5)+"\" y=\""+str(sy+4)+"\">"+text+"</text></g>").encode())
                        out.write("\r\n".encode())
                        temp.append(text)
        #boxes
        for relative in relatives.values():
            if self.RenderNavigation:
                if relative.FileId!=None:
                    url = "/"+self.URLTemplate+"/"+str(relative.FileId)
                    out.write(("<a xlink:href=\""+url+"\" >").encode())
            out.write("<g>".encode())
            createBox(out, relative.x, relative.y, 200, relative.Height(), relative.Type(),relative.State())
            out.write(("<text class=\"file\" x=\""+str(relative.x+24)+"\" y=\""+str(relative.y+15)+"\" >"+relative.Name+"</text></g>").encode())
            if self.RenderNavigation:
                if relative.FileId!=None:
                    out.write("</a>".encode())
            out.write("\r\n".encode())

        out.write("</g>".encode())
        if self.RenderNavigation:
            
            out.write(NAVIGATION)
            out.write("""</g>""".encode())
        out.write("</svg>".encode())
                      
def createBox(out, x, y, width, height, type, state):
    if width<100:
        width=100
    if height<32:
        height=32
    x2=x+width
    y2=y+height
    
    sx10=str(x)
    sx11=str(x+16)
    sx12=str(x+20)
    sy10=str(y)
    sy11=str(y+16)

    sx20=str(x2)
    sx21=str(x2-16)
    sy20=str(y2)
    sy21=str(y2-16)
    
    
    out.write(("<path class=\"shadow\" transform=\"translate(5,5)\" d=\"M "+sx12+","+sy10+" L "+sx21+","+sy10+" C "+sx20+","+sy10+" "+sx20+","+sy11+" "+sx20+","+sy11+" L "+sx20+","+sy21+" C "+sx20+","+sy20+" "+sx21+","+sy20+" "+sx21+","+sy20+" L "+sx11+","+sy20+" C "+sx10+","+sy20+" "+sx10+","+sy21+" "+sx10+","+sy21+" L "+sx10+","+sy11+" C "+sx10+","+sy10+" "+sx11+","+sy10+" "+sx11+","+sy10+" z\" opacity=\".3\"/>").encode())
    out.write(("<path id=\"state\" class=\""+state+"\" d=\"M "+sx12+","+sy10+" L "+sx21+","+sy10+" C "+sx20+","+sy10+" "+sx20+","+sy11+" "+sx20+","+sy11+" L "+sx20+","+sy21+" C "+sx20+","+sy20+" "+sx21+","+sy20+" "+sx21+","+sy20+" L "+sx12+","+sy20+" z\" />").encode())
    out.write(("<path id=\"resourcetype\" class=\""+type+"\" d=\"M "+sx10+","+sy11+" C "+sx10+","+sy10+" "+sx11+","+sy10+" "+sx11+","+sy10+" L "+sx12+","+sy10+" L "+sx12+","+sy20+" L "+sx11+","+sy20+" C "+sx10+","+sy20+" "+sx10+","+sy21+" "+sx10+","+sy21+" z\" />").encode())
    out.write(("<path d=\"M "+sx12+","+sy10+" L "+sx21+","+sy10+" C "+sx20+","+sy10+" "+sx20+","+sy11+" "+sx20+","+sy11+" L "+sx20+","+sy21+" C "+sx20+","+sy20+" "+sx21+","+sy20+" "+sx21+","+sy20+" L "+sx11+","+sy20+" C "+sx10+","+sy20+" "+sx10+","+sy21+" "+sx10+","+sy21+" L "+sx10+","+sy11+" C "+sx10+","+sy10+" "+sx11+","+sy10+" "+sx11+","+sy10+" z\" class=\"border\" />").encode())
    