from elasticsearch import VERSION as ELASTICSEARCH_VERSION
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk

from modelsearch.backends.elasticsearchbase import (
    ElasticsearchBaseAutocompleteQueryCompiler,
    ElasticsearchBaseIndex,
    ElasticsearchBaseMapping,
    ElasticsearchBaseSearchBackend,
    ElasticsearchBaseSearchQueryCompiler,
    ElasticsearchBaseSearchResults,
)



class Elasticsearch7Mapping(ElasticsearchBaseMapping):
    pass


class Elasticsearch7Index(ElasticsearchBaseIndex):
    pass


class Elasticsearch7SearchQueryCompiler(ElasticsearchBaseSearchQueryCompiler):
    mapping_class = Elasticsearch7Mapping


class Elasticsearch7SearchResults(ElasticsearchBaseSearchResults):
    pass


class Elasticsearch7AutocompleteQueryCompiler(ElasticsearchBaseAutocompleteQueryCompiler):
    mapping_class = Elasticsearch7Mapping


class Elasticsearch7SearchBackend(ElasticsearchBaseSearchBackend):
    mapping_class = Elasticsearch7Mapping
    index_class = Elasticsearch7Index
    query_compiler_class = Elasticsearch7SearchQueryCompiler
    autocomplete_query_compiler_class = Elasticsearch7AutocompleteQueryCompiler
    results_class = Elasticsearch7SearchResults
    NotFoundError = NotFoundError
    client_class = Elasticsearch
    use_new_elasticsearch_api = ELASTICSEARCH_VERSION >= (7, 15)

    def bulk(self, *args, **kwargs):
        return bulk(*args, **kwargs)


SearchBackend = Elasticsearch7SearchBackend
