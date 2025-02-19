from crispy_forms.bootstrap import StrictButton
from django.forms import Form
from js_asset import JS


class GFLExportForm(Form):
    def get_form_action(self):
        return StrictButton(
            "<i class='fas fa-download'></i> Export",
            type="submit",
            css_class="btn btn-sm btn-primary",
            id="export_btn",
        )

    class Media:
        js = [JS("dynpy_gfl/js/export_form.js", {"defer": "true"})]
