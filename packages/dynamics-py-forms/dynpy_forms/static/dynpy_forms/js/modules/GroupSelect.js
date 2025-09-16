export default class GroupSelect {
	constructor($select) {
		this.$select = $select;
		this.init();
	}
	init() {
		if (this.$select.data("selectpicker")) return;

		this.$select.selectpicker();
		//
		// After menu is ready, override group clicks
		this.$select.on("loaded.bs.select", () => {
			setTimeout(() => this.overrideGroupClick(), 0);
		});
	}
	get picker() {
		return this.$select.data("selectpicker");
	}
	overrideGroupClick() {
		const picker = this.picker;
		if (!picker || !picker.$menu) return;

		const inner = picker.$menu.children(".inner");
		if (!inner.length) return;

		inner.off("click", ".divider, .dropdown-header");
		inner.on("click", ".divider, .dropdown-header", function (e) {
			e.preventDefault();
			e.stopPropagation();

			if (picker.options.liveSearch) picker.$searchbox.trigger("focus");
			else picker.$button.trigger("focus");

			const position0 = picker.isVirtual
				? picker.selectpicker.view.position0
				: 0;

			const clickedData =
				picker.selectpicker.current.data[$(this).index() + position0];
			if (!clickedData) return;

			let selected = null;
			const data = picker.selectpicker.current.data;
			for (const element of data) {
				if (element.type === "option" && element.optID === clickedData.optID) {
					if (selected === null) selected = !element.selected;
					element.option.selected = selected;
					element.selected = selected; // sync internal state
				}
			}

			picker.setOptionStatus();
			picker.$element.triggerNative("change");
		});
	}
}
