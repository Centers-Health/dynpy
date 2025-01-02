from django.dispatch import receiver
from django_cas_ng.signals import cas_user_authenticated

from dynpy_cas.user_info_syncer import UserInfoSyncer


@receiver(cas_user_authenticated)
def sync_user_to_client(sender, **kwargs):
    """
    Receiver for syncing user data from the cas to the client db
    """

    is_superuser = kwargs.get("attributes").get("is_superuser")
    is_staff = kwargs.get("attributes").get("is_staff")
    email = kwargs.get("attributes").get("email")
    user = kwargs.get("user")

    UserInfoSyncer(user, is_superuser=is_superuser, is_staff=is_staff, email=email).sync()
