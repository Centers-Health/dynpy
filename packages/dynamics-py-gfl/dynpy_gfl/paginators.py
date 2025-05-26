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

    @cached_property
    def count(self):
        """
        Returns the total number of items in the object_list.
        This is useful for determining if there are more items available
        beyond the current combo page.
        """
        return self.object_list.count()


class ComboPaginator(InfiniteScrollPaginator):
    """
    Paginator for infinite scroll that allows for combo pages.
    For example, if you have a list of 1000 items and you want
    to let the users load 100 items before going to the next page
    but to load 100 on page load would be too slow, you can use this paginator
    to use infinite scroll up to 100 items, and then load the next 100 items
    when the user clicks the "Next" button.

    **Warning**: This paginator cannot be used with pages that allow
                 removing/adding items to the list, as it relies on the position
                 of the items in the list to determine which items to show.
    """

    def __init__(self, object_list, per_page, position, per_combo_page, combo_page):
        super().__init__(object_list, per_page, position)
        self.per_combo_page = per_combo_page
        self.combo_page = max(combo_page, 1)  # Ensure combo_page starts at 1

        # Validate logical relationship
        if self.per_page > self.per_combo_page:
            raise ValueError("per_page cannot be greater than per_combo_page")

    @cached_property
    def paginated_object_list(self):
        # Calculate the starting point based on the combo_page
        bottom = (self.combo_page - 1) * self.per_combo_page + self.position

        # Calculate the top and ensure does not go past the end of the combo page
        top = min(bottom + self.per_page, self.combo_page * self.per_combo_page)

        qs = self.object_list[bottom:top]
        return qs

    @cached_property
    def has_next(self):
        # This checks if there are more items to load within the current page's range
        return (
            len(self.paginated_object_list) == self.per_page
            and self.position + self.per_page < self.per_combo_page
        )

    @property
    def has_next_combo_page(self):
        """
        Returns True if there are more combo pages available.
        """
        return self.combo_page * self.per_combo_page < self.count

    @cached_property
    def showing_start(self):
        """
        Returns the start of the paginator for the current combo page.
        """
        if self.combo_page == 1:
            return 1
        # Calculate the start based on the combo_page and per_combo_page
        start = (self.combo_page - 1) * self.per_combo_page + 1
        return start

    @cached_property
    def showing_end(self):
        """
        Returns the end of the paginator.
        I.e on the 3rd page of 10, would return 30. But, if the list only
        contained 25 items, it would return 25.
        """
        if self.combo_page == 1:
            return min(self.per_combo_page, self.count)
        # Calculate the end based on the combo_page and per_combo_page
        end = self.combo_page * self.per_combo_page
        if end > self.count:
            return self.count
        return end
