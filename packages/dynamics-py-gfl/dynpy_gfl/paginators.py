from django.utils.functional import cached_property


class InfiniteScrollPaginator:
    """
    Does not inherit from Django's Paginator because this paginator is not
    working with "Pages", and therefore changes alot of the behavior.
    """

    def __init__(self, object_list, per_page, position=0):
        self.object_list = object_list
        self.per_page = int(per_page)
        self.position = position

    @cached_property
    def paginated_object_list(self):
        bottom = self.position
        top = bottom + self.per_page
        return self.object_list[bottom:top]

    @cached_property
    def has_next(self):
        """
        To avoid an additional query, has_next is set to true when per_page equals the
        length of paginated_object_list. When the length of object_list is divisible by
        per_page, the "last page" will have a length of 0. This results in one extra
        pagination request that returns nothing, which is preferable to having an extra query
        for every request.
        """
        return len(self.paginated_object_list) == self.per_page

    def is_paginated(self):
        """
        Always returns True because evaluating whether the queryset is paginated is costly,
        and with infinite scroll, this check typically isn't needed.

        If determining whether the queryset is paginated is necessary, you can check
        if has_next is True. Note that doing so will evaluate the queryset.
        """
        return True

    def page(self):
        """
        Returns None because this paginator doesn't work with pages.
        """

        return None
