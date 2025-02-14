from django.contrib import admin
from django.urls import include, path

from tests.views import DummyErrorView, DummyJSErrorView, DummyView

urlpatterns = [
    path("", DummyView.as_view()),
    path("admin/", admin.site.urls),
    path("dummy-error/", DummyErrorView.as_view(), name="dummy_error"),
    path("dummy-js-error/", DummyJSErrorView.as_view(), name="dummy_js_error"),
    path("dyn-ajax/erroneous/", include("dynpy.erroneous.ajax_urls")),
    path("strawberry-django-jwt/", include("tests.strawberry_django_jwt.urls")),
]
