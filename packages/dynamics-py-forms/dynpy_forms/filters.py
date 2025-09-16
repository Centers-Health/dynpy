from django_filters import ModelMultipleChoiceFilter
from dynpy.utils.objects import get_attribute

from dynpy_forms.fields import GroupAwareModelMultipleChoiceField


class GroupAwareModelMultipleChoiceFilter(ModelMultipleChoiceFilter):
    """
    A ModelMultipleChoiceFilter that filters choices based on both individual and group selection.

    """

    field_class = GroupAwareModelMultipleChoiceField

    def __init__(self, group_by_field, *args, **kwargs):
        kwargs.setdefault("group_by_field", group_by_field)

        super().__init__(*args, **kwargs)

    @property
    def field(self):
        request = get_attribute(self, "parent", "request")
        self.extra.setdefault("request", request)
        self.extra.setdefault("filter_name", self.filter_name)
        return super().field
