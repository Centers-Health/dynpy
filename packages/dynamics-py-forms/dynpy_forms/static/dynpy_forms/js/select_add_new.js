window.bootstrapSelectAddNew = (noResultsElem) => {
  const searchBoxValue = noResultsElem
    .closest("div.dropdown-menu")
    .querySelector("div.bs-searchbox > input[type=search]").value;
  const $selectPicker = $(
    noResultsElem.closest(".bootstrap-select").querySelector("select")
  );

  $selectPicker.append(
    `<option value="${searchBoxValue}" selected="">${searchBoxValue}</option>`
  );
  $selectPicker.selectpicker("refresh");
};
