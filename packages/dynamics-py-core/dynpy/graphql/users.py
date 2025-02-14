from django.contrib.auth import get_user_model

INTERNAL_API_USER_USERNAME = "internal_api_user"


def get_internal_api_user():
    """
    Superuser for internal, behind the scenes api usage.
    Relies on a user existing with the username "internal_api_user" (or "docker" for dev).
    If it fails, try creating one.
    """
    User = get_user_model()
    try:
        return User.objects.get(username=INTERNAL_API_USER_USERNAME)
    except User.DoesNotExist:
        return User.objects.get(username="docker")
