/*
Template Name: HUD - Responsive Bootstrap 5 Admin Template
Version: 2.4.0
Author: Sean Ngu
Website: http://www.seantheme.com/hud/
*/

var handleRenderTableData = function() {
	var table = $('#datatableDefault').DataTable({
		dom: "<'row mb-3'<'col-sm-4'l><'col-sm-8 text-end'<'d-flex justify-content-end'fB>>>t<'d-flex align-items-center mt-3'<'me-auto'i><'mb-0'p>>",
    lengthMenu: [  10, 20, 30, 40, 50  ],
		responsive: false,
		buttons: []
	});
};


/* Controller
------------------------------------------------ */
$(document).ready(function() {
	handleRenderTableData();
});