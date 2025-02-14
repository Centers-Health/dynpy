from django.conf import settings


def get_app_name_from_module(module: str):
    # Strip ".apps.AppConfig" from app names
    installed_app_names = [name.split(".apps")[0] for name in settings.INSTALLED_APPS]

    app_name = ""
    split_module = module.split(".")
    for i, val in enumerate(split_module):
        next_app_name = ".".join(split_module[0 : i + 1])
        if any([name.startswith(next_app_name) for name in installed_app_names]):
            app_name = next_app_name
        elif app_name == "":
            return None
        else:
            return app_name
