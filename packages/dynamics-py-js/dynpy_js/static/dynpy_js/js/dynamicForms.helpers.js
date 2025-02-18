export const addFormSelector = (selector, cond) => ({
	...cond,
	name: `${selector} [name=${cond.name}]`,
});

export const resolve = (cond) => {
	if (typeof cond === "boolean") return cond;
	const { name, value, operator } = cond;
	const left = document.querySelector(name).value;
	const right = value;
	return operator === "==" || typeof operator === "undefined"
		? left == right
		: left == "" || left === "" || left === undefined || left === false
			? false
			: operator === "==="
				? left === right
				: // these >/< are flipped so that the conditions make sense to user
					operator === "<"
					? Number.parseInt(left) > Number.parseInt(right)
					: operator === ">"
						? Number.parseInt(left) < Number.parseInt(right)
						: operator === "<="
							? Number.parseInt(left) >= Number.parseInt(right)
							: operator === ">="
								? Number.parseInt(left) <= Number.parseInt(right)
								: false;
};

export const showElement = (elem) => {
	elem.classList.remove("d-none");
	elem.disabled = false;
};

export const hideElement = (elem) => {
	elem.classList.add("d-none");
	elem.disabled = "disabled";
};

export const setInputValue = (input, value) => {
	if (input.nodeName.toLowerCase() === "input") {
		if (input.type === "checkbox" || input.type === "radio") {
			if (value) {
				input.checked = true;
			}
		} else {
			input.value = value;
			// everything else
		}
	} else {
		// select
		input.value = value;
	}
};
