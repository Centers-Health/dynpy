from django.conf import settings
from django.urls import path

from dynpy import views

"""
To include the custom error-handling views in production
add the following to the projects root urls.py:
handler403 = dynpy_views.permission_denied
handler404 = dynpy_views.page_not_found
handler500 = dynpy_views.server_error

To include the custom error-handling views for testing in Dev
add `path("", include("dynpy.urls"))` to the urlpatterns in urls.py
"""

urlpatterns = []

if settings.DEBUG:
    urlpatterns += [
        path("500/", views.server_error, name="500"),
        path("404/", views.page_not_found, name="404"),
        path("403/", views.permission_denied, name="403"),
    ]
