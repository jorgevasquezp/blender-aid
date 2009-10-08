function initTab(tab, tabname) {
	tab.addTab=addTab;
	tab.update=update;
	tab.hideAllTabs=hideAllTabs
	tab.hideLayer=hideLayer
	tab.showLayer=showLayer
	tab.hideTabLink=hideTabLink
	tab.items=[];
	tab.setAttribute("class", "tabs")
}

function addTab(anchorId, layerId) {
	anchor = document.getElementById(anchorId)
	anchor.setAttribute("onclick", "javascript:showTab(this, '"+this.id+"', '"+layerId+"');return false")
	anchor.setAttribute("href", "#")
	this.items.push([anchorId, layerId])
}

function update() {
	this.hideAllTabs()
	this.showLayer(this.items[0])
}

function showTab(element, tabId, layerName) {
	tabs = document.getElementById(tabId)
	tabs.hideAllTabs()
	tabs.showLayer([element.id, layerName])
}

function hideAllTabs() {
	for (i=0 ; i < this.items.length ; i++) {
		item = this.items[i]
		this.hideLayer(item)
	}
}

function hideTabLink(linkId) {
	link = document.getElementById(linkId)
	link.parentNode.setAttribute("style", "display:none;")
}

function hideLayer(item) {
	anc=document.getElementById(item[0]);
	anc.setAttribute("class", "")
	anc.parentNode.setAttribute("class", "")
	document.getElementById(item[1]).setAttribute("style", "display:none")
}

function showLayer(item) {
	anc=document.getElementById(item[0]);
	anc.setAttribute("class", "selected")
	anc.parentNode.setAttribute("class", "selected")
	document.getElementById(item[1]).setAttribute("style", "display:block")
}
