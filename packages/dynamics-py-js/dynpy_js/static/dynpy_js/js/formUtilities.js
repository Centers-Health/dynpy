const setFormsOnchangeHandlers = (elem = document) => {
	const forms = Array.from(elem.getElementsByTagName("form"));
	forms.forEach(setFormOnchangeHandlers);
};

const setFormOnchangeHandlers = (form) => {
	// currently the only onchange event is for autosubmit
	// so the onchange is after the 'if' statement
	if (form.classList.contains("js-form-autosubmit")) {
		setFormAutosubmitsOnChange(form);
	}
};

const setFormAutosubmitsOnChange = (form) => {
	form.onchange = () => {
		if (isValidSubmissionState(form)) {
			form.dispatchEvent(new Event("submit"));
		}
	};

	// If monthpicker stop onchange until click out of input
	const monthpickers = Array.from(form.getElementsByClassName("monthpicker"));

	monthpickers.forEach((monthpicker) => {
		monthpicker.onchange = (event) => {
			event.stopPropagation();
			const value = monthpicker.value;
			const min = monthpicker.min;
			const max = monthpicker.max;

			//Remove the feedback span if already there
			const invalidSpan =
				monthpicker.parentElement.querySelector(".is-invalid");
			if (invalidSpan) invalidSpan.remove();

			// Validate against min and max of the input if there is a value, min, and max
			if (!value || !min || !max || (value >= min && value <= max)) {
				form.dispatchEvent(new Event("change"));
			}

			// Set invalid feedback
			else {
				const span = document.createElement("span");
				span.innerHTML = "The selected date is out of range";
				span.classList.add(...["is-invalid", "text-danger"]);
				monthpicker.parentElement.appendChild(span);
			}
		};
	});

	// If multiselect stop onchange until click off select element
	const multiselects = Array.from(form.getElementsByClassName("selectpicker"));
	multiselects.forEach((multiselect) => {
		const liveSearch = multiselect.parentNode.querySelector(".bs-searchbox");
		if (liveSearch) {
			liveSearch.onchange = (event) => {
				event.stopPropagation();
			};
		}
		multiselect.onchange = (event) => {
			event.stopPropagation();
			$(multiselect).on("hidden.bs.select", () => {
				form.dispatchEvent(new Event("change"));
			});
		};
	});
};

const isValidSubmissionState = (form) => {
	var hasOnlyValidInputs = true;
	const formElements = Array.from(form.elements);

	const dateElements = formElements.filter(
		(element) => element.type === "date",
	);
	dateElements.forEach((dateElement) => {
		if (!isValidDate(dateElement.value)) hasOnlyValidInputs = false;
	});

	return hasOnlyValidInputs;
};

/*
    Submits the form as the user types into an input field as long as
    the input is greater than 3 characters (uses debounce  so that it
    does submit on every keystroke and only submits when the user
    finishes typing)
*/
const setupSubmitOnInputFields = () => {
	const elements = Array.from(
		document.getElementsByClassName("js-submit-on-input"),
	);
	elements.forEach((element) => {
		element.addEventListener(
			"input",
			makeDebounce(() => {
				if (element.value.length > 2) {
					element.form.dispatchEvent(new Event("submit"));
				}
			}, 500),
		);
	});
};

const setFormsSubmissionHandlers = (elem = document) => {
	const forms = Array.from(elem.getElementsByTagName("form"));
	forms.forEach(setFormSubmissionHandlers);
};

const getSubmitButtons = (form) => {
	return Array.from(form.querySelectorAll('[type="submit"]'));
};

const disableSubmitButtons = (form, event) => {
	// if we want the submit button to be sent to the back-end
	// we have to capture it before disabling
	if (event && event.submitter && event.submitter.name) {
		const input = document.createElement("input");
		input.type = "hidden";
		input.name = event.submitter.name;
		input.value = event.submitter.value;
		form.appendChild(input);
	}

	// Forms can have multiple submit buttons
	getSubmitButtons(form).forEach((button) => {
		// Do not disable if the button has a class name autosubmit-disabled
		if (!button.classList.contains("autosubmit-disabled")) {
			disable(button);
			document.body.style.cursor = "wait";
		}
	});
};

