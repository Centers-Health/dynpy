from django.urls import include, path
from django.views import View

urlpatterns = [
    path("", View.as_view(), name="dashboard"),
    path("mfa/login", View.as_view(), name="mfa_login"),
]

path("/", include(urlpatterns))
