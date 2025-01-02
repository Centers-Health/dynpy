from datetime import date

import pytest
from django.db import transaction
from django.db.utils import IntegrityError

from dynpy.erroneous.models import Error


@pytest.mark.django_db
def test_hash_unique_constraint_raises_integrity_error_if_two_hashes_are_same():
    """
    The unique constraint causes the 2nd create to fail because they share
    the same hash. And therefore the entire block gets rolled back and
    there are 0 records in the Error table.
    """
    with pytest.raises(IntegrityError), transaction.atomic():
        Error.objects.create(info="test", when=date.today(), hash=1111)
        Error.objects.create(info="test2", when=date.today(), hash=1111)
    assert Error.objects.count() == 0


@pytest.mark.django_db
def test_can_save_2_similar_rows_if_hash_is_different():
    """
    The unique contstaint on hash, so as long as the hash is
    different, the row will be inserted.
    """
    Error.objects.create(info="test", when=date.today(), hash=1111)
    Error.objects.create(info="test", when=date.today(), hash=2222)
    assert Error.objects.count() == 2


@pytest.mark.django_db
def test_error_can_have_path_over_200_characters():
    path = "hi_there" * 500
    Error.objects.create(path=path)
    assert Error.objects.count() == 1
