/**
 * Virtualizer - A virtual scrolling implementation for large tables
 *
 * This class implements efficient rendering of large tables by only displaying rows that are
 * currently visible in the viewport, plus a buffer area above and below. This significantly
 * improves performance when dealing with large datasets by reducing the number of DOM elements
 * actually present in the document.
 *
 * Usage:
 * ```javascript
 * const virtualizer = new Virtualizer({
 *   scrollAreaSelector: ".table_wrapper",
 *   rowSelector: "table tbody tr",
 *   filterFormId: "basicFilters"
 * });
 * ```
 */
class Virtualizer {
	constructor(config = {}) {
		// Default configuration options
		const defaultConfig = {
			bufferHeight: 400, // Height of buffer area above/below visible rows (px)
			scrollAreaSelector: ".table_wrapper", // CSS selector for the scrollable container
			rowSelector: "table tbody tr", // CSS selector for table rows
			rowTag: "tr", // HTML tag used for rows
			filterFormId: "basicFilters", // ID of the form containing filters
			keepParity: true, // Maintain even/odd row alternation
			loadBuffer: 1000, // Distance from bottom to trigger loading (px)
			loaderTemplate: null, // Custom HTML template for loader (default comes from `getDefaultLoaderTemplate`)
			processHtmx: false, // Enable HTMX processing
			scrollDebounce: 100, // Scroll event debounce time (ms)
			rowWrapperSelector: "table", // CSS selector for the row wrapper
			apiEndpoint: window.location.pathname, // API endpoint for fetching new rows
		};

		this.config = { ...defaultConfig, ...config };
		this.initializeState();
		this.initializeDOM();
		this.attachRefreshListener();

		if (this.isValidSetup()) {
			this.initialize();
		} else {
			console.error("Required elements not found");
		}
	}

	// Main initialization
	initialize() {
		this.controller = new AbortController();
		this.setInitialRows();
		this.attachScrollListener();
	}

	// State initialization
	initializeState() {
		this.state = {
			rows: [], // Array of all row objects with their positions and heights
			visibleRowDataList: [], // Array of visible row data
			loading: false, // Flag indicating if more rows are being loaded
			loadedLast: false, // Flag indicating if we've reached the end of available data
			start: 0, // Index of first visible row
			end: 0, // Index of last visible row
			scrolling: false, // Flag indicating if user is currently scrolling
			topSpacerHeight: 0, // Height of the top spacer
			bottomSpacerHeight: 0, // Height of the bottom spacer
			page: 1, // Current page number
			count: 0, // Total number of rows
			scrollTop: 0, // Current scroll position
		};
	}

	// DOM element initialization
	initializeDOM() {
		this.elements = {
			scrollArea: null, // Scrollable container element
			rowWrapper: null, // Container for the table rows
			tableHeader: null, // Table header element if present
			loader: null, // Loading indicator element
		};

		this.elements.scrollArea = document.querySelector(
			this.config.scrollAreaSelector,
		);
		// Find the row wrapper based on the first row's parent
		// const firstRow = this.elements.scrollArea?.querySelector(
		// 	this.config.rowSelector,
		// );
		this.elements.rowWrapper = this.elements.scrollArea.querySelector(
			this.config.rowWrapperSelector,
		);
		this.elements.tableHeader =
			this.elements.rowWrapper?.querySelector("thead");
		this.elements.loader = this.createLoader();
	}

	refresh() {
		this.controller.abort("Refreshed");
		this.setLoading(false);
		this.removeScrollListener();
		this.initializeState();
		this.initializeDOM();
		this.initialize();
	}

	attachRefreshListener() {
		document.addEventListener("htmx:afterRequest", (event) => {
			const target = event.detail.target;
			if (["table_wrapper", "gfl_table"].includes(target.id)) {
				this.refresh();
			}
		});
	}

	createLoader() {
		const loader = document.createElement(this.config.rowTag);
		loader.id = "loader";
		loader.innerHTML =
			this.config.loaderTemplate || this.getDefaultLoaderTemplate();
		return loader;
	}

	getDefaultLoaderTemplate() {
		const loaderContent = `
      <td colspan="100" class="p-3 bg-white">
        <div class="d-flex justify-content-center">
          <div class="spinner-border" role="status"></div>
        </div>
        <div class="d-flex justify-content-center">
            Loading...
        </div>
      </td>
    `;
		return this.config.rowTag === "tbody"
			? `<tr>${loaderContent}</tr>`
			: loaderContent;
	}

	// Validation check
	isValidSetup() {
		return this.elements.scrollArea && this.elements.rowWrapper;
	}

	// Row Processing Methods
	setInitialRows() {
		this.loadMoreRows();
	}

	processNewRows(newRows) {
		const { start, end } = this.calculateVisibleRange();
		this.updateState(start, end);
		this.renderVisibleRows(start, end);
		this.state.visibleRowDataList.push(...newRows);

		// Update the top spacer height
		const topHeight = this.state.rows[start]?.position || 0;
		this.state.topSpacerHeight = topHeight;
		this.state.bottomSpacerHeight = 0;
		this.onStateChange(this.state);

		// Calculate new row heights
		setTimeout(() => {
			const domRows = this.elements.rowWrapper.querySelectorAll(
				this.config.rowSelector,
			);
			const newRowElements = Array.from(domRows).slice(-newRows.length);
			let currentPosition = this.getLastRowPosition();
			for (let i = 0; i < newRowElements.length; i++) {
				const rowData = newRows[i];
				const rowElement = newRowElements[i];
				const rowHeight = rowElement.offsetHeight;
				this.state.rows.push({
					data: rowData,
					position: currentPosition,
					height: rowHeight,
				});
				currentPosition += rowHeight;
			}
			const { start, end } = this.calculateVisibleRange();
			this.updateState(start, end);
			if (this.shouldLoadMore()) {
				this.loadMoreRows();
			}
		}, 100);
	}

