// Closes popover when click outside of it if the event trigger
// (i.e the button) has the attribute data-close-on-outside-click='true'
$("html").click((e) => {
	// Check if click is outside a popover
	let isOutsidePopover = true;
	let elem = e.target;
	while (elem.parentNode) {
		if (elem.classList.contains("popover")) isOutsidePopover = false;
		elem = elem.parentNode;
	}
	if (isOutsidePopover) {
		$("[data-close-on-outside-click=true]").popover("hide");
	}
	// If the element clicked on is a button that has the attribute
	// data-toggle that starts with 'popover'(i.e. data-toggle='popover-form'),
	// show the element that was clicked. i.e. the popover that's button was clicked.
	if (e.target.dataset.toggle?.startsWith("popover")) {
		$(e.target).popover("show");
	}
});

$("[data-toggle=popover]").popover({
	html: true,
	sanitize: false,
});
