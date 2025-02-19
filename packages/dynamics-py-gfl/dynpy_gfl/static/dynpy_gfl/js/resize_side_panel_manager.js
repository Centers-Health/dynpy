const tablePanelResizeManager = () => {
	const tablePanelDivider = document.getElementById("table_panel_divider");
	const table = document.getElementById("gfl_table_wrapper");
	const body = document.querySelector("body");

	let cursorPosition = 0;
	let tableWidth = 0;

	// Handle the mousedown event that's triggered when user drags the divider
	const resizingStartedHandler = (e) => {
		body.classList.add("resizing");
		// Get the current mouse position
		Alpine.store("splitView").resizing = true;
		cursorPosition = e.clientX;
		tableWidth = table.getBoundingClientRect().width;

		document.addEventListener("mousemove", resizingInProgressHandler);
		document.addEventListener("mouseup", resizingFinishedHandler);
	};

	const resizingInProgressHandler = (e) => {
		e.preventDefault();
		// How far the mouse has been moved
		const amountMoved = e.clientX - cursorPosition;
		const newTableWidth =
			((tableWidth + amountMoved) * 100) /
			tablePanelDivider.parentNode.getBoundingClientRect().width;

		const sidePanelClosed = !Alpine.store("splitView").sidePanelOpen;

		// Don't allow them to make the side panel too small or too big or to resize it if it's closed
		if (10 < newTableWidth && newTableWidth < 80 && !sidePanelClosed) {
			const sidePanelWidth = 100 - newTableWidth;
			Alpine.store("splitView").tableWidth = `${newTableWidth}%`;
			Alpine.store("splitView").sidePanelWidth = `${sidePanelWidth}%`;
		}
	};

	const resizingFinishedHandler = () => {
		body.classList.remove("resizing");
		Alpine.store("splitView").resizing = false;
		document.removeEventListener("mousemove", resizingInProgressHandler);
		document.removeEventListener("mouseup", resizingFinishedHandler);
	};

	const initialize = () => {
		tablePanelDivider.addEventListener("mousedown", resizingStartedHandler);
	};

	return {
		initialize: initialize,
	};
};
