# Generated by Django 2.2.2 on 2019-06-27 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PostData', '0007_auto_20190627_1020'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commentreactions',
            old_name='commentId',
            new_name='comment',
        ),
        migrations.AlterField(
            model_name='commentreactions',
            name='reactionType',
            field=models.CharField(choices=[('love', 'love'), ('like', 'like'), ('haha', 'haha'), ('wow', 'wow'), ('sad', 'sad'), ('angry', 'angry')], max_length=10),
        ),
        migrations.AlterField(
            model_name='postreactions',
            name='reactionType',
            field=models.CharField(choices=[('love', 'love'), ('like', 'like'), ('haha', 'haha'), ('wow', 'wow'), ('sad', 'sad'), ('angry', 'angry')], max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='commentreactions',
            unique_together={('comment', 'user')},
        ),
    ]
