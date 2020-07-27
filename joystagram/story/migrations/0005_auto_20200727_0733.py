# Generated by Django 3.0.7 on 2020-07-27 07:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0004_story_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storycheck',
            name='story',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='story_checks', to='story.Story'),
        ),
    ]
