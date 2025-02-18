/****************************************************************/
/*                    Scroll Sensitive                          */
/****************************************************************/
/*
    Adds a class (`x-scrollable`, `y-scrollable`) to any element with
    a `scroll-sensitive` class, based on whether the element is currently
    scrollable.
    Useful for adding css that depends on whether the scrollbar is
    visible.

    Based on https://stackoverflow.com/a/62796638
*/
const scrollSensitiveElems = document.querySelector(".scroll-sensitive");

const isYScrollable = (elem) => {
	return elem.scrollHeight > elem.clientHeight;
};

const isXScrollable = (elem) => {
	return elem.scrollWidth > elem.clientWidth;
};

const resizeObserver = new ResizeObserver(() => {
	scrollSensitiveElems.classList.toggle(
		"y-scrollable",
		isYScrollable(scrollSensitiveElems),
	);
	scrollSensitiveElems.classList.toggle(
		"x-scrollable",
		isXScrollable(scrollSensitiveElems),
	);
});
if (scrollSensitiveElems) {
	resizeObserver.observe(scrollSensitiveElems);
}
