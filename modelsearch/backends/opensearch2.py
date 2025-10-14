from opensearchpy import NotFoundError, OpenSearch
from opensearchpy.helpers import bulk

from modelsearch.backends.elasticsearchbase import (
    ElasticsearchBaseAutocompleteQueryCompiler,
    ElasticsearchBaseIndex,
    ElasticsearchBaseMapping,
    ElasticsearchBaseSearchBackend,
    ElasticsearchBaseSearchQueryCompiler,
    ElasticsearchBaseSearchResults,
)


class OpenSearch2Mapping(ElasticsearchBaseMapping):
    pass


class OpenSearch2Index(ElasticsearchBaseIndex):
    pass


class OpenSearch2SearchQueryCompiler(ElasticsearchBaseSearchQueryCompiler):
    mapping_class = OpenSearch2Mapping


class OpenSearch2SearchResults(ElasticsearchBaseSearchResults):
    pass


class OpenSearch2AutocompleteQueryCompiler(ElasticsearchBaseAutocompleteQueryCompiler):
    mapping_class = OpenSearch2Mapping


class OpenSearch2SearchBackend(ElasticsearchBaseSearchBackend):
    mapping_class = OpenSearch2Mapping
    index_class = OpenSearch2Index
    query_compiler_class = OpenSearch2SearchQueryCompiler
    autocomplete_query_compiler_class = OpenSearch2AutocompleteQueryCompiler
    results_class = OpenSearch2SearchResults
    NotFoundError = NotFoundError
    client_class = OpenSearch

    def bulk(self, *args, **kwargs):
        return bulk(*args, **kwargs)


SearchBackend = OpenSearch2SearchBackend
