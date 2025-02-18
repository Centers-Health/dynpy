from dynpy_forms.iterators import GroupedModelChoiceIterator


class GroupedChoicesMixin:
    iterator = GroupedModelChoiceIterator

    def __init__(self, queryset, group_by_field=None, group_label=None, *args, **kwargs):
        """
        ``group_by_field`` is the name of a field on the model to use as an optgroup.
        ``group_label`` is a function to return a label for each optgroup.
        """
        super().__init__(queryset, *args, **kwargs)
        self.group_by_field = group_by_field
        self.group_label = group_label or (lambda group: group)

    def sort_queryset(self, queryset):
        if self.group_by_field:
            if queryset.ordered:
                # If the queryset is ordered, we can assume
                # it's ordered by the group_by_field first
                return queryset
            return queryset.order_by(self.group_by_field)
        return sorted(queryset, key=self.get_group)

    def get_group(self, obj):
        if self.group_by_field is None:
            raise ValueError("group_by_field must be set or get_group must be overridden")
        value = getattr(obj, self.group_by_field)
        return value if value is not None else ""

    def get_group_label(self, group):
        return self.group_label(group)

    def _get_choices(self):
        if hasattr(self, "_choices"):
            return self._choices
        return self.iterator(self)
