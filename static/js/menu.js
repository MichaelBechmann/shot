function close_sub_element(obj){
	// close all sub ul elements
	var open = obj.find('ul:visible');
	open.stop(true,false).fadeOut(50);
	return open;
}

function menuout(obj){
	if(!obj.length) return;
	$(obj).bind( "clickoutside", function(event){ // see http://benalman.com/projects/jquery-outside-events-plugin/
		close_sub_element($(this))
	});
}

function menuin(obj){
	if(!obj.length) return;
	$(obj).bind('click', function(){
		
		// close open item
		var a = $(this)
		var ul = a.parent().parent()
		
		var old_item = close_sub_element(ul)
		var new_item = a.find('~ul');
		
		// open selected item if not just closed
		if(!( new_item.get(0) == old_item.get(0))){
			new_item.stop(true,false).fadeIn(100);
		}
	});
}

$(document).ready(function(){
	menuout($(".menu > ul"));
	menuin ($(".menu li.expand > a"));
});