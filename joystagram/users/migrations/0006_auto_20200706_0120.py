# Generated by Django 3.0.7 on 2020-07-06 01:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20200705_0831'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='nickname',
            field=models.CharField(default='nick', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profile',
            name='img_url',
            field=models.ImageField(null=True, upload_to='profile_image'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='introduce',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
