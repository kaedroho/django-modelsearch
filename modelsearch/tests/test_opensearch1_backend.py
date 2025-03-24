from django.test import TestCase

from .elasticsearch_common_tests import ElasticsearchCommonSearchBackendTests


class TestOpenSearch1SearchBackend(ElasticsearchCommonSearchBackendTests, TestCase):
    backend_path = "modelsearch.backends.opensearch1"
