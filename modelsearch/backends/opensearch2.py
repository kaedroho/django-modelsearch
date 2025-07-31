from modelsearch.backends.opensearch1 import (
    OpenSearch1AutocompleteQueryCompiler,
    OpenSearch1Index,
    OpenSearch1Mapping,
    OpenSearch1SearchBackend,
    OpenSearch1SearchQueryCompiler,
    OpenSearch1SearchResults,
)


class OpenSearch2Mapping(OpenSearch1Mapping):
    pass


class OpenSearch2Index(OpenSearch1Index):
    pass


class OpenSearch2SearchQueryCompiler(OpenSearch1SearchQueryCompiler):
    mapping_class = OpenSearch2Mapping


class OpenSearch2SearchResults(OpenSearch1SearchResults):
    pass


class OpenSearch2AutocompleteQueryCompiler(OpenSearch1AutocompleteQueryCompiler):
    mapping_class = OpenSearch2Mapping


class OpenSearch2SearchBackend(OpenSearch1SearchBackend):
    mapping_class = OpenSearch2Mapping
    index_class = OpenSearch2Index
    query_compiler_class = OpenSearch2SearchQueryCompiler
    autocomplete_query_compiler_class = OpenSearch2AutocompleteQueryCompiler
    results_class = OpenSearch2SearchResults


SearchBackend = OpenSearch2SearchBackend
