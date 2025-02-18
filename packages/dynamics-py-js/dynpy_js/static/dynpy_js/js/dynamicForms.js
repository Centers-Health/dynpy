import {
	addFormSelector,
	hideElement,
	resolve,
	setInputValue,
	showElement,
} from "./dynamicForms.helpers.js";

const setupDynamicForm = (selector, fields) => {
	// Get form
	const form =
		typeof selector === "string" ? document.querySelector(selector) : selector;

	// Add event listener
	form.addEventListener("change", () => {
		form.querySelectorAll("input, select").forEach((input) => {
			// console.log(`checking ${input.name}`);
			const rulesForInput = fields.find((field) => field.name == input.name);
			if (rulesForInput) {
				// Is a managed field
				const isTriggered = Array.isArray(rulesForInput.triggers)
					? rulesForInput.triggers
							.map((cond) => resolve(addFormSelector(selector, cond)))
							.reduce((cur, prev) => cur && prev, true)
					: resolve(addFormSelector(selector, rulesForInput.triggers));

				const { value, show, reset } = rulesForInput.render;
				if (isTriggered) {
					if (value) setInputValue(input, reset ? "" : value);
					if (show) showElement(input);
				} else {
					if (show) hideElement(input);
				}
			} else {
				showElement(input);
			}
		});
	});

	// Trigger initial change
	form.dispatchEvent(new Event("change"));
};

export default setupDynamicForm;
