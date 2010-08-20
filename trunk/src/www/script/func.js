function sh(ob, tagid) {
a = ob.getAttribute("class");
if (a=="open") {
	a = "close";
} else {
	a = "open";
}
ob.setAttribute("class", a);
elem = document.getElementById(tagid);
vis = elem.style;
// if the style.display value is blank we try to figure it out here
if(vis.display==''&&elem.offsetWidth!=undefined&&elem.offsetHeight!=undefined)
    vis.display = (elem.offsetWidth!=0&&elem.offsetHeight!=0)?'block':'none';
  vis.display = (vis.display==''||vis.display=='block')?'none':'block';
}

function serviceStartRenameFile(callback, productionId, fileId, newName) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/renamefile", true );
	xmlDoc.send( "{\"production_id\":"+productionId+", \"file_id\":"+fileId+",\"new_filename\":\""+newName+"\"}\r\n" );
	return xmlDoc;
}

function serviceStartSolveMissingLink(callback, productionId, elementId, fileId) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/solvemissinglink", true );
	xmlDoc.send( "{\"production_id\":"+productionId+",\"file_id\":"+fileId+",\"element_id\":"+elementId+"}\r\n" );
	return xmlDoc;
}

function serviceMissingLinkSolutions(callback, productionId, elementId) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/missinglinksolutions", true );
	xmlDoc.send( "{\"production_id\":"+productionId+", \"element_id\":"+elementId+"}\r\n" );
	return xmlDoc;
}

function serviceStartRenameElement(callback, productionId, fileId, elementId, newName) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/renameelement", true );
	xmlDoc.send( "{\"production_id\":"+productionId+", \"file_id\":"+fileId+", \"element_id\":"+elementId+",\"new_name\":\""+newName+"\"}\r\n" );
	return xmlDoc;
}
function serviceStartMoveFile(callback, productionId, fileId, newName) {
	str = newName.replace(/\\/g, "/")
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/movefile", true );
	xmlDoc.send( "{\"production_id\":"+productionId+", \"file_id\":"+fileId+",\"new_location\":\""+str+"\"}\r\n" );
	return xmlDoc;
}
function serviceRefactoringTasks(callback) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/refactoringtasks", true );
	xmlDoc.send( "{}\r\n" );
	return xmlDoc;
}
function servicePerformOneRefactoringTask(callback) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/executetask", true );
	xmlDoc.send( "{}\r\n" );
	return xmlDoc;
}
function serviceCommitTasks(callback) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/committasks", true );
	xmlDoc.send( "{}\r\n" );
	return xmlDoc;
}
function serviceRollbackTasks(callback) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/rollbacktasks", true );
	xmlDoc.send( "{}\r\n" );
	return xmlDoc;
}
function serviceDeleteProduction(callback, productionId) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/deleteproduction", true );
	xmlDoc.send( "{\"production_id\":"+productionId+"}\r\n" );
	return xmlDoc;
}
function serviceAddProduction(callback, productionName, productionLocation, svnurl, svnuser, svnpassword) {
	str = productionLocation.replace(/\\/g, "/")
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/addproduction", true );
	xmlDoc.send( "{\"production_name\":\""+productionName+"\",\"production_location\":\""+str+"\",\"production_svnurl\":\""+svnurl+"\",\"production_svnusername\":\""+svnuser+"\",\"production_svnpassword\":\""+svnpassword+"\"}\r\n" );
	return xmlDoc;
}
function serviceProductions(callback) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/productions", true );
	xmlDoc.send( "{}\r\n" );  
	return xmlDoc;
}
function serviceProductionView(callback) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/productionview", true );
	xmlDoc.send( "{}\r\n" );
	return xmlDoc;
}
function serviceActivateProduction(callback, productionId) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/activateproduction", true );
	xmlDoc.send( "{\"production_id\":"+productionId+"}\r\n" );
	return xmlDoc;
}
function serviceFileView(callback, productionId, fileId) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/fileview", true );
	xmlDoc.send( "{\"production_id\":"+productionId+",\"file_id\":"+fileId+"}\r\n" );
	return xmlDoc;
}

function serviceDependancies(callback, navigation, view, filter, display, fileId) {
	xmlDoc = new XMLHttpRequest();
	xmlDoc.onload = callback ;
	xmlDoc.open( "POST", "/service/dependancy", true );
	xmlDoc.send( "{\"display\":\"detail\",\"navigation\":\""+navigation+"\", \"view\":\""+view+"\",\"filter\":\""+filter+"\",\"file_id\":"+fileId+"}\r\n" );  //file_id
	return xmlDoc;
}


function booleanFactory(item, column, td) {
	value = eval("item."+column[2])
	if (value == 1) {
		value = "true"
	} else if (value == 0) {
		value = "false";
	}
	return document.createTextNode(value);
}
function endiannessFactory(item, column, td) {
	value = eval("item."+column[2])
	if (value == 1) {
		value = "little"
	} else if (value == 0) {
		value = "big";
	}
	return document.createTextNode(value);
}

function dateFactory(item, column, td) {
	tim = eval("item."+column[2])
	dt = new Date()
	dt.setTime(tim)
	
	return document.createTextNode(dt.toLocaleString())
}

function filesizeFactory(item, column, td) {
	result = defaultDom(item, column, td);
	td.setAttribute("style", "text-align:right")
	return result
}
function percentageFactory(item, column, td) {
	per = eval("item."+column[2])
	per = Math.round(per * 100)
	return document.createTextNode(per+" %")
}

