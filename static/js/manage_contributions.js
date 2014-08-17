function setExpand(elements){
	elements.removeClass('ccollapse').addClass('cexpand');
}
function setCollapse(elements){
	elements.removeClass('cexpand').addClass('ccollapse');
}

$(document).ready(function(){
	$('.ctggl').hide();
	$('.ctggltrig').addClass('cexpand');
	$('.ctggltrig').click(function(){
		$(this)
			.parent()
			.next('.ctggl')
			.fadeToggle(600);
		if($(this).filter('.cexpand').size() > 0){
			setCollapse($(this));
		} else{
			setExpand($(this));
		}
	});
	
	
	$('.cexpand:not(.ctggltrig)').click(function(){
		$('.ctggl').slideDown(600);
		setCollapse($('.ctggltrig'));
	});
	
	$('.ccollapse:not(.ctggltrig)').click(function(){
		$('.ctggl').slideUp(600);
		setExpand($('.ctggltrig'));
	});
});

