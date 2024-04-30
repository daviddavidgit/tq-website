# Generated by Django 5.0.3 on 2024-04-17 07:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0018_merge_20240321_2254"),
        ("survey", "0004_remove_surveyinstance_invitation_sent"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="offering",
            name="survey",
            field=models.ForeignKey(
                blank=True,
                help_text="If not empty, will automatically send a survey invitation to all participants in each course, as soon as the respective course is over.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="survey.survey",
            ),
        ),
        migrations.AlterField(
            model_name="voucher",
            name="sent_to",
            field=models.ForeignKey(
                blank=True,
                help_text="User that the voucher was sent to.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="voucher",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]