function linkFactoryFile(item, column, td) {
	node = defaultDom(item, column, td);
	if (item.file_id!=null) {

		atag = document.createElement("a");
		atag.setAttribute("href", "#");
		atag.setAttribute("onclick", "javascript:selectFile("+item.file_id+");return false;");
		atag.appendChild(node);
		return atag
	} else {
		return node;
	}
}
function linkFactoryFileDepSource(item, column, td) {
	node = defaultDom(item, column, td);
	if (item.source_file_id!=null) {

		atag = document.createElement("a");
		atag.setAttribute("href", "#");
		atag.setAttribute("onclick", "javascript:selectFile("+item.source_file_id+");return false;");
		atag.appendChild(node);
		return atag
	} else {
		return node;
	}
}
function linkFactoryFileDepTarget(item, column, td) {
	node = defaultDom(item, column, td);
	if (item.target_file_id!=null) {

		atag = document.createElement("a");
		atag.setAttribute("href", "#");
		atag.setAttribute("onclick", "javascript:selectFile("+item.target_file_id+");return false;");
		atag.appendChild(node);
		return atag
	} else {
		return node;
	}
}

function fillSpan(spanname, value) {
	span = document.getElementById(spanname);
	clearChilderen(span)
	span.appendChild(document.createTextNode(value));
}
function clearChilderen(control) {
	while(control.hasChildNodes()){control.removeChild(control.childNodes[0]);}
}
function endsWith(str, other) {
	if (str == null) return false;
	if (str.length < other.length) {
		return false;
	}
	test = str.substring(str.length-other.length)
	if (test != other) {
		return false;
	}
	return true;	
}
function isBlendFile(filename){
	return endsWith(filename, ".blend");
}

function isImageFile(filename) {
	return endsWith(filename, ".png") || 
		endsWith(filename, ".jpg") || 
		endsWith(filename, ".jpeg") || 
		endsWith(filename, ".gif") || 
		endsWith(filename, ".exr") || 
		endsWith(filename, ".tga")
}
function isAudioFile(filename) {
	return endsWith(filename, ".wav")
}

// dom factory for returning the correct icon of a file.
function fileIconFactory(item, column, td) {
	filename = eval("item."+column[2]);
	iconfile ="images/unknownfile.png";
	if (isBlendFile(filename)) {
		iconfile="images/blendfile.png"
	}
	if (isImageFile(filename)) {
		iconfile="images/texturefile.png"
	}
	if (isAudioFile(filename)) {
		iconfile="images/audiofile.png"
	}
	if (endsWith(filename, ".py")) {
		iconfile="images/pythonfile.png"
	}
	if (endsWith(filename, ".txt")) {
		iconfile="images/textfile.png"
	}
	atag = document.createElement("img");
	atag.setAttribute("src", iconfile);
	atag.setAttribute("alt", "file");

	return atag
}

function taskIconFactory(item, column, td) {
	iconfile ="images/task.png";
	atag = document.createElement("img");
	atag.setAttribute("src", "images/task.png");
	return atag
}

// dom factory for returning the correct icon of a file.
function elementIconFactory(item, column, td) {
	type = eval("item."+column[2]);
	iconfile ="images/unknown.png";
	if (type=="CA") {
		iconfile="images/camera.png"
	} else
	if (type=="GR") {
		iconfile="images/group.png"
	} else
	if (type=="LA") {
		iconfile="images/lamp.png"
	} else
	if (type=="MA") {
		iconfile="images/material.png"
	} else
	if (type=="ME") {
		iconfile="images/mesh.png"
	} else
	if (type=="OB") {
		iconfile="images/object.png"
	} else
	if (type=="PA") {
		iconfile="images/particle.png"
	} else
	if (type=="SC") {
		iconfile="images/scene.png"
	} else
	if (type=="TE") {
		iconfile="images/texture.png"
	} else
	if (type=="WO") {
		iconfile="images/world.png"
	} else
	if (type=="IM") {
		iconfile="images/image.png"
	} else
	if (type=="AR") {
		iconfile="images/armature.png"
	} else
	if (type=="AC") {
		iconfile="images/action.png"
	} else
	if (type=="CU") {
		iconfile="images/curve.png"
	}

	atag = document.createElement("img");
	atag.setAttribute("src", iconfile);
	atag.setAttribute("alt", "element");

	return atag
}

function elementActionsFactory(item, column, td) {
	atag = document.createElement("a");
	atag.setAttribute("href", "#");
	atag.setAttribute("onclick", "javascript:startRenameElement("+item.element_id+");return false;");
	atag.appendChild(document.createTextNode("Rename"))
 	return atag;
}
function missingActionsFactory(item, column, td) {
	atag = document.createElement("a");
	atag.setAttribute("href", "#");
	atag.setAttribute("onclick", "javascript:selectMissingLinkSolution("+item.element_id+");return false;");
	atag.appendChild(document.createTextNode("Fix it"))
 	return atag;
}

function solveLinkFactory(item, column, td) {
	atag = document.createElement("a");
	atag.setAttribute("href", "#");
	atag.setAttribute("onclick", "javascript:startSolveMissingLink("+item.file_id+");return false;");
	atag.appendChild(document.createTextNode(eval("item."+column[2])))
 	return atag;
}


