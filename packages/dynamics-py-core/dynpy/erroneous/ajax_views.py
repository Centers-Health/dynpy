import json

from django.core import serializers
from django.http import JsonResponse
from django.template.loader import get_template
from django.views.generic import View

from dynpy.erroneous.utils import log_erroneous_error


class JSErrorView(View):
    def post(self, request):
        body = json.loads(request.body)
        user = request.user.get_username()
        user_agent = request.headers.get("User-Agent")
        message = body["message"]
        stacktrace = body["stacktrace"]
        window_location_href = body["window_location_href"]
        device_width = body["device_width"]
        device_height = body["device_height"]

        html = get_template("dyn-erroneous/includes/js_error.html").render(
            {
                "stacktrace": stacktrace,
                "message": message,
                "user_agent": user_agent,
                "window_location_href": window_location_href,
                "device_width": device_width,
                "device_height": device_height,
                "user": user,
            }
        )

        err = log_erroneous_error(
            kind="JS_Error",
            path=body["source"],
            info=message,
            data=stacktrace,
            html=html,
        )

        if err:
            err = serializers.serialize("json", [err])

        return JsonResponse({"instance": err}, status=200)
