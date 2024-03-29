# Generated by Django 2.2.2 on 2019-06-27 09:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PostData', '0003_auto_20190627_0645'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='replyId',
            new_name='commented_on',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='postId',
            new_name='post',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='userId',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='commentreactions',
            old_name='userId',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='userId',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='postreactions',
            old_name='postId',
            new_name='post',
        ),
        migrations.RenameField(
            model_name='postreactions',
            old_name='likeUserId',
            new_name='user',
        ),
    ]
