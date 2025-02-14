import sys
import traceback

from django.core.signals import got_request_exception
from django.dispatch.dispatcher import receiver
from django.views.debug import ExceptionReporter

from dynpy.erroneous.utils import localize_css, log_erroneous_error


@receiver(got_request_exception)
def create_from_exception(sender, request=None, *args, **kwargs):
    """
    Handles the exception upon receiving the signal.
    """
    kind, info, data = sys.exc_info()
    html = ExceptionReporter(request, kind, info, data).get_traceback_html()
    log_erroneous_error(
        kind=kind.__name__,
        path=request.build_absolute_uri(),
        info=info,
        data="\n".join(traceback.format_exception(kind, info, data)),
        html=localize_css(html),
    )
