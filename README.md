# Django ModelSearch

Django ModelSearch allows you index and search Django models using Elasticsearch.

This was built in to [Wagtail CMS](https://github.com/wagtail/wagtail) since 2014 and this package now allows it to be used in a standalone way on all other Django projects!

## Installation

Install with PIP, then add to `INSTALLED_APPS` in your Django settings:

```shell
pip install django-modelsearch
```

```python
# settings.py

INSTALLED_APPS = [
    ...
    "modelsearch
    ...
]
```

Configure a backend in Django settings. For example, to configure Elasticsearch:

```python
# settings.py

MODELSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.elasticsearch8',
        'URLS': ['https://localhost:9200'],
        'INDEX': 'wagtail',
        'TIMEOUT': 5,
        'OPTIONS': {},
        'INDEX_SETTINGS': {},
    }
}
```

## Indexing content

To index a model, add `modelsearch.index.Indexed` to the model class and define some `search_fields`:

```
from modelsearch import index

class Book(index.Indexed, models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=255, choices=GENRE_CHOICES)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published_date = models.DateTimeField()

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

## Searching content

Searching is done using a new `.search()` method that is added to the querysets of indexed models.

You can use Django's `.filter()`, `.exclude()`, and `.order_by()` with the search method and these will be added as filters in the Elasticsearch query.
Remember to index any fields you want to filter/order on with `index.FilterField` first!

For example:

```python
>>> Book.objects.filter(author=roald_dahl).search("chocolate factory")
[<Book: Charlie and the chocolate factory>]
```
