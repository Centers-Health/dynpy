from django.urls import reverse
from dynpy.utils.urls import reverseplus


def test_appends_query_params():
    url = reverseplus("admin:login", params={"search": "abc"})

    assert url == f"{reverse('admin:login')}?search=abc"
