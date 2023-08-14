#!/bin/bash
export WEBSITE_FOR_TESTING=https://staging.d1845vy2uqwo7b.amplifyapp.com
export TEST_ENV=staging
. venv/bin/activate
python -m unittest discover -s tests/
deactivate
