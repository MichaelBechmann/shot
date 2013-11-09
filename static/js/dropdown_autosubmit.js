$(document).ready(function(){
	$('.js_hide').hide();
	$('select.autosubmit').change(function() {
       $(this).parents('form').submit();
	});

});