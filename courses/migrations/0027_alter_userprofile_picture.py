# Generated by Django 5.0.4 on 2024-05-06 13:11

import courses.models.user_profile
import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0026_alter_offering_name_alter_offeringtranslation_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="picture",
            field=django_resized.forms.ResizedImageField(
                blank=True,
                crop=["middle", "center"],
                force_format=None,
                help_text="Profile picture. Only available to teachers and board members. Will be center cropped and rescaled to 512x512px upon upload.",
                keep_meta=True,
                null=True,
                quality=75,
                scale=None,
                size=[512, 512],
                upload_to=courses.models.user_profile.upload_path,
            ),
        ),
    ]
