# Generated by Django 2.2.2 on 2019-06-27 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PostData', '0002_auto_20190626_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='CommentReactions',
            name='reactionType',
            field=models.CharField(choices=[('Li', 'Like'), ('Lo', 'Love'), ('Ha', 'Haha'), ('Wo', 'Wow'), ('Sa', 'Sad'), ('An', 'Angry')], max_length=2),
        ),
        migrations.AlterField(
            model_name='PostReactions',
            name='reactionType',
            field=models.CharField(choices=[('Li', 'Like'), ('Lo', 'Love'), ('Ha', 'Haha'), ('Wo', 'Wow'), ('Sa', 'Sad'), ('An', 'Angry')], max_length=2),
        ),
    ]
