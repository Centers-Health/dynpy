const isValidDate = (dateValue) => {
	if (dateValue === "") return true; // allow empty date elements

	const year = Number.parseInt(dateValue.split("-")[0]);
	const month = Number.parseInt(dateValue.split("-")[1]);
	const day = Number.parseInt(dateValue.split("-")[2]);

	return isValidYear(year) && isValidMonth(month) && isValidDay(day);
};

const isValidDay = (day) => {
	return day >= 1 && day <= 31;
};

const isValidMonth = (month) => {
	return month >= 1 && month <= 12;
};

const isValidYear = (year) => {
	return year >= 1000 && year <= 9999;
};

const loadAjaxTemplate = (elem) => {
	/*
        Handles ajax data loading.

        Can be used independently for loading ajax data on specific
        events by using it inside an event handler and passing it
        the element to be manipulated.

        Make sure to add { once: true } to the event handler so
        it only loads the first time the event is triggered.

        Accepts the following data attributes on the element:
        1. data-loader-style for loader type (default is 'spinner')
        2. data-loading-message for message while loading (optional)
        3. data-ajax-url for ajax request url (required)
        4. data-success-callback is called on successful fetch. (must use function declaration)
           If there is no function specified it will replace the element
           with the response data
        5. data-error-callback function that is called if request fails. (must use function declaration)
        6. data-error-message for message to be displayed if request fails
    */

	const loaderStyle = elem.dataset.loaderStyle || "spinner";
	const customLoadingMessage = elem.dataset.loadingMessage
		? elem.dataset.loadingMessage
		: null;
	elem.innerHTML = getLoaderInstance(loaderStyle, customLoadingMessage);
	const url = elem.dataset.ajaxUrl;
	fetch(url)
		.then((response) => {
			if (!response.ok) throw new Error();
			return response.text();
		})
		.then((data) => {
			const successCallback = elem.dataset.successCallback;
			if (
				successCallback !== undefined &&
				typeof window[successCallback] === "function"
			) {
				//if set success callback will use that on success
				window[successCallback](data);
			} else {
				elem.outerHTML = data;
			}
		})
		.catch(() => {
			const errorCallback = elem.dataset.errorCallback;
			if (
				errorCallback !== undefined &&
				typeof window[errorCallback] === "function"
			) {
				//if set error callback will use that on error
				window[errorCallback]();
			} else {
				const customErrorMessage = elem.dataset.errorMessage
					? elem.dataset.errorMessage
					: null;
				elem.innerHTML = getLoadingErrorInstance(customErrorMessage);
			}
		});
};

const loadAjaxTemplates = () => {
	const templateLoaders = Array.from(
		document.getElementsByClassName("js-ajax-template-load"),
	);
	for (const templateLoader of templateLoaders) {
		loadAjaxTemplate(templateLoader);
	}
};

const snakeToCamel = (str) =>
	str.replace(/([-_][a-z])/g, (group) => group.toUpperCase().replace("_", ""));

const makeDebounce = (fn, delay) => {
	let timeout;
	return (...args) => {
		clearTimeout(timeout);
		timeout = setTimeout(() => fn(...args), delay);
	};
};

const fetchModalContent = (modalBtn, params = {}) => {
	const data = modalBtn.dataset;
	const url = `${data.ajaxUrl}?${$.param(params)}`;
	fetch(url)
		.then((response) => response.text())
		.then((response) => {
			const modalId = data.target;
			document.querySelector(`${modalId} .modal-body`).innerHTML = response;
			document.querySelector(`${modalId} .modal-title`).innerHTML =
				data.modalTitle;
		});
};

const enable = (elem) => {
	elem.disabled = false;
};

const disable = (elem) => {
	elem.disabled = true;
};

const toTitleCase = (str) => {
	return str.replace(
		/\w\S*/g,
		(txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase(),
	);
};
