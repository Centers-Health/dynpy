from django.urls import path

from dynpy.erroneous.ajax_views import JSErrorView

urlpatterns = [
    path(
        "js-error/create/",
        JSErrorView.as_view(),
        name="log_js_error",
    ),
]
