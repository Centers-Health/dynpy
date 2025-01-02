import os

from django.conf import settings as django_settings


# Warning: All values are treated as literals therefore booleans will be treated as string literals
def env(request=None):
    return dict(os.environ)


def settings(request):
    return {"settings": django_settings}
