from opensearchpy import NotFoundError

from modelsearch.backends.opensearch2 import (
    OpenSearch2AutocompleteQueryCompiler,
    OpenSearch2Index,
    OpenSearch2Mapping,
    OpenSearch2SearchBackend,
    OpenSearch2SearchQueryCompiler,
    OpenSearch2SearchResults,
)
from modelsearch.index import class_is_indexed


class OpenSearch3Mapping(OpenSearch2Mapping):
    pass


class OpenSearch3Index(OpenSearch2Index):
    def put(self):
        self.es.indices.create(index=self.name, body=self.backend.settings)

    def delete(self):
        try:
            self.es.indices.delete(index=self.name)
        except NotFoundError:
            pass

    def refresh(self):
        self.es.indices.refresh(index=self.name)

    def exists(self):
        return self.es.indices.exists(index=self.name)

    def add_item(self, item):
        # Make sure the object can be indexed
        if not class_is_indexed(item.__class__):
            return

        # Get mapping
        mapping = self.mapping_class(item.__class__)

        # Add document to index
        self.es.index(
            index=self.name,
            body=mapping.get_document(item),
            id=mapping.get_document_id(item),
        )


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
