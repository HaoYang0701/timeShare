$(document).ready(function(){

$(function(){
    document.getElementById('listing_loc').focus();
});

$(function(){
    document.getElementById('listing_tag').focus();
});

$(document.body).on( "blur", "#listing_tag", function() {  
	if ($('#listing_tag').val() != ""){
	var toTag = $("#listing_tag").val();
	$( "#listing_tag" ).hide();
	$( "#tag_label" ).hide();
	$('<div/>',{
    text: toTag,
    'class': 'chip  blue lighten-1 white-text',
	}).prependTo('#tagDiv');
	}
});
});