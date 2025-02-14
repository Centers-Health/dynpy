from django.views.generic import View
from django.views.generic.base import TemplateView


class DummyView(View):
    pass


class DummyErrorView(View):
    def get(self, request, *args, **kwargs):
        raise AttributeError


class DummyJSErrorView(TemplateView):
    template_name = "tests/dummy_js_error_with_erroneous.html"