const enableSubmitButtons = (form) => {
	getSubmitButtons(form).forEach((button) => {
		enable(button);
	});
};

const setFormSubmissionHandlers = (form) => {
	/*
        1. Prevents forms from being submitting multiple times when the submit button is double clicked by
           disabling the submit button on form submit.
           Re-enables submit button on input

        2. Adds confirmation bootbox if the form has js-form-confirm class

        3. Adds async validation or confirmation if the form has js-async-[validate|confirm] classes.

        4. If you want to add a custom function to be called upon submission of a particular form, you can define that function in a way that
           it will be added to the global js window object, and then define a "callback" field in the action that uses that form. (Set the "callback" field equal to
           the string of the function name).  That function will then be called right after form submission, i.e. only if it passes validateForm(form).

           NOTE: if a function is declared in the global scope, then that function is automatically added to the global js window object.  However,
           this only applies to a function declaration, such as:
                function someFunction(){
                      // do stuff here
                }
           but not to a function expression, such as:
              const someFunction = function (){
                        // do stuff here
                    }
           However, after a function expression has been defined, you can manually attach it to the window object by doing:
                window.someFunction =  someFunction;
  */
	form.addEventListener("submit", async (e) => {
		e.preventDefault();

		// disable the submit button to prevent multiple submissions or multiple confirm boxes
		disableSubmitButtons(form, e);

		const callbackFunctionString = e.target.dataset.callback;
		const invalidCallbackFunction = e.target.dataset.invalidCallback;
		const confirmCallbackFunction = e.target.dataset.confirmCallback;

		let formIsValid = true;
		if (
			e.target.classList.contains("js-async-validate") ||
			e.target.classList.contains("js-async-confirm")
		) {
			formIsValid = await asyncFormHandler(e, form);
		}

		if (formIsValid && e.target.classList.contains("js-form-confirm")) {
			formIsValid = false; // confirmSubmission handles the submit
			if (confirmCallbackFunction) {
				window[confirmCallbackFunction](e);
			}
			confirmSubmission(
				e.target.dataset.message,
				e.target,
				e,
				callbackFunctionString,
			);
		}

		// this is only reached if classList doesn't contain 'js-form-confirm'
		if (formIsValid) {
			submitForm(e.target, e, callbackFunctionString);
		}

		if (!formIsValid && invalidCallbackFunction) {
			window[invalidCallbackFunction](e);
		}

		// if form stays on page, that means there were errors preventing
		// submission - so scroll to top of form to show errors
		const formErrors = form.querySelector(".form-errors");
		if (formErrors) {
			formErrors.scrollIntoView({ behavior: "smooth", block: "end" });
		}
	});

	["input", "change"].forEach((eventName) => {
		form.addEventListener(eventName, (e) => {
			enableSubmitButtons(e.currentTarget);
		});
	});
};

const confirmSubmission = (
	confirmation_text,
	form,
	event,
	callbackFunctionString,
) => {
	bootbox.confirm({
		message: confirmation_text || "Are you sure?",
		centerVertical: true,
		callback: (confirmed) => {
			if (confirmed) {
				submitForm(form, event, callbackFunctionString);
			} else {
				enableSubmitButtons(form);
			}
		},
	});
};

/* All submission of forms go and should go through this function
    so any functionality before submission should be done in this function */
const submitForm = (form, event, callbackFunctionString = null) => {
	//If there is a modal, close modal before submit so that if, after redirect, the user navigates back, the modal will be closed.
	$(form.closest(".modal")).modal("hide");

	if (callbackFunctionString && window[callbackFunctionString]) {
		window[callbackFunctionString]();
	}
	form.submit();
};

/* -------- POST functions that validate the form data asynchronously ------- */

