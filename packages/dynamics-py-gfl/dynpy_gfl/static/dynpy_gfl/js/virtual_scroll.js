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
			processHtmx: true, // Enable HTMX processing
			scrollDebounce: 100, // Scroll event debounce time (ms)
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
		if (this.config.processHtmx) {
			this.disableHtmxLoadTriggers();
		}
		this.controller = new AbortController();
		this.setInitialRows();
		this.attachScrollListener();
	}

	// State initialization
	initializeState() {
		this.state = {
			rows: [], // Array of all row objects with their positions and heights
			loading: false, // Flag indicating if more rows are being loaded
			loadedLast: false, // Flag indicating if we've reached the end of available data
			start: 0, // Index of first visible row
			end: 0, // Index of last visible row
			scrolling: false, // Flag indicating if user is currently scrolling
		};
	}

	// DOM element initialization
	initializeDOM() {
		this.elements = {
			scrollArea: null, // Scrollable container element
			rowWrapper: null, // Container for the table rows
			tableHeader: null, // Table header element if present
			topSpacer: null, // Spacer element above visible rows
			bottomSpacer: null, // Spacer element below visible rows
			loader: null, // Loading indicator element
		};

		this.elements.scrollArea = document.querySelector(
			this.config.scrollAreaSelector,
		);
		// Find the row wrapper based on the first row's parent
		const firstRow = this.elements.scrollArea?.querySelector(
			this.config.rowSelector,
		);
		this.elements.rowWrapper = firstRow?.parentElement;
		this.elements.tableHeader =
			this.elements.rowWrapper?.querySelector("thead");
		this.elements.topSpacer = this.createSpacer("topSpacer");
		this.elements.bottomSpacer = this.createSpacer("bottomSpacer");
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

	// DOM Element Creation Methods
	createSpacer(id) {
		const spacer = document.createElement(this.config.rowTag);
		spacer.id = id;
		spacer.style.height = "0px";
		return spacer;
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
		const existingRows = this.elements.rowWrapper.querySelectorAll(
			this.config.rowSelector,
		);
		this.processNewRows(existingRows);
	}

	processNewRows(newRows) {
		const startPosition = this.getLastRowPosition();
		let currentPosition = startPosition;

		for (const row of newRows) {
			this.appendRowToWrapper(row);
			currentPosition = this.addRowToCollection(row, currentPosition);
		}

		this.removeProcessedRows(newRows);
		this.updateAfterProcessing();
	}

	updateAfterProcessing() {
		if (!this.state.scrolling) {
			const { start, end } = this.calculateVisibleRange();

			if (this.state.start !== start || this.state.end !== end) {
				this.renderVisibleRows(start, end);
				this.updateState(start, end);
			} else {
				this.updateBottomSpacer();
			}
		}

		if (this.shouldLoadMore()) {
			this.loadMoreRows();
		}
	}

	getLastRowPosition() {
		const lastRow = this.state.rows[this.state.rows.length - 1];
		return lastRow ? lastRow.position + lastRow.height : 0;
	}

	appendRowToWrapper(row) {
		if (row.parentElement !== this.elements.rowWrapper) {
			this.elements.rowWrapper.appendChild(row);
		}
	}

	addRowToCollection(row, position) {
		this.state.rows.push({
			html: row.outerHTML,
			position: position,
			height: row.offsetHeight,
		});
		return position + row.offsetHeight;
	}

	removeProcessedRows(rows) {
		for (const row of rows) {
			if (row.parentElement === this.elements.rowWrapper) {
				row.remove();
			}
		}
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
		this.state.scrolling = false;
		this.updateVisibleRows();
		if (this.shouldLoadMore()) {
			this.loadMoreRows();
		}
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

		if (this.state.start === start && this.state.end === end) return;

		this.renderVisibleRows(start, end);
		this.updateState(start, end);
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
		const html = this.buildHtmlString(start, end);
		this.elements.rowWrapper.innerHTML = html;

		if (this.config.processHtmx) {
			htmx.process(this.elements.rowWrapper);
		}
	}

	buildHtmlString(start, end) {
		this.updateSpacers(start, end);
		const headerHTML = this.elements.tableHeader
			? this.elements.tableHeader.outerHTML
			: "";
		const rowsHTML = this.state.rows
			.slice(start, end)
			.reduce((acc, row) => acc + row.html, "");

		let htmlString =
			headerHTML +
			this.elements.topSpacer.outerHTML +
			rowsHTML +
			this.elements.bottomSpacer.outerHTML;
		if (this.state.loading) {
			htmlString += this.elements.loader.outerHTML;
		}
		return htmlString;
	}

	updateSpacers(start, end) {
		const lastRow = this.state.rows[this.state.rows.length - 1];
		const topHeight = this.state.rows[start].position;
		const bottomHeight = this.calculateBottomSpacerHeight(lastRow, end);

		this.elements.topSpacer.style.height = `${topHeight}px`;
		this.elements.bottomSpacer.style.height = `${bottomHeight}px`;
	}

	updateBottomSpacer() {
		const lastRow = this.state.rows[this.state.rows.length - 1];
		const bottomSpacer =
			this.elements.rowWrapper.querySelector("#bottomSpacer");
		if (bottomSpacer) {
			const spacerHeight = this.calculateBottomSpacerHeight(
				lastRow,
				this.state.end,
			);
			bottomSpacer.style.height = `${spacerHeight}px`;
		}
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

	// Data Loading
	loadMoreRows() {
		this.setLoading(true);

		this.fetchNewRows()
			.then((response) => response.text())
			.then((text) => {
				const newRows = this.parseNewRows(text);

				if (newRows.length) {
					this.setLoading(false);
					this.processNewRows(newRows);
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
		return fetch(`${window.location.pathname}?${this.getQueryParams()}`, {
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
		params.append("position", this.state.rows.length.toString());
		params.append("scrolling", "true");
		return params.toString();
	}

	parseNewRows(html) {
		return new DOMParser()
			.parseFromString(`<table>${html}</table>`, "text/html")
			.querySelectorAll(this.config.rowTag);
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

	disableHtmxLoadTriggers() {
		this.elements.rowWrapper.addEventListener(
			"htmx:afterOnLoad",
			() => {
				for (const el of this.elements.rowWrapper.querySelectorAll(
					'[hx-trigger^="load"]',
				)) {
					el.setAttribute("hx-disable", "");
				}

				this.elements.tableHeader =
					this.elements.rowWrapper.querySelector("thead");
			},
			{ once: true },
		);
	}
}
