# Generated by Django 5.1.7 on 2025-03-24 17:18

import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import modelsearch.index


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        (
            "taggit",
            "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("date_of_birth", models.DateField(null=True)),
            ],
            bases=(modelsearch.index.Indexed, models.Model),
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("summary", models.TextField(blank=True)),
                ("publication_date", models.DateField()),
                ("number_of_pages", models.IntegerField()),
                (
                    "authors",
                    models.ManyToManyField(
                        related_name="books", to="searchtests.author"
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            bases=(modelsearch.index.Indexed, models.Model),
        ),
        migrations.CreateModel(
            name="Character",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="ProgrammingGuide",
            fields=[
                (
                    "book_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="searchtests.book",
                    ),
                ),
                (
                    "programming_language",
                    models.CharField(
                        choices=[
                            ("py", "Python"),
                            ("js", "JavaScript"),
                            ("rs", "Rust"),
                        ],
                        max_length=255,
                    ),
                ),
            ],
            bases=("searchtests.book",),
        ),
        migrations.CreateModel(
            name="UnindexedBook",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("publication_date", models.DateField()),
                ("number_of_pages", models.IntegerField()),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            bases=(modelsearch.index.Indexed, models.Model),
        ),
        migrations.CreateModel(
            name="Novel",
            fields=[
                (
                    "book_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="searchtests.book",
                    ),
                ),
                ("setting", models.CharField(max_length=255)),
                (
                    "protagonist",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="searchtests.character",
                    ),
                ),
            ],
            bases=("searchtests.book",),
        ),
        migrations.AddField(
            model_name="character",
            name="novel",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="characters",
                to="searchtests.novel",
            ),
        ),
    ]
