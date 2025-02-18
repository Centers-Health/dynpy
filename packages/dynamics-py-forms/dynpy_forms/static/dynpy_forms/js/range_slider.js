$(() => {
	$(".range-slider").each(function () {
		const $this = $(this);
		const $parent = $this.parent();

		let numberFormatter;
		const numberFormat = $parent.attr("number_format");
		if (numberFormat === "Dollars Only") {
			// Formatter to optionally convert numbers to dollars
			numberFormatter = new Intl.NumberFormat("en-US", {
				style: "currency",
				currency: "USD",
				maximumFractionDigits: 0,
			});
		}

		const setCurrentValues = (min, max) => {
			// Set slider hidden input values
			$(`#${$parent.attr("id")}_min`).val(min);
			$(`#${$parent.attr("id")}_max`).val(max);

			// Set value label
			let text = `${min} - ${max}`;
			if (numberFormatter) {
				text = `${numberFormatter.format(min)} - ${numberFormatter.format(
					max,
				)}`;
			}
			$(`#${$parent.attr("id")}-value_label`).text(text);
		};

		const range_min = Number.parseFloat($parent.attr("data_range_min"));
		const range_max = Number.parseFloat($parent.attr("data_range_max"));
		const cur_min = Number.parseFloat($parent.attr("data_cur_min"));
		const cur_max = Number.parseFloat($parent.attr("data_cur_max"));
		const step = Number.parseFloat($parent.attr("step"));

		$this.slider({
			range: true,
			min: range_min,
			max: range_max,
			step: step,
			values: [cur_min, cur_max],
			stop: () => $this.trigger("change"),
			slide: (_, ui) => {
				const min = ui.values[0];
				const max = ui.values[1];
				setCurrentValues(min, max);
			},
		});
		setCurrentValues(cur_min, cur_max);
	});
});
