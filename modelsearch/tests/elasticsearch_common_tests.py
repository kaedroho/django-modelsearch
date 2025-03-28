from datetime import date
from io import StringIO

from django.core import management

from modelsearch.query import MATCH_ALL
from modelsearch.test.testapp import models
from modelsearch.tests.test_backends import BackendTests


class ElasticsearchCommonSearchBackendTests(BackendTests):
    def test_search_with_spaces_only(self):
        # Search for some space characters and hope it doesn't crash
        results = self.backend.search("   ", models.Book)

        # Queries are lazily evaluated, force it to run
        list(results)

        # Didn't crash, yay!

    def test_filter_with_unsupported_lookup_type(self):
        """
        Not all lookup types are supported by the Elasticsearch backends
        """
        from modelsearch.backends.base import FilterError

        with self.assertRaises(FilterError):
            list(
                self.backend.search(
                    "Hello", models.Book.objects.filter(title__iregex="h(ea)llo")
                )
            )

    def test_partial_search(self):
        results = self.backend.autocomplete("Java", models.Book)

        self.assertUnsortedListEqual(
            [r.title for r in results],
            ["JavaScript: The Definitive Guide", "JavaScript: The good parts"],
        )

    def test_disabled_partial_search(self):
        results = self.backend.search("Java", models.Book)

        self.assertUnsortedListEqual([r.title for r in results], [])

    def test_disabled_partial_search_with_whole_term(self):
        # Making sure that there isn't a different reason why the above test
        # returned no results
        results = self.backend.search("JavaScript", models.Book)

        self.assertUnsortedListEqual(
            [r.title for r in results],
            ["JavaScript: The Definitive Guide", "JavaScript: The good parts"],
        )

    def test_child_partial_search(self):
        # Note: Expands to "Westeros". Which is in a field on Novel.setting
        results = self.backend.autocomplete("Wes", models.Book)

        self.assertUnsortedListEqual(
            [r.title for r in results],
            ["A Game of Thrones", "A Storm of Swords", "A Clash of Kings"],
        )

    def test_ascii_folding(self):
        book = models.Book.objects.create(
            title="Ĥéllø", publication_date=date(2017, 10, 19), number_of_pages=1
        )

        index = self.backend.get_index_for_model(models.Book)
        index.add_item(book)
        index.refresh()

        results = self.backend.autocomplete("Hello", models.Book)

        self.assertUnsortedListEqual([r.title for r in results], ["Ĥéllø"])

    def test_query_analyser(self):
        # This is testing that fields that use edgengram_analyzer as their index analyser do not
        # have it also as their query analyser
        results = self.backend.search("JavaScript", models.Book)
        self.assertUnsortedListEqual(
            [r.title for r in results],
            ["JavaScript: The Definitive Guide", "JavaScript: The good parts"],
        )

        # Even though they both start with "Java", this should not match the "JavaScript" books
        results = self.backend.search("JavaBeans", models.Book)
        self.assertSetEqual({r.title for r in results}, set())

    def test_search_with_hyphen(self):
        """
        This tests that punctuation characters are treated the same
        way in both indexing and querying.

        See: https://github.com/wagtail/wagtail/issues/937
        """
        book = models.Book.objects.create(
            title="Harry Potter and the Half-Blood Prince",
            publication_date=date(2009, 7, 15),
            number_of_pages=607,
        )

        index = self.backend.get_index_for_model(models.Book)
        index.add_item(book)
        index.refresh()

        results = self.backend.search("Half-Blood", models.Book)
        self.assertUnsortedListEqual(
            [r.title for r in results],
            [
                "Harry Potter and the Half-Blood Prince",
            ],
        )

    def test_search_with_numeric_term(self):
        book = models.Book.objects.create(
            title="Harry Potter and the 31337 Goblets of Fire",
            publication_date=date(2009, 7, 15),
            number_of_pages=607,
        )

        index = self.backend.get_index_for_model(models.Book)
        index.add_item(book)
        index.refresh()

        results = self.backend.search("31337", models.Book)
        self.assertUnsortedListEqual(
            [r.title for r in results],
            [
                "Harry Potter and the 31337 Goblets of Fire",
            ],
        )

        results = self.backend.autocomplete("313", models.Book)
        self.assertUnsortedListEqual(
            [r.title for r in results],
            [
                "Harry Potter and the 31337 Goblets of Fire",
            ],
        )

        results = self.backend.search("31337 goblets", models.Book)
        self.assertUnsortedListEqual(
            [r.title for r in results],
            [
                "Harry Potter and the 31337 Goblets of Fire",
            ],
        )

        results = self.backend.autocomplete("31337 gob", models.Book)
        self.assertUnsortedListEqual(
            [r.title for r in results],
            [
                "Harry Potter and the 31337 Goblets of Fire",
            ],
        )

    def test_and_operator_with_single_field(self):
        # Testing for bug #1859
        results = self.backend.search(
            "JavaScript", models.Book, operator="and", fields=["title"]
        )
        self.assertUnsortedListEqual(
            [r.title for r in results],
            ["JavaScript: The Definitive Guide", "JavaScript: The good parts"],
        )

    def test_rebuild_modelsearch_index_command_schema_only(self):
        management.call_command(
            "rebuild_modelsearch_index",
            backend_name=self.backend_name,
            schema_only=True,
            stdout=StringIO(),
        )

        # This should not give any results
        results = self.backend.search(MATCH_ALL, models.Book)
        self.assertSetEqual(set(results), set())

    def test_more_than_ten_results(self):
        # #3431 reported that Elasticsearch only sends back 10 results if the results set is not sliced
        results = self.backend.search(MATCH_ALL, models.Book)

        self.assertEqual(len(results), 14)

    def test_more_than_one_hundred_results(self):
        # Tests that fetching more than 100 results uses the scroll API
        books = []
        for i in range(150):
            books.append(
                models.Book.objects.create(
                    title=f"Book {i}",
                    publication_date=date(2017, 10, 21),
                    number_of_pages=i,
                )
            )

        index = self.backend.get_index_for_model(models.Book)
        index.add_items(models.Book, books)
        index.refresh()

        results = self.backend.search(MATCH_ALL, models.Book)
        self.assertEqual(len(results), 164)

    def test_slice_more_than_one_hundred_results(self):
        books = []
        for i in range(150):
            books.append(
                models.Book.objects.create(
                    title=f"Book {i}",
                    publication_date=date(2017, 10, 21),
                    number_of_pages=i,
                )
            )

        index = self.backend.get_index_for_model(models.Book)
        index.add_items(models.Book, books)
        index.refresh()

        results = self.backend.search(MATCH_ALL, models.Book)[10:120]
        self.assertEqual(len(results), 110)

    def test_slice_to_next_page(self):
        # ES scroll API doesn't support offset. The implementation has an optimisation
        # which will skip the first page if the first result is on the second page
        books = []
        for i in range(150):
            books.append(
                models.Book.objects.create(
                    title=f"Book {i}",
                    publication_date=date(2017, 10, 21),
                    number_of_pages=i,
                )
            )

        index = self.backend.get_index_for_model(models.Book)
        index.add_items(models.Book, books)
        index.refresh()

        results = self.backend.search(MATCH_ALL, models.Book)[110:]
        self.assertEqual(len(results), 54)

    def test_cannot_filter_on_date_parts_other_than_year(self):
        # Filtering by date not supported, should throw a FilterError
        from modelsearch.backends.base import FilterError

        in_jan = models.Book.objects.filter(publication_date__month=1)
        with self.assertRaises(FilterError):
            self.backend.search(MATCH_ALL, in_jan)
