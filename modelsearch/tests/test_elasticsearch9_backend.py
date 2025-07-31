import unittest

from django.test import TestCase

from .elasticsearch_common_tests import ElasticsearchCommonSearchBackendTests

try:
    from elasticsearch import VERSION as ELASTICSEARCH_VERSION
except ImportError:
    ELASTICSEARCH_VERSION = (0, 0, 0)


@unittest.skipIf(ELASTICSEARCH_VERSION[0] != 9, "Elasticsearch 9 required")
class TestElasticsearch9SearchBackend(ElasticsearchCommonSearchBackendTests, TestCase):
    backend_path = "modelsearch.backends.elasticsearch9"
