from unittest.mock import MagicMock

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.template import Context, Template

from dynpy_cas.enums import Codename
from dynpy_cas.templatetags.permission_tags import do_has_edit_permission


def describe_editor_only_tag():
    def it_hides_content_if_user_does_not_have_edit_permission(rf, test_user, mocker):
        request = rf.post("/")
        request.user = test_user
        mock_resolve = MagicMock()
        mock_resolve.app_name = "aging"
        mocker.patch("dynpy_cas.templatetags.permission_tags.resolve", return_value=mock_resolve)

        template_str = (
            "{% load permission_tags %}"
            "{% editor_only %}"
            "   Some secret stuff"
            "{% end_editor_only %}"
        )
        context = Context({"request": request})
        template = Template(template_str).render(context)

        assert "Some secret stuff" not in template

    def it_shows_content_if_user_has_edit_permission(rf, test_user, mocker):
        request = rf.post("/")
        request.user = test_user
        mock_resolve = MagicMock()
        mock_resolve.app_name = "aging"
        mocker.patch("dynpy_cas.templatetags.permission_tags.resolve", return_value=mock_resolve)

        editor_perm = Permission.objects.get(codename=Codename.AGING_EDITOR)
        test_user.user_permissions.add(editor_perm)
        template_str = (
            "{% load permission_tags %}"
            "{% editor_only %}"
            "   Some secret stuff"
            "{% end_editor_only %}"
        )
        context = Context({"request": request})
        template = Template(template_str).render(context)

        assert "Some secret stuff" in template


def describe_has_edit_permission_filter():
    def it_returns_True_if_user_has_edit_permission(test_user):
        editor_perm = Permission.objects.get(codename=Codename.AGING_EDITOR)
        test_user.user_permissions.add(editor_perm)
        assert do_has_edit_permission(test_user, "aging") is True

    def it_returns_False_if_user_does_not_have_edit_permission(test_user):
        assert do_has_edit_permission(test_user, "aging") is False
