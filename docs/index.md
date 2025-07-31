(modelsearch)=

# Welcome to the Django-modelsearch documentation!

This documentation provides an overview of how to index Django models and run search queries using the ORM.

```{toctree}
---
maxdepth: 2
---
indexing
searching
backends
```

## Installation

Install with PIP, then add to `INSTALLED_APPS` in your Django settings:

```shell
pip install modelsearch
```

```python
# settings.py

INSTALLED_APPS = [
    ...
    "modelsearch
    ...
]
```

## Configuration

In its default configuration, modelsearch will index content into your default database. If your database is either SQLite or PostgreSQL, it'll make use of the available full text search features of those databases automatically.

If you would like to change the configuration or use a different backend like Elasticsearch, see [](modelsearch_backends).

## Indexing

Models need to be indexed before they can be searched. We firstly need to define how each model should be mapped into the search index then they can be indexed in bulk using the `rebuild_modelsearch_index` management command or using a signal.


See [](modelsearch_indexing_update) for information on how to keep the objects in your search index in sync with the objects in your database.

If you have created some extra fields in a subclass of `Page` or `Image`, you may want to add these new fields to the search index, so a user's search query can match the Page or Image's extra content. See [](modelsearch_indexing_fields).

If you have a custom model which doesn't derive from `Page` or `Image` that you would like to make searchable, see [](modelsearch_indexing_models).

## Searching

Wagtail provides an API for performing search queries on your models. You can also perform search queries on Django QuerySets.

See [](modelsearch_searching).
