# Generated by Django 4.1.4 on 2023-01-28 14:55

import django.db.models.deletion
import multiselectfield.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("form", "0027_rename_scene_options_brandqa_scene_options_out_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="brandqa",
            name="scene_options_in",
        ),
        migrations.RemoveField(
            model_name="brandqa",
            name="scene_options_out",
        ),
        migrations.RemoveField(
            model_name="brandqa",
            name="submit_duration",
        ),
        migrations.RemoveField(
            model_name="consistencymodel",
            name="submit_duration",
        ),
        migrations.RemoveField(
            model_name="introduction",
            name="submit_duration",
        ),
        migrations.RemoveField(
            model_name="popup",
            name="submit_duration",
        ),
        migrations.RemoveField(
            model_name="sceneqa",
            name="submit_duration",
        ),
        migrations.RemoveField(
            model_name="surveyqa",
            name="submit_duration",
        ),
        migrations.AddField(
            model_name="brandqa",
            name="submit_time",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="consistencymodel",
            name="submit_time",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="experience",
            name="exp_start",
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="gazemodel",
            name="submit_time",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="introduction",
            name="submit_time",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="popup",
            name="clear_brand",
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="popup",
            name="submit_time",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="sceneqa",
            name="submit_time",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="surveyqa",
            name="submit_time",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="video",
            name="title",
            field=models.CharField(default="s", max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="brandqa",
            name="audio_types",
            field=multiselectfield.db.fields.MultiSelectField(
                choices=[
                    (0, "Narration"),
                    (1, "Background Music"),
                    (2, "Silent"),
                    (3, "Don't Remember"),
                ],
                max_length=100,
            ),
        ),
        migrations.CreateModel(
            name="BrandDescQA",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("submit_time", models.DateTimeField(auto_now=True)),
                (
                    "brand",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="form.brand"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "video_description_option_out",
                    models.ManyToManyField(to="form.video"),
                ),
            ],
        ),
    ]