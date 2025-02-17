from django.contrib.auth import get_user_model

User = get_user_model()


class UserInfoSyncer:
    """
    Class for syncing user information sent over from the CAS server to the user record
    on the client side

    Usage:
        UserInfoSyncer(user, **attrs).sync()
    """

    def __init__(self, user: User, **attrs) -> None:
        self.user = user
        self.attrs = attrs

    def sync(self):
        # .update() does not send signals because it's meant for bulk updates
        User.objects.filter(pk=self.user.pk).update(**self.attrs)
