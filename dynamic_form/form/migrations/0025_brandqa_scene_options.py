# Generated by Django 4.1.4 on 2023-01-24 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("form", "0024_brandqa_submit_duration_popup_submit_duration_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="brandqa",
            name="scene_options",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
