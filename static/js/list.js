$.extend($.expr[':'], {
	containsExact: function(elem, i, m) {
        return $(elem).text() === m[3]; // m[3] contains the string in the parentheses of the call, see http://www.jameswiseman.com/blog/2010/04/19/creating-a-jquery-custom-selector/
	}

});
$(document).ready(function(){
	
	$('td:containsExact(True), span.value:containsExact(True)')
	.addClass("true");	
	$('td:containsExact(False), span.value:containsExact(False)')
	.addClass("false");	
	$('td:containsExact(None), span.value:containsExact(None), div.w2p_fw:containsExact(None)')
	.addClass("none");	
    // Loop through all the div.thatSetsABackgroundWithAnIcon on your page
    $('#ps_data_table td > div').each(function(){
          var $div = $(this);
          // Set the div's height to its parent td's height
          $div.height($div.closest('td').height());
    });
});