
function htmlColorToRGB(htmlColor) {
	reg = /^(\w{2})(\w{2})(\w{2})$/
	if (htmlColor.charAt(0) == '#') {
      	htmlColor= htmlColor.substr(1,6);
	}
	bits = reg.exec(htmlColor);
	result = [parseInt(bits[1], 16), parseInt(bits[2], 16), parseInt(bits[3], 16)];
	return result;
}

function htmlColorDiff(htmlcolor1, htmlcolor2) {
	rgb1 = htmlColorToRGB(htmlcolor1);
	rgb2 = htmlColorToRGB(htmlcolor2);
	dif = Math.abs(rgb1[0] - rgb2[0]);
	dif += Math.abs(rgb1[1] - rgb2[1]);
	dif += Math.abs(rgb1[2] - rgb2[2]);
	return dif;
}

function initColorChoser(control, name) {
	t = ["00", "33", "66", "99", "bb", "ff"];
	for (r = 0 ; r < 6 ; r ++) {
	for (g = 0 ; g < 6 ; g ++) {
	for (b = 0 ; b < 6 ; b ++) {
		c = t[r]+t[g]+t[b];
		item = document.createElement("option");
		item.setAttribute("value", c);
		item.setAttribute("style", "background-color:"+c+";");
		item.appendChild(document.createTextNode(c));
		control.appendChild(item);

	}
	}
	}
}


