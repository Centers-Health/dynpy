function triggerChangeOnHide(e) {
	$(e.target).on("hidden.bs.select", (e) => {
		e.target.closest("form").dispatchEvent(new Event("change"));
	});
}
