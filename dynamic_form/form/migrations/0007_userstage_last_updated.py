# Generated by Django 4.1.4 on 2022-12-25 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("form", "0006_alter_gazemodel_gaze_x_alter_gazemodel_gaze_y"),
    ]

    operations = [
        migrations.AddField(
            model_name="userstage",
            name="last_updated",
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
