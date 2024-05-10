# Generated by Django 5.0.4 on 2024-05-06 13:11

import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0003_alter_eventcategory_options_eventcategory_position"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="image",
            field=django_resized.forms.ResizedImageField(
                blank=True,
                crop=["middle", "center"],
                force_format=None,
                help_text="Advertising image for this event. Will be center cropped and rescaled to 720x405px (16:9) upon upload.",
                keep_meta=True,
                null=True,
                quality=75,
                scale=None,
                size=[720, 405],
                upload_to="",
            ),
        ),
        migrations.AlterField(
            model_name="eventcategory",
            name="image",
            field=django_resized.forms.ResizedImageField(
                blank=True,
                crop=["middle", "center"],
                force_format=None,
                help_text="Will be center cropped and rescaled to 720x405px (16:9) upon upload.",
                keep_meta=True,
                null=True,
                quality=75,
                scale=None,
                size=[720, 405],
                upload_to="",
            ),
        ),
    ]