# Generated by Django 4.2.4 on 2023-08-27 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='introduction',
            name='age',
            field=models.IntegerField(default=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='introduction',
            name='gender',
            field=models.CharField(default='1', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='introduction',
            name='stream',
            field=models.CharField(default='1', max_length=100),
            preserve_default=False,
        ),
    ]
