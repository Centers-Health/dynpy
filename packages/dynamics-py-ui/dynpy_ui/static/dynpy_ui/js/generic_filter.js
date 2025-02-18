// on a template, use:
// data-target-selector="elements_included_in_the_filtering"
// data-match-selector="elements_to_match_the_filter_to"

const jsFilter = (targetSelector, matchSelector) => (e) => {
	const children = document.querySelectorAll(targetSelector);

	// show all
	for (const child of children) child.hidden = false;
	Array.from(children)
		.filter(
			(child) =>
				!(
					matchSelector
						? Array.from(child.querySelectorAll(matchSelector)).reduce(
								(prev, cur) => cur.innerText + prev,
								"",
							)
						: child.innerText
				)
					.toLowerCase()
					.includes(e.target.value.toLowerCase()),
		)
		.map((child) => {
			child.hidden = true;
		});
};

const startJsFilter = () => {
	// Setup Filters
	const JsFilters = document.querySelectorAll(".js-filter");
	for (const jf of JsFilters) {
		const targetSelector = jf.dataset.targetSelector;
		const matchSelector = jf.dataset.matchSelector;
		console.assert(targetSelector, "Need to define a data-target-selector");
		jf.oninput = makeDebounce(jsFilter(targetSelector, matchSelector), 200);
	}
};
