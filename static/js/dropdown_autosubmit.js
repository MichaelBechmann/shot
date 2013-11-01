$(document).ready(function(){
	$('.js_hide').hide();
	$('select.autosubmit').change(function() {
       $('form').submit();
   });
});