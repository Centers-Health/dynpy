(() => {
	// NOTE: starts from 1 since we are using css nth-child selectors
	const getNthOffsetLeft = (n) =>
		document.querySelector(`.gfl-frozen th:nth-child(${n})`).offsetLeft;
	// NOTE: starts from 1 since we are using css nth-child selectors
	const getNthOffsetWidth = (n) =>
		document.querySelector(`.gfl-frozen th:nth-child(${n})`).offsetWidth;
	const getCompleteOffset = (n) => {
		if (n === 1) return 0;
		let sum = 0;
		for (let i = 1, len = n; i < len; i++) {
			const off = getNthOffsetWidth(i);
			sum += off;
		}
		return sum;
	};

	const setFrozenColumnsOffset = (numberOfFrozenColumns = 0) => {
		const root = document.documentElement;
		if (numberOfFrozenColumns > 0) {
			const offsets = [];
			for (let i = numberOfFrozenColumns; i > 0; i--) {
				offsets[i] = getCompleteOffset(i);
			}
			for (const [i, offset] of offsets.entries()) {
				root.style.setProperty(`--col-${i}-offset`, `${offset}px`);
			}
		}
	};
	// NOTE: this is needed to wait until all css is finished rendering. Otherwise there is a race condition and the offsets are not reliably calculated.
	document.onreadystatechange = () => {
		if (document.readyState !== "complete") {
		} else {
			setFrozenColumnsOffset(frozenColumnsOffset);
		}
	};

	// Recalculate offsets when table is resized
	const gfl_table = document.getElementById("gfl_table_wrapper");
	if (gfl_table) {
		new ResizeObserver(() =>
			setFrozenColumnsOffset(frozenColumnsOffset),
		).observe(gfl_table);
	}
})();
