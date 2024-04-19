#!/bin/bash
export WEBSITE_FOR_TESTING=https://newsindex.piji.com.au
export LOCAL_NEWS_WEBSITE=$WEBSITE_FOR_TESTING/local-news
export TEST_ENV=prod
. venv/bin/activate
python -m unittest discover -s tests/
deactivate
