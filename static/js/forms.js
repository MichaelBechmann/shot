//Capitalize first letter while typing inside of input field

jQuery(document).ready(function($) {
	$('#person_forename__row, #person_name__row, #person_street__row, #person_place__row').keyup(function(event) {
		var textBox = event.target;
		var start = textBox.selectionStart;
		var end = textBox.selectionEnd;
		textBox.value = textBox.value.charAt(0).toUpperCase() + textBox.value.slice(1);
		textBox.setSelectionRange(start, end);
	});
});
