function close(){
	// determine open element
	var open = $("#menu_staff > ul > li > ul:visible");
	open.stop(true,true).fadeOut(250);
	return open;
}

function menuout(obj){
	if(!obj.length) return;
	$(obj).bind( "clickoutside", function(event){
		close();
	});
}

function menuin(obj){
	if(!obj.length) return;
	$("#menu_staff ul").removeClass("expand");
	$(obj).click(function(){
		
		// close open item
		var old_item = close();
		var new_item = $(this).find('~ul');
		
		// open selected item if not just closed
		if(!( new_item.get(0) == old_item.get(0))){
			new_item.stop(true,true).fadeIn(350);
		}
		return false;
	});
}

$(document).ready(function(){
	menuin($("#menu_staff > ul > li.expand > a"));
	menuout($("#menu_staff > ul"));
});