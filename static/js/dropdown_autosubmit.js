$(document).ready(function(){
	$('.js_hide').hide();
	$('select').change(function() {
       $('form').submit();
   });
});