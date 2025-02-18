/*
 Usage:
 Add the 'copyable' css class to an element to copy the inner text.
 To copy anything other than the element's inner text,
 use the 'data-copy-attr' to specify the HTML attribute you want to use for copying.
 Using the 'href' attribute for links will use the absolute url automatically.
*/

const initializeCopyElements = () => {
	const getAbsoluteUrl = (link) => {
		if (link.href.startsWith("http")) return link.href;
		return `${link.protocol}//${link.host}${link.href}`;
	};
	document.querySelectorAll(".copyable").forEach((elem) => {
		// copy inner text by default
		// if data-copy-attr is set use it instead
		let copyText = elem.getAttribute(elem.dataset.copyAttr) || elem.innerText;
		const tooltipText = "Copy";

		// copy absolute links
		if (elem.dataset.copyAttr == "href") {
			copyText = getAbsoluteUrl(elem);
			tooltipText == "Copy Link";
		}

		// trim whitespace
		copyText = copyText.trim();

		// append copy icon with tooltip to be shown on hover
		const copyIcon = document.createElement("i");

		copyIcon.className = "far fa-copy copy-btn pr-2 py-1";

		copyIcon.title = tooltipText;
		copyIcon.dataset.placement = "top";
		copyIcon.dataset.toggle = "tooltip";
		elem.appendChild(copyIcon);
		$(copyIcon).tooltip();

		elem.addEventListener("click", (e) => {
			e.preventDefault();
			// copy to clipboard
			navigator.clipboard.writeText(copyText);

			// change icon and tooltip after copied
			$(copyIcon).tooltip("dispose");
			copyIcon.className = "fa fa-check-circle text-success copy-btn pr-2 py-1";
			copyIcon.title = "Copied!";
			$(copyIcon).tooltip("show");

			// reset copy icon
			elem.addEventListener(
				"mouseleave",
				(e) => {
					// wait for css transition (0.2s)
					setTimeout(() => {
						copyIcon.className = "far fa-copy copy-btn pr-2 py-1";
						$(copyIcon).tooltip("dispose");
						copyIcon.title = tooltipText;
						$(copyIcon).tooltip();
					}, 200);
				},
				{ once: true },
			);
		});
	});
};
initializeCopyElements();
