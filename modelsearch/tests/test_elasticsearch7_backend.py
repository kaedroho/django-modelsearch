import datetime
import json
import unittest
from unittest import mock

from django.db.models import Q
from django.test import TestCase

from modelsearch.query import MATCH_ALL, Fuzzy, Phrase
from modelsearch.test.testapp import models

from .elasticsearch_common_tests import ElasticsearchCommonSearchBackendTests

try:
    from elasticsearch import VERSION as ELASTICSEARCH_VERSION
    from elasticsearch.serializer import JSONSerializer

    from modelsearch.backends.elasticsearch7 import Elasticsearch7SearchBackend
except ImportError:
    ELASTICSEARCH_VERSION = (0, 0, 0)


use_new_elasticsearch_api = ELASTICSEARCH_VERSION >= (7, 15)

if use_new_elasticsearch_api:
    search_query_kwargs = {
        "query": "QUERY",
    }
else:
    search_query_kwargs = {"body": {"query": "QUERY"}}


@unittest.skipIf(ELASTICSEARCH_VERSION[0] != 7, "Elasticsearch 7 required")
class TestElasticsearch7SearchBackend(ElasticsearchCommonSearchBackendTests, TestCase):
    backend_path = "modelsearch.backends.elasticsearch7"


@unittest.skipIf(ELASTICSEARCH_VERSION[0] != 7, "Elasticsearch 7 required")
class TestElasticsearch7SearchQuery(TestCase):
    maxDiff = None

    def assertDictEqual(self, a, b):
        default = JSONSerializer().default
        self.assertEqual(
            json.dumps(a, sort_keys=True, default=default),
            json.dumps(b, sort_keys=True, default=default),
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.query_compiler_class = Elasticsearch7SearchBackend.query_compiler_class
        cls.autocomplete_query_compiler_class = (
            Elasticsearch7SearchBackend.autocomplete_query_compiler_class
        )

    def test_simple(self):
        # Create a query
        query = self.query_compiler_class(models.Book.objects.all(), "Hello")

        # Check it
        expected_result = {
            "bool": {
                "filter": {"match": {"_django_content_type": "searchtests.Book"}},
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_simple_autocomplete(self):
        # Create a query
        query = self.autocomplete_query_compiler_class(
            models.Book.objects.all(), "Hello"
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": {"match": {"_django_content_type": "searchtests.Book"}},
                "must": {
                    "match": {
                        "_edgengrams": {
                            "query": "Hello",
                        }
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_match_all_autocomplete(self):
        # Create a query
        query = self.autocomplete_query_compiler_class(
            models.Book.objects.all(), MATCH_ALL
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": {"match": {"_django_content_type": "searchtests.Book"}},
                "must": {"match_all": {}},
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_non_supported_queries_autocomplete(self):
        # Create a query
        query = self.autocomplete_query_compiler_class(
            models.Book.objects.all(), Fuzzy("Hello")
        )

        # Check it
        with self.assertRaises(NotImplementedError):
            query.get_query()

    def test_none_query_string(self):
        # Create a query
        query = self.query_compiler_class(models.Book.objects.all(), MATCH_ALL)

        # Check it
        expected_result = {
            "bool": {
                "filter": {"match": {"_django_content_type": "searchtests.Book"}},
                "must": {"match_all": {}},
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_and_operator(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.all(), "Hello", operator="and"
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": {"match": {"_django_content_type": "searchtests.Book"}},
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                        "operator": "and",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_filter(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(title="Test"), "Hello"
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {"term": {"title_filter": "Test"}},
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_and_filter(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(
                title="Test", publication_date=datetime.date(2017, 10, 18)
            ),
            "Hello",
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {
                        "bool": {
                            "must": [
                                {"term": {"publication_date_filter": "2017-10-18"}},
                                {"term": {"title_filter": "Test"}},
                            ]
                        }
                    },
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }

        # Make sure field filters are sorted (as they can be in any order which may cause false positives)
        query = query.get_query()
        field_filters = query["bool"]["filter"][1]["bool"]["must"]
        field_filters[:] = sorted(
            field_filters, key=lambda f: list(f["term"].keys())[0]
        )

        self.assertDictEqual(query, expected_result)

    def test_or_filter(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(
                Q(title="Test") | Q(publication_date=datetime.date(2017, 10, 18))
            ),
            "Hello",
        )

        # Make sure field filters are sorted (as they can be in any order which may cause false positives)
        query = query.get_query()
        field_filters = query["bool"]["filter"][1]["bool"]["should"]
        field_filters[:] = sorted(
            field_filters, key=lambda f: list(f["term"].keys())[0]
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {
                        "bool": {
                            "should": [
                                {"term": {"publication_date_filter": "2017-10-18"}},
                                {"term": {"title_filter": "Test"}},
                            ]
                        }
                    },
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query, expected_result)

    def test_negated_filter(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.exclude(publication_date=datetime.date(2017, 10, 18)),
            "Hello",
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {
                        "bool": {
                            "mustNot": {
                                "term": {"publication_date_filter": "2017-10-18"}
                            }
                        }
                    },
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_fields(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.all(), "Hello", fields=["title"]
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": {"match": {"_django_content_type": "searchtests.Book"}},
                "must": {
                    "match": {
                        "title": {
                            "query": "Hello",
                            "boost": 10.0,
                        },
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_fields_with_and_operator(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.all(), "Hello", fields=["title"], operator="and"
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": {"match": {"_django_content_type": "searchtests.Book"}},
                "must": {
                    "match": {
                        "title": {
                            "query": "Hello",
                            "boost": 10.0,
                            "operator": "and",
                        }
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_multiple_fields(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.all(), "Hello", fields=["title", "summary"]
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": {"match": {"_django_content_type": "searchtests.Book"}},
                "must": {
                    "multi_match": {
                        "fields": [
                            "title^10.0",
                            "summary^2.0",
                        ],
                        "query": "Hello",
                    }
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_multiple_fields_with_and_operator(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.all(),
            "Hello",
            fields=["title", "summary"],
            operator="and",
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": {"match": {"_django_content_type": "searchtests.Book"}},
                "must": {
                    "multi_match": {
                        "fields": [
                            "title^10.0",
                            "summary^2.0",
                        ],
                        "query": "Hello",
                        "operator": "and",
                    }
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_exact_lookup(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(title__exact="Test"), "Hello"
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {"term": {"title_filter": "Test"}},
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_none_lookup(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(title=None), "Hello"
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {"bool": {"mustNot": {"exists": {"field": "title_filter"}}}},
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_isnull_true_lookup(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(title__isnull=True), "Hello"
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {"bool": {"mustNot": {"exists": {"field": "title_filter"}}}},
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_isnull_false_lookup(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(title__isnull=False), "Hello"
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {"exists": {"field": "title_filter"}},
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_startswith_lookup(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(title__startswith="Test"), "Hello"
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {"prefix": {"title_filter": "Test"}},
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_gt_lookup(self):
        # This also tests conversion of python dates to strings

        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(
                publication_date__gt=datetime.datetime(2014, 4, 29)
            ),
            "Hello",
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {"range": {"publication_date_filter": {"gt": "2014-04-29"}}},
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_lt_lookup(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(
                publication_date__lt=datetime.datetime(2014, 4, 29)
            ),
            "Hello",
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {"range": {"publication_date_filter": {"lt": "2014-04-29"}}},
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_gte_lookup(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(
                publication_date__gte=datetime.datetime(2014, 4, 29)
            ),
            "Hello",
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {"range": {"publication_date_filter": {"gte": "2014-04-29"}}},
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_lte_lookup(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(
                publication_date__lte=datetime.datetime(2014, 4, 29)
            ),
            "Hello",
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {"range": {"publication_date_filter": {"lte": "2014-04-29"}}},
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_range_lookup(self):
        start_date = datetime.datetime(2014, 4, 29)
        end_date = datetime.datetime(2014, 8, 19)

        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.filter(publication_date__range=(start_date, end_date)),
            "Hello",
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {
                        "range": {
                            "publication_date_filter": {
                                "gte": "2014-04-29",
                                "lte": "2014-08-19",
                            }
                        }
                    },
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    },
                },
            }
        }
        self.assertDictEqual(query.get_query(), expected_result)

    def test_custom_ordering(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.order_by("publication_date"),
            "Hello",
            order_by_relevance=False,
        )

        # Check it
        expected_result = [{"publication_date_filter": "asc"}]
        self.assertDictEqual(query.get_sort(), expected_result)

    def test_custom_ordering_reversed(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.order_by("-publication_date"),
            "Hello",
            order_by_relevance=False,
        )

        # Check it
        expected_result = [{"publication_date_filter": "desc"}]
        self.assertDictEqual(query.get_sort(), expected_result)

    def test_custom_ordering_multiple(self):
        # Create a query
        query = self.query_compiler_class(
            models.Book.objects.order_by("publication_date", "number_of_pages"),
            "Hello",
            order_by_relevance=False,
        )

        # Check it
        expected_result = [
            {"publication_date_filter": "asc"},
            {"number_of_pages_filter": "asc"},
        ]
        self.assertDictEqual(query.get_sort(), expected_result)

    def test_phrase_query(self):
        # Create a query
        query_compiler = self.query_compiler_class(
            models.Book.objects.all(), Phrase("Hello world")
        )

        # Check it
        expected_result = {
            "multi_match": {
                "fields": [
                    "_all_text",
                    "_all_text_boost_10_0^10.0",
                    "_all_text_boost_2_0^2.0",
                ],
                "query": "Hello world",
                "type": "phrase",
            },
        }
        self.assertDictEqual(query_compiler.get_inner_query(), expected_result)

    def test_phrase_query_multiple_fields(self):
        # Create a query
        query_compiler = self.query_compiler_class(
            models.Book.objects.all(),
            Phrase("Hello world"),
            fields=["title", "summary"],
        )

        # Check it
        expected_result = {
            "multi_match": {
                "query": "Hello world",
                "fields": [
                    "title^10.0",
                    "summary^2.0",
                ],
                "type": "phrase",
            }
        }
        self.assertDictEqual(query_compiler.get_inner_query(), expected_result)

    def test_phrase_query_single_field(self):
        # Create a query
        query_compiler = self.query_compiler_class(
            models.Book.objects.all(), Phrase("Hello world"), fields=["title"]
        )

        # Check it
        expected_result = {
            "match_phrase": {
                "title": {
                    "query": "Hello world",
                    "boost": 10.0,
                },
            },
        }
        self.assertDictEqual(query_compiler.get_inner_query(), expected_result)

    def test_fuzzy_query(self):
        # Create a query
        query_compiler = self.query_compiler_class(
            models.Book.objects.all(),
            Fuzzy("Hello world"),
        )

        # Check it
        expected_result = {
            "multi_match": {
                "fields": [
                    "_all_text",
                    "_all_text_boost_10_0^10.0",
                    "_all_text_boost_2_0^2.0",
                ],
                "query": "Hello world",
                "fuzziness": "AUTO",
            }
        }
        self.assertDictEqual(query_compiler.get_inner_query(), expected_result)

    def test_fuzzy_query_single_field(self):
        # Create a query
        query_compiler = self.query_compiler_class(
            models.Book.objects.all(),
            Fuzzy("Hello world"),
            fields=["title"],
        )

        # Check it
        expected_result = {
            "match": {
                "title": {
                    "query": "Hello world",
                    "fuzziness": "AUTO",
                    "boost": 10.0,
                },
            }
        }
        self.assertDictEqual(query_compiler.get_inner_query(), expected_result)

    def test_fuzzy_query_multiple_fields(self):
        # Create a query
        query_compiler = self.query_compiler_class(
            models.Book.objects.all(),
            Fuzzy("Hello world"),
            fields=["title", "summary"],
        )

        expected_result = {
            "multi_match": {
                "fields": [
                    "title^10.0",
                    "summary^2.0",
                ],
                "query": "Hello world",
                "fuzziness": "AUTO",
            }
        }
        self.assertDictEqual(query_compiler.get_inner_query(), expected_result)

    def test_fuzzy_query_with_operator(self):
        # Create a query
        query_compiler = self.query_compiler_class(
            models.Book.objects.all(),
            Fuzzy("Hello world", operator="and"),
        )

        # Check it
        expected_result = {
            "multi_match": {
                "fields": [
                    "_all_text",
                    "_all_text_boost_10_0^10.0",
                    "_all_text_boost_2_0^2.0",
                ],
                "query": "Hello world",
                "fuzziness": "AUTO",
                "operator": "and",
            }
        }
        self.assertDictEqual(query_compiler.get_inner_query(), expected_result)

    def test_year_filter(self):
        # Create a query
        query_compiler = self.query_compiler_class(
            models.Book.objects.filter(publication_date__year__lt=1900), "Hello"
        )

        # Check it
        expected_result = {
            "bool": {
                "filter": [
                    {"match": {"_django_content_type": "searchtests.Book"}},
                    {"range": {"publication_date_filter": {"lt": "1900-01-01"}}},
                ],
                "must": {
                    "multi_match": {
                        "fields": [
                            "_all_text",
                            "_all_text_boost_10_0^10.0",
                            "_all_text_boost_2_0^2.0",
                        ],
                        "query": "Hello",
                    }
                },
            }
        }
        self.assertDictEqual(query_compiler.get_query(), expected_result)


@unittest.skipIf(ELASTICSEARCH_VERSION[0] != 7, "Elasticsearch 7 required")
class TestElasticsearch7SearchResults(TestCase):
    fixtures = ["search"]

    def assertDictEqual(self, a, b):
        default = JSONSerializer().default
        self.assertEqual(json.dumps(a, sort_keys=True, default=default), json.dumps)

    def get_results(self):
        backend = Elasticsearch7SearchBackend({})
        query = mock.MagicMock()
        query.queryset = models.Book.objects.all()
        query.get_query.return_value = "QUERY"
        query.get_sort.return_value = None
        return backend.results_class(backend, query)

    def construct_search_response(self, results):
        return {
            "_shards": {"failed": 0, "successful": 5, "total": 5},
            "hits": {
                "hits": [
                    {
                        "_id": "searchtests_book:" + str(result),
                        "_index": "searchtests_book",
                        "_score": 1,
                        "_type": "searchtests_book",
                        "fields": {
                            "pk": [str(result)],
                        },
                    }
                    for result in results
                ],
                "max_score": 1,
                "total": len(results),
            },
            "timed_out": False,
            "took": 2,
        }

    @mock.patch("elasticsearch.Elasticsearch.search")
    def test_basic_search(self, search):
        search.return_value = self.construct_search_response([])
        results = self.get_results()

        list(results)  # Performs search

        search.assert_any_call(
            _source=False,
            stored_fields="pk",
            index="searchtests_book",
            scroll="2m",
            size=100,
            **search_query_kwargs,
        )

    @mock.patch("elasticsearch.Elasticsearch.search")
    def test_get_single_item(self, search):
        # Need to return something to prevent index error
        search.return_value = self.construct_search_response([1])
        results = self.get_results()

        results[10]  # Performs search

        search.assert_any_call(
            from_=10,
            _source=False,
            stored_fields="pk",
            index="searchtests_book",
            size=1,
            **search_query_kwargs,
        )

    @mock.patch("elasticsearch.Elasticsearch.search")
    def test_slice_results(self, search):
        search.return_value = self.construct_search_response([])
        results = self.get_results()[1:4]

        list(results)  # Performs search

        search.assert_any_call(
            from_=1,
            _source=False,
            stored_fields="pk",
            index="searchtests_book",
            size=3,
            **search_query_kwargs,
        )

    @mock.patch("elasticsearch.Elasticsearch.search")
    def test_slice_results_multiple_times(self, search):
        search.return_value = self.construct_search_response([])
        results = self.get_results()[10:][:10]

        list(results)  # Performs search

        search.assert_any_call(
            from_=10,
            _source=False,
            stored_fields="pk",
            index="searchtests_book",
            size=10,
            **search_query_kwargs,
        )

    @mock.patch("elasticsearch.Elasticsearch.search")
    def test_slice_results_and_get_item(self, search):
        # Need to return something to prevent index error
        search.return_value = self.construct_search_response([1])
        results = self.get_results()[10:]

        results[10]  # Performs search

        search.assert_any_call(
            from_=20,
            _source=False,
            stored_fields="pk",
            index="searchtests_book",
            size=1,
            **search_query_kwargs,
        )

    @mock.patch("elasticsearch.Elasticsearch.search")
    def test_result_returned(self, search):
        search.return_value = self.construct_search_response([1])
        results = self.get_results()

        self.assertEqual(results[0], models.Book.objects.get(id=1))

    @mock.patch("elasticsearch.Elasticsearch.search")
    def test_len_1(self, search):
        search.return_value = self.construct_search_response([1])
        results = self.get_results()

        self.assertEqual(len(results), 1)

    @mock.patch("elasticsearch.Elasticsearch.search")
    def test_len_2(self, search):
        search.return_value = self.construct_search_response([1, 2])
        results = self.get_results()

        self.assertEqual(len(results), 2)

    @mock.patch("elasticsearch.Elasticsearch.search")
    def test_duplicate_results(self, search):  # Duplicates will not be removed
        search.return_value = self.construct_search_response([1, 1])
        results = list(
            self.get_results()
        )  # Must cast to list so we only create one query

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], models.Book.objects.get(id=1))
        self.assertEqual(results[1], models.Book.objects.get(id=1))

    @mock.patch("elasticsearch.Elasticsearch.search")
    def test_result_order(self, search):
        search.return_value = self.construct_search_response([1, 2, 3])
        results = list(
            self.get_results()
        )  # Must cast to list so we only create one query

        self.assertEqual(results[0], models.Book.objects.get(id=1))
        self.assertEqual(results[1], models.Book.objects.get(id=2))
        self.assertEqual(results[2], models.Book.objects.get(id=3))

    @mock.patch("elasticsearch.Elasticsearch.search")
    def test_result_order_2(self, search):
        search.return_value = self.construct_search_response([3, 2, 1])
        results = list(
            self.get_results()
        )  # Must cast to list so we only create one query

        self.assertEqual(results[0], models.Book.objects.get(id=3))
        self.assertEqual(results[1], models.Book.objects.get(id=2))
        self.assertEqual(results[2], models.Book.objects.get(id=1))


@unittest.skipIf(ELASTICSEARCH_VERSION[0] != 7, "Elasticsearch 7 required")
class TestElasticsearch7Mapping(TestCase):
    fixtures = ["search"]

    maxDiff = None

    def assertDictEqual(self, a, b):
        default = JSONSerializer().default
        self.assertEqual(
            json.dumps(a, sort_keys=True, default=default),
            json.dumps(b, sort_keys=True, default=default),
        )

    def setUp(self):
        # Create ES mapping
        self.es_mapping = Elasticsearch7SearchBackend.mapping_class(models.Book)

        # Create ES document
        self.obj = models.Book.objects.get(id=4)

    def test_get_document_type(self):
        self.assertEqual(self.es_mapping.get_document_type(), "doc")

    def test_get_mapping(self):
        # Build mapping
        mapping = self.es_mapping.get_mapping()

        # Check
        expected_result = {
            "properties": {
                "pk": {"type": "keyword", "store": True},
                "_django_content_type": {"type": "keyword"},
                "_all_text": {"type": "text"},
                "_all_text_boost_10_0": {"type": "text"},
                "_all_text_boost_2_0": {"type": "text"},
                "_edgengrams": {
                    "analyzer": "edgengram_analyzer",
                    "search_analyzer": "standard",
                    "type": "text",
                },
                "title": {
                    "type": "text",
                    "copy_to": ["_all_text", "_all_text_boost_10_0"],
                },
                "title_edgengrams": {
                    "type": "text",
                    "analyzer": "edgengram_analyzer",
                    "search_analyzer": "standard",
                },
                "title_filter": {"type": "keyword"},
                "authors": {
                    "type": "nested",
                    "properties": {
                        "name": {"type": "text", "copy_to": "_all_text"},
                        "name_edgengrams": {
                            "analyzer": "edgengram_analyzer",
                            "search_analyzer": "standard",
                            "type": "text",
                        },
                        "date_of_birth_filter": {"type": "date"},
                    },
                },
                "authors_filter": {"type": "integer"},
                "publication_date_filter": {"type": "date"},
                "summary": {
                    "copy_to": ["_all_text", "_all_text_boost_2_0"],
                    "type": "text",
                },
                "number_of_pages_filter": {"type": "integer"},
                "tags": {
                    "type": "nested",
                    "properties": {
                        "name": {"type": "text", "copy_to": "_all_text"},
                        "slug_filter": {"type": "keyword"},
                    },
                },
                "tags_filter": {"type": "integer"},
            }
        }

        self.assertDictEqual(mapping, expected_result)

    def test_get_document_id(self):
        self.assertEqual(self.es_mapping.get_document_id(self.obj), str(self.obj.pk))

    def test_get_document(self):
        # Get document
        document = self.es_mapping.get_document(self.obj)

        # Sort edgengrams
        if "_edgengrams" in document:
            document["_edgengrams"].sort()

        # Check
        expected_result = {
            "pk": "4",
            "_django_content_type": ["searchtests.Book"],
            "_edgengrams": [
                "J. R. R. Tolkien",
                "The Fellowship of the Ring",
            ],
            "title": "The Fellowship of the Ring",
            "title_edgengrams": "The Fellowship of the Ring",
            "title_filter": "The Fellowship of the Ring",
            "authors": [
                {
                    "name": "J. R. R. Tolkien",
                    "name_edgengrams": "J. R. R. Tolkien",
                    "date_of_birth_filter": datetime.date(1892, 1, 3),
                }
            ],
            "authors_filter": [2],
            "publication_date_filter": datetime.date(1954, 7, 29),
            "summary": "",
            "number_of_pages_filter": 423,
            "tags": [],
            "tags_filter": [],
        }

        self.assertDictEqual(document, expected_result)


@unittest.skipIf(ELASTICSEARCH_VERSION[0] != 7, "Elasticsearch 7 required")
class TestElasticsearch7MappingInheritance(TestCase):
    fixtures = ["search"]
    maxDiff = None

    def assertDictEqual(self, a, b):
        default = JSONSerializer().default
        self.assertEqual(
            json.dumps(a, sort_keys=True, default=default),
            json.dumps(b, sort_keys=True, default=default),
        )

    def setUp(self):
        # Create ES mapping
        self.es_mapping = Elasticsearch7SearchBackend.mapping_class(models.Novel)

        self.obj = models.Novel.objects.get(id=4)

    def test_get_document_type(self):
        self.assertEqual(self.es_mapping.get_document_type(), "doc")

    def test_get_mapping(self):
        # Build mapping
        mapping = self.es_mapping.get_mapping()

        # Check
        expected_result = {
            "properties": {
                # New
                "searchtests_novel__setting": {
                    "type": "text",
                    "copy_to": "_all_text",
                },
                "searchtests_novel__setting_edgengrams": {
                    "type": "text",
                    "analyzer": "edgengram_analyzer",
                    "search_analyzer": "standard",
                },
                "searchtests_novel__protagonist": {
                    "type": "nested",
                    "properties": {
                        "name": {
                            "type": "text",
                            "copy_to": ["_all_text", "_all_text_boost_0_5"],
                        },
                        "novel_id_filter": {"type": "integer"},
                    },
                },
                "searchtests_novel__protagonist_id_filter": {"type": "integer"},
                "searchtests_novel__characters": {
                    "type": "nested",
                    "properties": {
                        "name": {
                            "type": "text",
                            "copy_to": ["_all_text", "_all_text_boost_0_25"],
                        },
                    },
                },
                # Inherited
                "pk": {"type": "keyword", "store": True},
                "_django_content_type": {"type": "keyword"},
                "_all_text": {"type": "text"},
                "_all_text_boost_0_25": {"type": "text"},
                "_all_text_boost_0_5": {"type": "text"},
                "_all_text_boost_10_0": {"type": "text"},
                "_all_text_boost_2_0": {"type": "text"},
                "_edgengrams": {
                    "analyzer": "edgengram_analyzer",
                    "search_analyzer": "standard",
                    "type": "text",
                },
                "title": {
                    "type": "text",
                    "copy_to": ["_all_text", "_all_text_boost_10_0"],
                },
                "title_edgengrams": {
                    "type": "text",
                    "analyzer": "edgengram_analyzer",
                    "search_analyzer": "standard",
                },
                "title_filter": {"type": "keyword"},
                "authors": {
                    "type": "nested",
                    "properties": {
                        "name": {"type": "text", "copy_to": "_all_text"},
                        "name_edgengrams": {
                            "analyzer": "edgengram_analyzer",
                            "search_analyzer": "standard",
                            "type": "text",
                        },
                        "date_of_birth_filter": {"type": "date"},
                    },
                },
                "authors_filter": {"type": "integer"},
                "publication_date_filter": {"type": "date"},
                "number_of_pages_filter": {"type": "integer"},
                "summary": {
                    "copy_to": ["_all_text", "_all_text_boost_2_0"],
                    "type": "text",
                },
                "tags": {
                    "type": "nested",
                    "properties": {
                        "name": {"type": "text", "copy_to": "_all_text"},
                        "slug_filter": {"type": "keyword"},
                    },
                },
                "tags_filter": {"type": "integer"},
            }
        }

        self.assertDictEqual(mapping, expected_result)

    def test_get_document_id(self):
        # This must be tests_searchtest instead of 'tests_searchtest_tests_searchtestchild'
        # as it uses the contents base content type name.
        # This prevents the same object being accidentally indexed twice.
        self.assertEqual(self.es_mapping.get_document_id(self.obj), str(self.obj.pk))

    def test_get_document(self):
        # Build document
        document = self.es_mapping.get_document(self.obj)

        # Sort edgengrams
        if "_edgengrams" in document:
            document["_edgengrams"].sort()

        # Sort characters
        if "searchtests_novel__characters" in document:
            document["searchtests_novel__characters"].sort(key=lambda c: c["name"])

        # Check
        expected_result = {
            # New
            "searchtests_novel__setting": "Middle Earth",
            "searchtests_novel__setting_edgengrams": "Middle Earth",
            "searchtests_novel__protagonist": {
                "name": "Frodo Baggins",
                "novel_id_filter": 4,
            },
            "searchtests_novel__protagonist_id_filter": 8,
            "searchtests_novel__characters": [
                {"name": "Bilbo Baggins"},
                {"name": "Frodo Baggins"},
                {"name": "Gandalf"},
            ],
            # Changed
            "_django_content_type": ["searchtests.Novel", "searchtests.Book"],
            "_edgengrams": [
                "J. R. R. Tolkien",
                "Middle Earth",
                "The Fellowship of the Ring",
            ],
            # Inherited
            "pk": "4",
            "title": "The Fellowship of the Ring",
            "title_edgengrams": "The Fellowship of the Ring",
            "title_filter": "The Fellowship of the Ring",
            "authors": [
                {
                    "name": "J. R. R. Tolkien",
                    "name_edgengrams": "J. R. R. Tolkien",
                    "date_of_birth_filter": datetime.date(1892, 1, 3),
                }
            ],
            "authors_filter": [2],
            "publication_date_filter": datetime.date(1954, 7, 29),
            "number_of_pages_filter": 423,
            "summary": "",
            "tags": [],
            "tags_filter": [],
        }

        self.assertDictEqual(document, expected_result)


@unittest.skipIf(ELASTICSEARCH_VERSION[0] != 7, "Elasticsearch 7 required")
@mock.patch("modelsearch.backends.elasticsearch7.Elasticsearch7SearchBackend.client_class")
class TestBackendConfiguration(TestCase):
    def test_default_settings(self, Elasticsearch):
        Elasticsearch7SearchBackend(params={})

        Elasticsearch.assert_called_with(
            hosts=[
                {
                    "host": "localhost",
                    "port": 9200,
                    "url_prefix": "",
                    "use_ssl": False,
                    "verify_certs": False,
                    "http_auth": None,
                }
            ],
            timeout=10,
        )

    def test_hosts(self, Elasticsearch):
        Elasticsearch7SearchBackend(
            params={
                "HOSTS": [
                    {
                        "host": "127.0.0.1",
                        "port": 9300,
                        "use_ssl": True,
                        "verify_certs": True,
                    }
                ]
            }
        )

        Elasticsearch.assert_called_with(
            hosts=[
                {
                    "host": "127.0.0.1",
                    "port": 9300,
                    "use_ssl": True,
                    "verify_certs": True,
                }
            ],
            timeout=10,
        )

    def test_urls(self, Elasticsearch):
        # This test backwards compatibility with old URLS setting
        Elasticsearch7SearchBackend(
            params={
                "URLS": [
                    "http://localhost:12345",
                    "https://127.0.0.1:54321",
                    "http://username:password@elasticsearch.mysite.com",
                    "https://elasticsearch.mysite.com/hello",
                ],
            }
        )

        Elasticsearch.assert_called_with(
            hosts=[
                {
                    "host": "localhost",
                    "port": 12345,
                    "url_prefix": "",
                    "use_ssl": False,
                    "verify_certs": False,
                    "http_auth": None,
                },
                {
                    "host": "127.0.0.1",
                    "port": 54321,
                    "url_prefix": "",
                    "use_ssl": True,
                    "verify_certs": True,
                    "http_auth": None,
                },
                {
                    "host": "elasticsearch.mysite.com",
                    "port": 80,
                    "url_prefix": "",
                    "use_ssl": False,
                    "verify_certs": False,
                    "http_auth": ("username", "password"),
                },
                {
                    "host": "elasticsearch.mysite.com",
                    "port": 443,
                    "url_prefix": "/hello",
                    "use_ssl": True,
                    "verify_certs": True,
                    "http_auth": None,
                },
            ],
            timeout=10,
        )
