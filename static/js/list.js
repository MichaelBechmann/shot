$.extend($.expr[':'], {
	containsExact: function(elem, i, m) {
        return $(elem).text() === m[3]; // m[3] contains the string in the parentheses of the call, see http://www.jameswiseman.com/blog/2010/04/19/creating-a-jquery-custom-selector/
	}

});


$(document).ready(function(){
	
	$('td:containsExact(True)')
	.addClass("true");	
	$('td:containsExact(False)')
	.addClass("false");	
	$('td:containsExact(None)')
	.addClass("none");	
	
});