import GroupSelect from "./GroupSelect.js";

export default class GroupAwareSelect extends GroupSelect {
	constructor($select) {
		super($select);
		this.groupKey = $select.data("group-key") || "_group_";
		this._tmp = [];

		// 1) After selectpicker builds its data/menu: prime visual state from hidden inputs
		this.$select.on("loaded.bs.select", () => {
			this._primeFromHidden();
		});

		// 2) Each time the menu opens, make checkboxes reflect hidden groups
		this.$select.on("show.bs.select", () => {
			this._applyTempVisualForCheckboxes();
			this._render();
		});

		// 3) On close, convert full groups to hidden inputs & revert temporary option selections
		this.$select.on("hide.bs.select", () => {
			this.injectGroupInputs();
			this._revertTempVisual();
		});
	}

	get data() {
		return this.picker?.selectpicker?.main?.data || [];
	}

	// ---------- PAGE-LOAD / CLOSED MENU STATE ----------

	_primeFromHidden() {
		const data = this.data;
		if (!data.length) return;

		const labels = this._hiddenGroupLabels();
		if (!labels.size) return;

		const optLabelById = this._optgroupLabelsById(data);
		const touched = [];

		for (const el of data) {
			if (el.type === "option") {
				const label = optLabelById[el.optID];
				if (labels.has(label)) {
					el.selected = true;
					if (!el.option.selected) {
						el.option.selected = true;
						touched.push(el);
					}
				}
			}
		}

		this._render();

		for (const el of touched) {
			el.option.selected = false;
		}
	}

	// ---------- MENU STATE ----------

	_applyTempVisualForCheckboxes() {
		const data = this.data;
		if (!data.length) return;

		const labels = this._hiddenGroupLabels();
		if (!labels.size) return;

		const optLabelById = this._optgroupLabelsById(data);
		this._tmp.length = 0;

		for (const el of data) {
			if (el.type === "option") {
				const label = optLabelById[el.optID];
				if (labels.has(label) && !el.option.selected) {
					el.option.selected = true;
					this._tmp.push(el);
				}
			}
		}
	}

	_revertTempVisual() {
		if (!this._tmp.length) return;
		for (const el of this._tmp) {
			// Revert temporary changes unless the user manually selected it.
			if (!el.selected) {
				el.option.selected = false;
			}
		}
		this._tmp.length = 0;
	}

	// ---------- SUBMISSION CONVERSION ----------

	injectGroupInputs() {
		const picker = this.picker;
		const data = this.data;
		if (!picker || !data.length) return;

		const $form = this.$select.closest("form");

		const prevHidden = new Set();
		const selector = `input.group-injected[name="${this.groupKey}"]`;
		$form.find(selector).each((_, input) => {
			const v = $(input).val();
			if (v != null && v !== "") prevHidden.add(String(v));
		});

		$form.find(selector).remove();

		const groups = {};
		for (const el of data) {
			if (el.type === "optgroup-label") {
				groups[el.optID] = { label: el.display, items: [] };
			} else if (el.type === "option") {
				if (!groups[el.optID]) groups[el.optID] = { label: null, items: [] };
				groups[el.optID].items.push(el);
			}
		}

		for (const group of Object.values(groups)) {
			if (!group.label || group.items.length === 0) continue;

			const allSelectedByOption = group.items.every(
				(el) => el.selected === true,
			);

			if (allSelectedByOption) {
				$("<input>", {
					type: "hidden",
					class: "group-injected",
					name: this.groupKey,
					value: group.label,
				}).appendTo($form);

				for (const el of group.items) {
					el.option.selected = false;
				}
			} else if (prevHidden.has(group.label)) {
				for (const el of group.items) {
					if (el.selected) {
						el.option.selected = true;
					}
				}
			}
		}
	}

	// ---------- HELPERS ----------

	_hiddenGroupLabels() {
		const $form = this.$select.closest("form");
		const labels = new Set();
		const selector = `input.group-injected[name="${this.groupKey}"]`;
		$form.find(selector).each((_, input) => {
			const v = $(input).val();
			if (v != null && v !== "") labels.add(String(v).trim());
		});
		return labels;
	}

	_optgroupLabelsById(data) {
		const map = {};
		for (const el of data) {
			if (el.type === "optgroup-label") map[el.optID] = el.display;
		}
		return map;
	}

	_render() {
		const picker = this.picker;
		if (!picker) return;
		picker.setOptionStatus();
		picker.render(false);
	}
}
