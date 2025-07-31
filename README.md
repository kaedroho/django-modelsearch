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
- Autocomplete
- Faceting
- Per-field boosting
- Fuzzy Search
- Phrase search
- Query combinators

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
        'INDEX': 'wagtail',
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

class BookQuerySet(models.QuerySet, SearchableQuerySetMixin):
    pass

class Book(index.Indexed, models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=255, choices=GENRE_CHOICES)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published_date = models.DateTimeField()

    objects = BookQuerySet.as_manager()

    search_fields = [
        index.SearchField('title', boost=10),
        index.AutocompleteField('title', boost=10),
        index.SearchField('get_genre_display'),

        index.FilterField('genre'),
        index.FilterField('author'),
        index.FilterField('published_date'),
    ]
```

Then run the `rebuild_index` management command to build the search index.

## Searching

You can search models using the `.search()` QuerySet method (added by `SearchableQuerySetMixin`). For example:

```python
>>> Book.objects.filter(author=roald_dahl).search("chocolate factory")
[<Book: Charlie and the chocolate factory>]
```

`.search()` can be used in conjunction with most other QuerySet Methods like `.filter()`, `.exclude()` or `.order_by()`. When using Elasticsearch, these are automatically converted to the same Elasticsearch Query, so any fields used here must be indexed with `index.FilterField` so they are added to the Elasticsearch index.

### Autocomplete

To autocomplete a partial search query, use the `.autocomplete()` method. For example:

```python
>>> Book.objects.filter(author=roald_dahl).search("choco")
[<Book: Charlie and the chocolate factory>]
```

Note that fields used in autocomplete need to also be indexed as an `AutocompleteField` as autocompletable fields need to be indexed differently.
