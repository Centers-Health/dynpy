from django.conf import settings
from django.http import HttpResponse


class HealthCheckMiddleware:
    """
    Returns 'OK' for requests to the health check path (default: /up/).

    Override the path with settings.HEALTH_CHECK_PATH.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.health_check_path = getattr(settings, "HEALTH_CHECK_PATH", "/up/")

    def __call__(self, request):
        is_health_check_request = request.path == self.health_check_path
        return HttpResponse("OK") if is_health_check_request else self.get_response(request)
