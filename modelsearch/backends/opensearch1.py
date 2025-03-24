from modelsearch.backends.elasticsearch7 import (
    Elasticsearch7AutocompleteQueryCompiler,
    Elasticsearch7Index,
    Elasticsearch7Mapping,
    Elasticsearch7SearchBackend,
    Elasticsearch7SearchQueryCompiler,
    Elasticsearch7SearchResults,
)


class OpenSearch1Mapping(Elasticsearch7Mapping):
    pass


class OpenSearch1Index(Elasticsearch7Index):
    pass


class OpenSearch1SearchQueryCompiler(Elasticsearch7SearchQueryCompiler):
    mapping_class = OpenSearch1Mapping


class OpenSearch1SearchResults(Elasticsearch7SearchResults):
    pass


class OpenSearch1AutocompleteQueryCompiler(Elasticsearch7AutocompleteQueryCompiler):
    mapping_class = OpenSearch1Mapping


class OpenSearch1SearchBackend(Elasticsearch7SearchBackend):
    mapping_class = OpenSearch1Mapping
    index_class = OpenSearch1Index
    query_compiler_class = OpenSearch1SearchQueryCompiler
    autocomplete_query_compiler_class = OpenSearch1AutocompleteQueryCompiler
    results_class = OpenSearch1SearchResults


SearchBackend = OpenSearch1SearchBackend
