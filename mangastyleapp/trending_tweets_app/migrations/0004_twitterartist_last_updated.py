# Generated by Django 4.1 on 2022-08-17 14:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trending_tweets_app', '0003_alter_mediaattachment_parent_tweet_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitterartist',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 17, 14, 29, 2, 887838, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
    ]
