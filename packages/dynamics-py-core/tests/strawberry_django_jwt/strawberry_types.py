import strawberry_django
from strawberry import auto

from tests.strawberry_django_jwt import models


@strawberry_django.type(models.MyTestModel)
class MyTestModel:
    test: auto
