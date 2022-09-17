#!/bin/sh
# the separator used by aws ec2 docker-compose is a dash '-' whereas my macbook uses an underscore '_'
# using dash since I need this in production for cron jobs
docker run --rm --env-file /home/ec2-user/mangastyle/.env.prod --network mangastyle_backend mangastyle-web:latest python manage.py update_tweets all