import hashlib
import re

from django.conf import settings
from django.db.models.expressions import F
from django.utils import timezone

from dynpy.erroneous.models import Error


def log_erroneous_error(kind: str, html: str, info: str, data: str, path: str) -> Error:
    if settings.DEBUG is False:
        # The hash is a combination of stacktrace and today's date.
        today = timezone.now().date()
        str_to_hash = "\n".join(str(arg) for arg in [kind, info, data]) + str(today)

        err, created = Error.objects.get_or_create(
            hash=hashlib.md5(str_to_hash.encode()).hexdigest(),
            defaults={
                "kind": kind,
                "html": html,
                "path": path,
                "info": info,
                "data": data,
            },
        )
        if not created:
            Error.objects.filter(id=err.id).update(count=F("count") + 1)

        return err
    else:
        print(f"{kind}: {info}")


def localize_css(html: str):
    """
    Change scope of all internal css to sibling elements only
    so the styles don't effect the entire page.
    Useful for embedding Django error templates into erroneous error pages.
    """

    style_re = r'<style type="text\/css">[^<]*<\/style>'
    _id = "pageTemplate"
    style = re.search(style_re, html)
    if style:
        localized_style = re.sub(r"\S.*{", f"#{_id} " + r"\g<0>", style.group())
        html = re.sub(style_re, localized_style, html)
        return f'<div id="{_id}">{html}</div>'
