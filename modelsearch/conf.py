from functools import cache

from django.core.exceptions import ImproperlyConfigured


@cache
def get_app_config():
    """
    Return the ModelSearchAppConfig instance registered in the Django app registry.
    This allows for ModelSearchAppConfig to be subclassed and made available under a different
    module path and/or app label, rather than hardcoding "modelsearch" - Wagtail makes use of this
    to allow existing projects to continue using "wagtail.search" in INSTALLED_APPS.
    """
    from django.apps import apps

    from modelsearch.apps import ModelSearchAppConfig

    app_configs = [
        app_config
        for app_config in apps.get_app_configs()
        if isinstance(app_config, ModelSearchAppConfig)
    ]
    if len(app_configs) == 0:  # pragma: no cover
        raise ImproperlyConfigured(
            "The modelsearch app was not found in INSTALLED_APPS"
        )
    elif len(app_configs) > 1:  # pragma: no cover
        raise ImproperlyConfigured(
            "Multiple instances of the modelsearch app were found in INSTALLED_APPS"
        )
    return app_configs[0]
