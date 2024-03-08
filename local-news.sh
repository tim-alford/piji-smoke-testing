#!/bin/bash
export LOCAL_NEWS_WEBSITE=https://staging.d1845vy2uqwo7b.amplifyapp.com/local-news
export TEST_ENV=staging
. venv/bin/activate
python -m unittest -vvv tests/test_local_news.py
deactivate
