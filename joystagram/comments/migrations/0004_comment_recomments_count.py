# Generated by Django 3.0.7 on 2020-07-22 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0003_auto_20200714_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='recomments_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
