from django.apps import AppConfig
from django.core.checks import Tags, Warning, register
from django.db import connection
from django.utils.translation import gettext_lazy as _

from modelsearch.signal_handlers import register_signal_handlers

from . import checks  # NOQA: F401


class WagtailSearchAppConfig(AppConfig):
    name = "modelsearch"
    label = "modelsearch"
    verbose_name = _("Django-modelsearch")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        register_signal_handlers()

        if connection.vendor == "postgresql":
            # Only PostgreSQL has support for tsvector weights
            from modelsearch.backends.database.postgres.weights import set_weights

            set_weights()

        from modelsearch.models import IndexEntry

        IndexEntry.add_generic_relations()

    @register(Tags.compatibility, Tags.database)
    def check_if_sqlite_version_is_supported(app_configs, **kwargs):
        if connection.vendor == "sqlite":
            import sqlite3

            from modelsearch.backends.database.sqlite.utils import fts5_available

            if sqlite3.sqlite_version_info < (3, 19, 0):
                return [
                    Warning(
                        "Your SQLite version is older than 3.19.0. A fallback search backend will be used instead.",
                        hint="Upgrade your SQLite version to at least 3.19.0",
                        id="modelsearch.W002",
                        obj=WagtailSearchAppConfig,
                    )
                ]
            elif not fts5_available():
                return [
                    Warning(
                        "Your SQLite installation is missing the fts5 extension. A fallback search backend will be used instead.",
                        hint="Upgrade your SQLite installation to a version with fts5 enabled",
                        id="modelsearch.W003",
                        obj=WagtailSearchAppConfig,
                    )
                ]
        return []
