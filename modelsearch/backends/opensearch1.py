from opensearchpy import OpenSearch, NotFoundError
from opensearchpy.helpers import bulk

from modelsearch.backends.elasticsearchbase import (
    ElasticsearchBaseAutocompleteQueryCompiler,
    ElasticsearchBaseIndex,
    ElasticsearchBaseMapping,
    ElasticsearchBaseSearchBackend,
    ElasticsearchBaseSearchQueryCompiler,
    ElasticsearchBaseSearchResults,
)


class OpenSearch1Mapping(ElasticsearchBaseMapping):
    pass


class OpenSearch1Index(ElasticsearchBaseIndex):
    pass


class OpenSearch1SearchQueryCompiler(ElasticsearchBaseSearchQueryCompiler):
    mapping_class = OpenSearch1Mapping


class OpenSearch1SearchResults(ElasticsearchBaseSearchResults):
    pass


class OpenSearch1AutocompleteQueryCompiler(ElasticsearchBaseAutocompleteQueryCompiler):
    mapping_class = OpenSearch1Mapping


class OpenSearch1SearchBackend(ElasticsearchBaseSearchBackend):
    mapping_class = OpenSearch1Mapping
    index_class = OpenSearch1Index
    query_compiler_class = OpenSearch1SearchQueryCompiler
    autocomplete_query_compiler_class = OpenSearch1AutocompleteQueryCompiler
    results_class = OpenSearch1SearchResults
    NotFoundError = NotFoundError
    client_class = OpenSearch

    def bulk(self, *args, **kwargs):
        return bulk(*args, **kwargs)


SearchBackend = OpenSearch1SearchBackend
