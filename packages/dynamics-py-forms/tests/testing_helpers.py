def get_formset_data(formset, data: list[dict]) -> dict:
    """
    Takes a list of data dicts and appends the correct prefix to each key.
    Return a dictionary of formset data to be passed to a formset's data argument
    including the management form data.
    """
    management_form_data = {
        formset.add_prefix("TOTAL_FORMS"): len(data),
        formset.add_prefix("INITIAL_FORMS"): len(formset.get_queryset()),
        formset.add_prefix("MIN_NUM_FORMS"): formset.min_num,
        formset.add_prefix("MAX_NUM_FORMS"): formset.max_num,
    }
    form_data = {}
    for i, form_data_dict in enumerate(data):
        for key, value in form_data_dict.items():
            form_data[formset.add_prefix(f"{i}-{key}")] = value
    return {**management_form_data, **form_data}
