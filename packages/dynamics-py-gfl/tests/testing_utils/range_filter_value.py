from collections import namedtuple


class RangeFilterValue(namedtuple("RangeFilterValue", ["start", "stop"])):
    """
    Used to pass a value to a range filter in tests

    Example:
        f = AllValuesRangeFilter(...)
        qs = Resident.objects.all()
        results = f.filter(qs, RangeFilterValue(start=min_value, stop=max_value))
    """
