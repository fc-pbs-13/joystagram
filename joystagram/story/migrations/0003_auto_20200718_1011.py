# Generated by Django 3.0.7 on 2020-07-18 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0002_auto_20200717_0508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
    ]
