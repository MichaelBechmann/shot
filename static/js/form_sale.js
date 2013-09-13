$(document).ready(function(){
	
	$('.ctggltrig').each(function(){
		$(this).click( function(){
			$(this)
				.parent().parent()
				.next('.ctggl')
				.fadeToggle(600);
		});
		if(!($(this).is(':checked'))){
			$(this).parent().parent()
				.next('.ctggl')
				.hide();
		}	
	});
	
	$('#shift_descr').hide();
	$('#plclick').show();
	
	$('#shift_descr_tggl').click( function(){
		$('#shift_descr').slideToggle(1000);
		$('#plclick').toggle();
	});
	
	$('#shift_descr').click( function(){
		$(this).slideToggle(1000);
		$('#plclick').toggle();
	});
});

