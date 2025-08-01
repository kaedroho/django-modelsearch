# Django ModelSearch

<p>
    <a href="https://github.com/kaedroho/django-modelsearch/actions">
        <img src="https://github.com/kaedroho/django-modelsearch/workflows/ModelSearch%20CI/badge.svg?branch=main" alt="Build Status" />
    </a>
    <a href="https://opensource.org/licenses/BSD-3-Clause">
        <img src="https://img.shields.io/badge/license-BSD-blue.svg" alt="License" />
    </a>
    <a href="https://pypi.python.org/pypi/modelsearch/">
        <img src="https://img.shields.io/pypi/v/modelsearch.svg" alt="Version" />
    </a>
    <a href="https://django-modelsearch.readthedocs.io/en/latest/">
        <img src="https://img.shields.io/badge/Documentation-blue" alt="Documentation" />
    </a>
</p>

Django ModelSearch allows you to index Django models and [search them using the ORM](https://django-modelsearch.readthedocs.io/en/latest/searching.html)!

It supports PostgreSQL FTS, SQLite FTS5, Elasticsearch (7.x, 8.x, and 9.x), and OpenSearch (1.x, 2.x, and 3.x).

Features:

- Index models in Elasticsearch and OpenSearch and query with the Django ORM
- Reuse existing QuerySets for search, works with Django paginators and `django-filter`
- Also supports PostgreSQL FTS and SQLite FTS5
- [Autocomplete](https://django-modelsearch.readthedocs.io/en/latest/searching.html#autocomplete-search)
- [Faceting](https://django-modelsearch.readthedocs.io/en/latest/searching.html#facet-field-name)
- [Per-field boosting](https://django-modelsearch.readthedocs.io/en/latest/indexing.html#boosting-search-fields)
- [Fuzzy Search](https://django-modelsearch.readthedocs.io/en/latest/searching.html#fuzzy-search)
- [Phrase search](https://django-modelsearch.readthedocs.io/en/latest/searching.html#phrase-search)
- [Structured queries](https://django-modelsearch.readthedocs.io/en/latest/searching.html#structured-queries)
- [Multi-table inheritance](https://django-modelsearch.readthedocs.io/en/latest/indexing.html#indexing-models-with-multi-table-inheritance)
- Zero-downtime index rebuilding (uses aliases to atomically swap in a new index when its ready)

This has been built into [Wagtail CMS](https://github.com/wagtail/wagtail) since 2014 and extracted into a separate package in March 2025.

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

By default, Django ModelSearch will index into the database configured in `DATABASES["default"]` and use PostgreSQL FTS or SQLite FTS, if available.

You can change the indexing configuration, or add additional backends with the `MODALSEARCH_BACKENDS` setting. For example, to configure Elasticsearch:

```python
# settings.py

MODELSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'modelsearch.backends.elasticsearch8',
        'URLS': ['https://localhost:9200'],
        'INDEX_PREFIX': 'modelsearch_',
        'TIMEOUT': 5,
        'OPTIONS': {},
        'INDEX_SETTINGS': {},
    }
}
```

## Indexing

To index a model, add `modelsearch.index.Indexed` to the model class and define some `search_fields`:

```python
from modelsearch import index
from modelsearch.queryset import SearchableQuerySetMixin


# This adds a .search() method to the models QuerySet
class SongQuerySet(SearchableQuerySetMixin, models.QuerySet):
    pass


# Create a model that inherits from Indexed
class Song(index.Indexed, models.Model):
    name = models.TextField()
    lyrics = models.TextField()
    release_date = models.DateField()
    artist = models.ForeignKey(Artist, related_name='songs')

    objects = SongQuerySet.as_manager()

    search_fields = [
        # Index text fields for full-text search
        # Boost the important fields
        index.SearchField('name', boost=2.0),
        index.SearchField('lyrics'),

        # Index fields that for filtering
        # These get inserted into Elasticsearch for fast filtering
        index.FilterField('release_date'),
        index.FilterField('artist'),

        # Pull in content from related models too
        index.RelatedFields('artist', [
           index.SearchField('name'),
        ]),
    ]
```

Then run the `django-admin rebuild_modelsearch_index` to create the indexes, mappings and insert the data.

## Searching

Search by calling `.search()` on the QuerySet!

```python
Song.objects.search("Flying Whales")
```

Searches also work when reversing `ForeignKey`s:

```python
opeth.songs.search("Ghost of ")
```

You can use Django's `.filter()`, `.exclude()` and `.order_by()` with search too:

```python
Song.objects.filter(release_date__year__lt=1971).search("Iron Man")
```

The filters are rewitten into the Elasticsearch query to make it run fast with a lot of data.
