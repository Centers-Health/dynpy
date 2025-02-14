from django.apps import AppConfig


class AdminConfig(AppConfig):
    name = "dynpy.admin"
    label = "dynpy_admin"  # Default is 'admin' which conflicts with django's admin
