from tempfile import TemporaryFile
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import Http404
from django.utils.timezone import now
from datetime import timedelta

from django.db.models import Q, Avg
from .models import MediaAttachment, MediaTweet

import json

import logging
log = logging.getLogger(__name__)

# filters is a single place to control the frontend and backend for applying filters
filters = {
    'days': {
        'filterTitle': 'How many days ago',
        'filterValues': {
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            'All Time': None,
        },
        'radioName': 'days',
        'radioDirection': 'row',
        'radioToCheck': '1',
        'default': 1,
    },
    'minfollowers': {
        'filterTitle': 'Minimum user followers',
        'filterValues': {
            'None': None,
            '1K': 1000,
            '10K': 10000,
            '100K': 100000,
            '500K': 500000,
            '1M': 1000000,
        },
        'radioName': 'minfollowers',
        'radioDirection': 'row',
        'radioToCheck': 'None',
        'default': None,
    },
    'maxfollowers': {
        'filterTitle': 'Maximum user followers',
        'filterValues': {
            '1K': 1000,
            '10K': 10000,
            '100K': 100000,
            '500K': 500000,
            '1M': 1000000,
            'None': None,
        },
        'radioName': 'maxfollowers',
        'radioDirection': 'row',
        'radioToCheck': 'None',
        'default': None,
    },
    'minlikes': {
        'filterTitle': 'Minimum likes',
        'filterValues': {
            'None': None,
            '10K': 10000,
            '50K': 50000,
            '100K': 100000,
            '200K': 200000,
        },
        'radioName': 'minlikes',
        'radioDirection': 'row',
        'radioToCheck': 'None',
        'default': None,
    },
    'maxlikes': {
        'filterTitle': 'Maximum likes',
        'filterValues': {
            '10K': 10000,
            '50K': 50000,
            '100K': 100000,
            '200K': 200000,
            'None': None,
        },
        'radioName': 'maxlikes',
        'radioDirection': 'row',
        'radioToCheck': 'None',
        'default': None,
    },
    'style': {
        'filterTitle': 'Art Style',
        'filterValues': {
            'All': None,
            'mangastyle': 0,
            'lewd': 2,
        },
        'radioName': 'style',
        'radioDirection': 'column',
        'radioToCheck': 'mangastyle',
        'default': 0,
    },
}

# return the query str's value if it exists and is valid, else return the default
def get_filter_query_value(request, filter_name):
    query_value = filters[filter_name]['default']
    if query_str := request.GET.get(filter_name):
        query_value = filters[filter_name]['filterValues'].get(query_str, query_value)
    return query_value

# requires python > 3.8
def create_filtered_query_set(request):
    # Remove all tweets classified as 'Not Art' (keep unlabeled tweets though)
    tweets_query = (MediaTweet.objects
                    .filter(author__hide=False)
                    .filter(likes_count__gte=1000)
                    .annotate(avg_style=Avg('mediaattachment__style'))
                    .exclude(avg_style=1))

    # 1. Days Filter
    days = get_filter_query_value(request, 'days')
    if days is not None:
        time_filter = now() - timedelta(days=days)
        tweets_query = tweets_query.filter(created_at__gte=time_filter)

    # 2. Min Followers Filter
    min_followers = get_filter_query_value(request, 'minfollowers')
    if min_followers:
        tweets_query = tweets_query.filter(author__followers_count__gte=min_followers)

    # 3. Max Followers Filter
    max_followers = get_filter_query_value(request, 'maxfollowers')
    if max_followers:
        tweets_query = tweets_query.filter(author__followers_count__lte=max_followers)

    # 4. Min Likes Filter
    min_likes = get_filter_query_value(request, 'minlikes')
    if min_likes:
        tweets_query = tweets_query.filter(likes_count__gte=min_likes)

    # 5. Max Likes Filter
    max_likes = get_filter_query_value(request, 'maxlikes')
    if max_likes:
        tweets_query = tweets_query.filter(likes_count__lte=max_likes)

    # 6. Style Filter
    style = get_filter_query_value(request, 'style')
    if style is not None: # style can have value 0, so we can't use if style:
        if style == 0:
            tweets_query = tweets_query.filter(Q(possibly_sensitive=False) | Q(mediaattachment__style=0)).exclude(mediaattachment__style=2)
        elif style == 2:
            tweets_query = tweets_query.filter(Q(possibly_sensitive=True) | Q(mediaattachment__style=2)).exclude(mediaattachment__style=0)
    
    # 7. Sort by likes descending
    tweets_query = tweets_query.order_by('-likes_count')
    log.warning(f"QUERY: {tweets_query.query}")
    return tweets_query

def tweets(request):
    page_num = 1
    if request.GET.get('page'):
        try:
            page_num = int(request.GET.get('page'))
        except Exception as e:
            logging.debug(f"HttpRequest {request} resulted in Exception: {e}")
            raise Http404("Page not found")

    tweets_per_page = 50
    rank_inc = (page_num - 1) * tweets_per_page

    tweets_query = create_filtered_query_set(request)
    tweet_paginator = Paginator(tweets_query.all(), tweets_per_page)

    context = {
        'trending_tweets': tweet_paginator.get_page(page_num),
        'rank_increment': rank_inc, # Take page number as arg to this fn
        'num_pages': tweet_paginator.num_pages,
        'current_page': page_num,
        'filters': json.dumps(filters),
    }
    return render(request, 'trending_tweets_app/index.html', context=context)
