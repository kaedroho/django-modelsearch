from modelsearch.backends.opensearch1 import (
    OpenSearch2AutocompleteQueryCompiler,
    OpenSearch2Index,
    OpenSearch2Mapping,
    OpenSearch2SearchBackend,
    OpenSearch2SearchQueryCompiler,
    OpenSearch2SearchResults,
)


class OpenSearch3Mapping(OpenSearch2Mapping):
    pass


class OpenSearch3Index(OpenSearch2Index):
    pass


class OpenSearch3SearchQueryCompiler(OpenSearch2SearchQueryCompiler):
    mapping_class = OpenSearch3Mapping


class OpenSearch3SearchResults(OpenSearch2SearchResults):
    pass


class OpenSearch3AutocompleteQueryCompiler(OpenSearch2AutocompleteQueryCompiler):
    mapping_class = OpenSearch3Mapping


class OpenSearch3SearchBackend(OpenSearch2SearchBackend):
    mapping_class = OpenSearch3Mapping
    index_class = OpenSearch3Index
    query_compiler_class = OpenSearch3SearchQueryCompiler
    autocomplete_query_compiler_class = OpenSearch3AutocompleteQueryCompiler
    results_class = OpenSearch3SearchResults


SearchBackend = OpenSearch3SearchBackend
