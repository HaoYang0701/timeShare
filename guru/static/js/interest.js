$(document).ready(function(){
   	var Intro = function() {
       $('#Intromodal').openModal();
	};

	document.getElementById("submitInterests").onclick = function() {
    	document.getElementById("checkInterestForm").submit();
	}
	
	Intro();
});
