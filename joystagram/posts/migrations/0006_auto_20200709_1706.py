# Generated by Django 3.0.7 on 2020-07-09 17:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200708_0836'),
        ('posts', '0005_auto_20200709_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='owner',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='users.Profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recomment',
            name='owner',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='recomments', to='users.Profile'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post'),
        ),
        migrations.AlterField(
            model_name='recomment',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recomments', to='posts.Comment'),
        ),
    ]