	getLastRowPosition() {
		const lastRow = this.state.rows[this.state.rows.length - 1];
		return lastRow ? lastRow.position + lastRow.height : 0;
	}

	// Scroll Handling
	attachScrollListener() {
		this.debouncedScroll = this.debounce(
			() => this.onScroll(),
			this.config.scrollDebounce,
		);
		this.elements.scrollArea.addEventListener("scroll", this.debouncedScroll);
	}

	removeScrollListener() {
		this.elements.scrollArea.removeEventListener(
			"scroll",
			this.debouncedScroll,
		);
	}

	onScroll() {
		// this.state.scrolling = false;
		// this.updateVisibleRows();
		this.state.scrollTop = this.elements.scrollArea.scrollTop;
		if (this.shouldLoadMore()) {
			this.loadMoreRows();
		} else {
			this.updateVisibleRows();
		}
		console.log("------------------");
		console.log("Scroll Top: ", this.state.scrollTop);
		console.log("Table Height: ", this.elements.rowWrapper.clientHeight);
		console.log("Top spacer height: ", this.state.topSpacerHeight);
		console.log(
			"Sum row heights: ",
			this.state.rows
				.slice(this.state.start, this.state.end)
				.reduce((acc, row) => acc + row.height, 0),
		);
		console.log("Bottom spacer height: ", this.state.bottomSpacerHeight);
	}

	debounce(func, wait) {
		let timeout;
		return (...args) => {
			clearTimeout(timeout);
			timeout = setTimeout(() => func.apply(this, args), wait);
		};
	}

	// Row Visibility Management
	updateVisibleRows() {
		const { start, end } = this.calculateVisibleRange();

		// if (this.state.start === start && this.state.end === end) return;
		if (
			start !== 0 &&
			end !== this.state.rows.length &&
			(Math.abs(this.state.start - start) < 3 ||
				Math.abs(this.state.end - end) < 3)
		)
			return;

		this.renderVisibleRows(start, end);
		this.updateState(start, end);
		this.updateSpacers(start, end);
		this.onStateChange(this.state);
	}

	calculateVisibleRange() {
		const topPosition = Math.max(
			0,
			this.elements.scrollArea.scrollTop - this.config.bufferHeight,
		);
		const windowHeight =
			this.elements.scrollArea.clientHeight + this.config.bufferHeight * 2;

		let start = this.getNearestIndex(topPosition);
		if (this.config.keepParity && start % 2 !== 0) {
			start--;
		}

		const end = Math.min(
			this.getNearestIndex(topPosition + windowHeight) + 1,
			this.state.rows.length,
		);

		return { start, end };
	}

	getNearestIndex(position) {
		if (position <= 0) return 0;
		let left = 0;
		let right = this.state.rows.length - 1;

		while (left <= right) {
			const mid = Math.floor((left + right) / 2);
			const midPosition = this.state.rows[mid].position;

			if (midPosition <= position) {
				left = mid + 1;
			} else {
				right = mid - 1;
			}
		}

		return right;
	}

	renderVisibleRows(start, end) {
		this.state.visibleRowDataList = this.state.rows
			.slice(start, end)
			.map((row) => row.data);
	}

	updateSpacers(start, end) {
		const lastRow = this.state.rows[this.state.rows.length - 1];
		const topHeight = this.state.rows[start].position;
		const bottomHeight = this.calculateBottomSpacerHeight(lastRow, end);

		this.state.topSpacerHeight = topHeight;
		this.state.bottomSpacerHeight = bottomHeight;
	}

	calculateBottomSpacerHeight(lastRow, end) {
		const lastVisibleRow = this.state.rows[Math.max(0, end - 1)];
		return (
			lastRow.position +
			lastRow.height -
			(lastVisibleRow.position + lastVisibleRow.height)
		);
	}

	updateState(start, end) {
		this.state.start = start;
		this.state.end = end;
	}

	onStateChange(state) {}

	// Data Loading
	loadMoreRows() {
		this.setLoading(true);

		this.fetchNewRows()
			.then((response) => response.json())
			.then((response) => {
				const newRows = response.results;

				if (newRows) {
					this.setLoading(false);
					this.processNewRows(newRows);
					this.state.page++;
					this.state.count = response.count;
				} else {
					this.state.loadedLast = true;
					this.setLoading(false);
				}
			})
			.catch((error) => {
				console.error("Error loading more rows:", error);
				this.setLoading(false);
			});
	}

	fetchNewRows() {
		const signal = this.controller.signal;
		return fetch(`${this.config.apiEndpoint}?${this.getQueryParams()}`, {
			signal,
		});
	}

	shouldLoadMore() {
		const lastVisibleRowPosition =
			this.state.rows[Math.max(0, this.state.end - 1)].position;
		const totalHeight = this.state.rows[this.state.rows.length - 1].position;
		return (
			lastVisibleRowPosition > totalHeight - this.config.loadBuffer &&
			!this.state.loadedLast &&
			!this.state.loading
		);
	}

	getQueryParams() {
		const form = document.getElementById(this.config.filterFormId);
		const params = new URLSearchParams(new FormData(form));
		params.append("page", this.state.page);
		// params.append("scrolling", "true");
		return params.toString();
	}

	setLoading(loading) {
		this.state.loading = loading;
		const loader =
			this.elements.rowWrapper.querySelector("#loader") || this.elements.loader;
		if (loading && loader.parentElement !== this.elements.rowWrapper) {
			this.elements.rowWrapper.appendChild(this.elements.loader);
		} else {
			this.elements.loader.remove();
		}
	}
}
