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

// Adds ability to select/deselect all optgroup items
$(".selectpicker")
	.selectpicker()
	.on("loaded.bs.select", enableBoostrapSelectOptgroup);

function enableBoostrapSelectOptgroup() {
	const that = $(this).data("selectpicker");
	const inner = that.$menu.children(".inner");

	// Remove default event
	inner.off("click", ".divider, .dropdown-header");
	// Add new event
	inner.on("click", ".divider, .dropdown-header", function (e) {
		// Original functionality from bootstrap-select
		e.preventDefault();
		e.stopPropagation();
		if (that.options.liveSearch) {
			that.$searchbox.trigger("focus");
		} else {
			that.$button.trigger("focus");
		}

		// Extended functionality
		const position0 = that.isVirtual() ? that.selectpicker.view.position0 : 0;
		const clickedData =
			that.selectpicker.current.data[$(this).index() + position0];

		// Copied parts from changeAll function
		let selected = null;
		for (
			let i = 0, data = that.selectpicker.current.data, len = data.length;
			i < len;
			i++
		) {
			const element = data[i];
			if (element.type === "option" && element.optID === clickedData.optID) {
				if (selected === null) {
					selected = !element.selected;
				}
				element.option.selected = selected;
			}
		}
		that.setOptionStatus();
		that.$element.triggerNative("change");
	});
}