const setFormValidationHandler = (form) => {
	/**
	 * Takes a form and adds a validation handler.
	 * The event is based on the data-validate-on
	 * attribute.
	 *
	 * If validateOn is 'input' debounce the validation.
	 */

	const validateOn = form.dataset.validateOn;
	if (validateOn != "submit") {
		const debounceInterval = validateOn == "input" ? 500 : 0;
		form.addEventListener(
			validateOn,
			makeDebounce((e) => {
				asyncFormHandler(e, form);
				e.target.focus();
			}, debounceInterval),
		);
	}
};
const setFormsValidationHandler = () => {
	/**
	 * On page load looks for all forms that have js-validate class
	 * and that do not have data-validate-on='submit and adds the
	 * form validation handler. Submit is handled by setFormSubmissionHandlers.
	 */
	const forms = Array.from(
		document.querySelectorAll(
			`[class*='js-async-validate'][data-validate-on]:not([data-validate-on='submit'])`,
		),
	);
	forms.forEach(setFormValidationHandler);
};

const handleConfirmation = (data, e, form) => {
	const message = data["message"];

	// Add async confirmation message
	if (message) {
		form.classList.add("js-form-confirm");
		form.setAttribute("data-message", message);
	} else if (message === "") {
		form.classList.remove("js-form-confirm");
	}
};

const handleValidation = (data, form) => {
	const formErrors = data["errors"] || {};
	// clear previous validation
	form
		.querySelectorAll(".is-invalid")
		.forEach((e) => e.classList.remove("is-invalid"));
	form
		.querySelectorAll(".invalid-feedback, .form-errors")
		.forEach((e) => e.remove());
	Object.entries(formErrors).forEach(([name, errors]) => {
		if (name === "__all__") {
			const formErrorsDiv = createFormErrors(errors);
			form.insertBefore(formErrorsDiv, form.firstElementChild);
		} else {
			let inputField = form.querySelector(`[name=${name}]`);
			if (inputField.classList.contains("selectpicker")) {
				inputField = inputField.parentElement;
			}
			inputField.classList.add("is-invalid");
			errors.forEach((error) => {
				const feedback = createInvalidFeedback(error.message);
				inputField.after(feedback);
			});
		}
	});
	const invalidElem = form.querySelector(".is-invalid");
	if (invalidElem) {
		const getfirstInvalidElement = () => {
			return invalidElem.classList.contains("bootstrap-select")
				? invalidElem.querySelector("select")
				: invalidElem;
		};
		// Focus on - and scroll to - first invalid element, but
		// only if there aren't general form errors (in which case
		// the user is already directed to the top of the form so
		//they can see all errors listed):
		if (!document.querySelector(".form-errors")) {
			const firstInvalidElement = getfirstInvalidElement();
			firstInvalidElement.focus();
		}
	}
	document.body.style.cursor = "";
	return data["success"];
};

const asyncFormHandler = async (e, form) => {
	let isValid;

	const formData = new FormData(form);

	if (form.classList.contains("js-async-validate")) {
		formData.append("validate", "true");
	}
	if (form.classList.contains("js-async-confirm") && e.type === "submit") {
		formData.append("confirm", "true");
	}

	// Hit post endpoint and do validation/ async confirmation message.
	await fetch(form.action, {
		method: form.method,
		body: formData,
	})
		.then((response) => {
			if (!response.ok) throw new Error();
			return response.json();
		})
		.then((data) => {
			isValid = handleValidation(data, form);
			handleConfirmation(data, e, form);
		})
		.catch((err) => {
			console.error(err);
			const customErrorMessage =
				"Sorry there was an error processing the form.";
			form.innerHTML = getLoadingErrorInstance(customErrorMessage);
			isValid = false;
		});

	return isValid;
};

const createInvalidFeedback = (feedback) => {
	const feedbackSpan = document.createElement("span");
	feedbackSpan.classList.add("invalid-feedback");
	const feedbackText = document.createElement("strong");
	feedbackText.textContent = feedback;
	feedbackSpan.appendChild(feedbackText);
	return feedbackSpan;
};

const createFormErrors = (errors) => {
	const errorsDiv = document.createElement("div");
	errorsDiv.classList.add(
		"alert",
		"alert-block",
		"alert-danger",
		"form-errors",
	);
	const errorsList = document.createElement("ul");
	errorsList.classList.add("m-0");
	errors.forEach((error) => {
		const errorItem = document.createElement("li");
		errorItem.innerHTML = error.message;
		errorsList.appendChild(errorItem);
	});
	errorsDiv.appendChild(errorsList);
	return errorsDiv;
};
