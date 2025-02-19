const adjustScroll = () => {
	const target = window.location.hash.substring(1);
	if (!target) {
		return;
	}
	window.location.hash = ""; // Stops browser auto scroll

	// We want to remove the  hash from the url.  Although the above line does that well, later on in the code (split_view.js) we
	// run history.replaceState with the global url variable (defined in generic_filter_list.js) as a parmater, and that global variable already has a hash.
	// Thus we here remove the hash from the global url variable.
	if (typeof url !== "undefined") {
		url.hash = "";
	}

	const tableWrapper = document.getElementsByClassName("table_wrapper")[0];
	const headerHeight = tableWrapper.querySelector("thead").clientHeight;
	const row = document.getElementById(target);
	if (row) {
		const rowTop = row.offsetTop;
		tableWrapper.scrollTo({
			top: rowTop - headerHeight,
		});
	}
};

window.addEventListener("load", () => {
	adjustScroll();
});
