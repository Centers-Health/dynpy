from django.urls import re_path
from django_cas_ng import views as cas_ng_views

"""
Urls for connecting a django project to the CAS
Add the following urls before "accounts/" to override the builtin auth urls
```
from dynpy_cas.urls import cas_urls

urlpatterns = [
    ...
    *cas_urls,
    path("accounts/", include("django.contrib.auth.urls")),
    ...
]
```
"""
cas_urls = [
    re_path("^accounts/login", cas_ng_views.LoginView.as_view(), name="cas_ng_login"),
    re_path("^accounts/logout", cas_ng_views.LogoutView.as_view(), name="cas_ng_logout"),
    # Used for posting logout requests from CAS
    re_path("^accounts/callback", cas_ng_views.CallbackView.as_view(), name="cas_ng_callback"),
]
