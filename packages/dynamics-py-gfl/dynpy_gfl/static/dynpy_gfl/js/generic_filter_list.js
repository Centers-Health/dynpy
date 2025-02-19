const url = new URL(window.location);
const nonFilterParams = ["filters_collapsed", "show_extra_filters"];

const FilterManager = (() => {
	const filterToggleBtn = document.getElementById("filtersToggle");
	const resetFiltersBtn = document.getElementById("resetFilters");
	const filterToggleIcon = document.querySelector("#filtersToggle i");
	const extraFiltersToggleBtn = document.getElementById("extraFiltersToggle");
	const extraFiltersInput = document.getElementById("showExtraFilters");
	const firstPageBtn = document.getElementById("firstPage");
	const lastPageBtn = document.getElementById("lastPage");
	const nextPageBtn = document.getElementById("nextPage");
	const previousPageBtn = document.getElementById("previousPage");
	const pageNavButtons = [
		firstPageBtn,
		lastPageBtn,
		nextPageBtn,
		previousPageBtn,
	];

	const setFiltersCollapsed = () => {
		filterToggleIcon.classList.add("fa-expand-alt");
		filterToggleIcon.classList.remove("fa-compress-alt");
		filterToggleBtn.lastChild.textContent = " Expand";
		url.searchParams.set("filters_collapsed", "true");
		url.search = url.searchParams;
		history.replaceState({}, "", url);
	};

	const setFiltersExpanded = () => {
		filterToggleIcon.classList.remove("fa-expand-alt");
		filterToggleIcon.classList.add("fa-compress-alt");
		filterToggleBtn.lastChild.textContent = " Collapse";
		url.searchParams.delete("filters_collapsed");
		url.search = url.searchParams;
		history.replaceState({}, "", url);
	};

	const showExtraFilters = () => {
		extraFiltersToggleBtn.textContent = "Less Filters";
		url.searchParams.set("show_extra_filters", "true");
		url.search = url.searchParams;
		history.replaceState({}, "", url);
		extraFiltersInput.setAttribute("value", "true");
	};

	const hideExtraFilters = () => {
		extraFiltersToggleBtn.textContent = "More Filters";
		url.searchParams.delete("show_extra_filters");
		url.search = url.searchParams;
		history.replaceState({}, "", url);
		extraFiltersInput.setAttribute("value", "false");
	};

	const clearFilters = (e) => {
		e.preventDefault();
		const searchParams = new URLSearchParams(location.search);
		for (const key of searchParams.keys()) {
			if (!nonFilterParams.includes(key)) url.searchParams.delete(key);
		}
		location.search = url.searchParams;
	};

	const addQueryParamsToButton = (btn) => {
		btn.addEventListener("click", () => {
			const urlParams = new URLSearchParams(window.location.search);
			urlParams.set("page", new URLSearchParams(btn.search).get("page"));
			btn.search = urlParams.toString();
		});
	};

	// Attach the click event listener to the pageNavButtons
	for (const btn of pageNavButtons) {
		if (btn) {
			addQueryParamsToButton(btn);
		}
	}

	if (resetFiltersBtn !== null) {
		resetFiltersBtn.onclick = clearFilters;
	}

	if (url.searchParams.has("filters_collapsed")) {
		setFiltersCollapsed();
	}

	$("#filters").on("show.bs.collapse", function (e) {
		if ($(this).is(e.target)) setFiltersExpanded();
	});

	$("#filters").on("hide.bs.collapse", function (e) {
		if ($(this).is(e.target)) setFiltersCollapsed();
	});

	if (url.searchParams.get("show_extra_filters") === "true") {
		showExtraFilters();
	}

	$("#extraFilters").on("show.bs.collapse", function (e) {
		if ($(this).is(e.target)) showExtraFilters();
	});

	$("#extraFilters").on("hide.bs.collapse", function (e) {
		if ($(this).is(e.target)) hideExtraFilters();
	});
})();
