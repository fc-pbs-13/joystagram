# Generated by Django 3.0.7 on 2020-07-20 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_post_likes_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='comments_count',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
