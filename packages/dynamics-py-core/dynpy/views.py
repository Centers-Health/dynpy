import mimetypes
import posixpath
from pathlib import Path

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseNotModified,
    HttpResponseServerError,
)
from django.shortcuts import render
from django.utils._os import safe_join
from django.utils.http import http_date
from django.utils.translation import gettext as _
from django.views.generic import View
from django.views.generic.edit import UpdateView
from django.views.static import was_modified_since


class MediaFileView(View):
    """
    Extension of django.views.static.serve view for serving files
    with ability to add permissions based on user and url kwargs.
    """

    force_download: bool = False
    authentication_required: bool = True

    def user_has_permission(self, user: AbstractBaseUser, **kwargs) -> bool:
        return True

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        document_root = settings.MEDIA_ROOT
        prefix = settings.MEDIA_URL.lstrip("/")

        path = posixpath.normpath(request.path_info).lstrip("/")
        fullpath = Path(safe_join(document_root, path.replace(prefix, "", 1)))

        if fullpath.is_dir():
            raise Http404(_("Directory indexes are not allowed here."))

        if not fullpath.exists():
            raise Http404(_("“%(path)s” does not exist") % {"path": fullpath})

        # Respect the If-Modified-Since header.
        statobj = fullpath.stat()
        if not was_modified_since(
            request.headers.get("if-modified-since"),
            statobj.st_mtime,
        ):
            return HttpResponseNotModified()
        content_type, encoding = mimetypes.guess_type(str(fullpath))
        content_type = (
            content_type if content_type and not self.force_download else "application/octet-stream"
        )

        if (
            self.authentication_required and not request.user.is_authenticated
        ) or not self.user_has_permission(request.user, **kwargs):
            return HttpResponse("You do not have permission to access this file", status=403)

        response = FileResponse(fullpath.open("rb"), content_type=content_type)
        response.headers["Last-Modified"] = http_date(statobj.st_mtime)
        if encoding:
            response.headers["Content-Encoding"] = encoding
        return response


class CreateUpdateView(UpdateView):
    """
    View for updating an object or creating a new one if it does not exist.

    This class is a wrapper of Django's UpdateView which
    returns an error for requests with no pk or slug
    This class captures that error, allowing the page to load as a CreateView.

    Use this with a URL with an optional pk.
    """

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying if a pk or slug is given otherwise returns None.
        """
        try:
            return super().get_object()
        except AttributeError:
            return None


def server_error(request):
    return HttpResponseServerError(render(request, "dynpy/500.html", status=500))


def page_not_found(request, exception=None):
    return HttpResponseNotFound(
        render(request, "dynpy/404.html", context={"exception": exception}, status=404)
    )


def permission_denied(request, exception=None):
    return HttpResponseForbidden(
        render(request, "dynpy/403.html", context={"exception": exception}, status=403)
    )
