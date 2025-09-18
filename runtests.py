import argparse
import os

import django

from django.core.management import call_command


def main():
    parser = argparse.ArgumentParser(
        description="Run Django tests with a specified search backend."
    )
    parser.add_argument(
        "--backend",
        required=True,
        help="Specify the search backend (db, elasticsearch7, elasticsearch8, elasticsearch9, opensearch1, opensearch2, opensearch3).",
    )

    args = parser.parse_args()

    os.environ["SEARCH_BACKEND"] = args.backend
    os.environ["DJANGO_SETTINGS_MODULE"] = "modelsearch.test.settings"

    django.setup()

    call_command("test")


if __name__ == "__main__":
    main()
