# Generated by Django 4.1 on 2022-09-09 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0016_alter_mediatweet_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitterartist',
            name='hide',
            field=models.BooleanField(default=False),
        ),
    ]
