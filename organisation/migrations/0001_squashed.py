# Generated by Django 4.0.8 on 2023-01-06 20:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import parler.fields
import parler.models


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("organisation", "0001_initial"),
        ("organisation", "0002_auto_20151013_1220"),
        ("organisation", "0003_auto_20160704_1158"),
        ("organisation", "0004_function_users"),
        ("organisation", "0005_remove_function_user"),
        ("organisation", "0002_alter_function_options_remove_function_active_and_more"),
        ("organisation", "0003_alter_functiontranslation_master"),
    ]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Function",
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
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                (
                    "users",
                    models.ManyToManyField(
                        blank=True,
                        related_name="functions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["email"],
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="FunctionTranslation",
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
                (
                    "language_code",
                    models.CharField(
                        db_index=True, max_length=15, verbose_name="Language"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name of the ressort. E.g. Event Management",
                        max_length=64,
                        verbose_name="[TR] Name",
                    ),
                ),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="organisation.function",
                    ),
                ),
            ],
            options={
                "verbose_name": "function Translation",
                "db_table": "organisation_function_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
