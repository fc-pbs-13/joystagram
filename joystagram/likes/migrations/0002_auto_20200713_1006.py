# Generated by Django 3.0.7 on 2020-07-13 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('comments', '0002_auto_20200713_1006'),
        ('likes', '0001_initial'),
        ('users', '0001_initial'),
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recommentlike',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recomment_likes', to='users.Profile'),
        ),
        migrations.AddField(
            model_name='recommentlike',
            name='recomment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='comments.ReComment'),
        ),
        migrations.AddField(
            model_name='postlike',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_likes', to='users.Profile'),
        ),
        migrations.AddField(
            model_name='postlike',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='posts.Post'),
        ),
        migrations.AddField(
            model_name='commentlike',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='comments.Comment'),
        ),
        migrations.AddField(
            model_name='commentlike',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_likes', to='users.Profile'),
        ),
        migrations.AlterUniqueTogether(
            name='recommentlike',
            unique_together={('owner', 'recomment')},
        ),
        migrations.AlterUniqueTogether(
            name='postlike',
            unique_together={('owner', 'post')},
        ),
        migrations.AlterUniqueTogether(
            name='commentlike',
            unique_together={('owner', 'comment')},
        ),
    ]