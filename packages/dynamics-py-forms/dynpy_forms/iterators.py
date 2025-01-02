from itertools import groupby

from django.forms.models import ModelChoiceIterator


class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset.all()
        sorted_queryset = self.field.sort_queryset(queryset)
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, choices in groupby(sorted_queryset, key=self.field.get_group):
            if self.field.get_group_label(group):
                yield (self.field.get_group_label(group), [self.choice(ch) for ch in choices])
