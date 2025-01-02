"""
Based on https://github.com/mridang/django-erroneous

Usage:

JS error logger:
    - Add the following to your template:
        {% include "dyn-erroneous/includes/erroneous_script.html" %}
    - Add the following path to your urls:
        path("dyn-ajax/erroneous/", include("dynpy.erroneous.ajax_urls"))
"""
