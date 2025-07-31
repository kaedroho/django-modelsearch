from modelsearch.backends.elasticsearch8 import (
    Elasticsearch8AutocompleteQueryCompiler,
    Elasticsearch8Index,
    Elasticsearch8Mapping,
    Elasticsearch8SearchBackend,
    Elasticsearch8SearchQueryCompiler,
    Elasticsearch8SearchResults,
)

class Elasticsearch9Mapping(Elasticsearch8Mapping):
    pass


class Elasticsearch9Index(Elasticsearch8Index):
    pass


class Elasticsearch9SearchQueryCompiler(Elasticsearch8SearchQueryCompiler):
    mapping_class = Elasticsearch9Mapping


class Elasticsearch9SearchResults(Elasticsearch8SearchResults):
    pass


class Elasticsearch9AutocompleteQueryCompiler(Elasticsearch8AutocompleteQueryCompiler):
    mapping_class = Elasticsearch9Mapping


class Elasticsearch9SearchBackend(Elasticsearch8SearchBackend):
    mapping_class = Elasticsearch9Mapping
    index_class = Elasticsearch9Index
    query_compiler_class = Elasticsearch9SearchQueryCompiler
    autocomplete_query_compiler_class = Elasticsearch9AutocompleteQueryCompiler
    results_class = Elasticsearch9SearchResults


SearchBackend = Elasticsearch9SearchBackend
