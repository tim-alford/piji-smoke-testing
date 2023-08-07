#!/bin/bash
export WEBSITE_FOR_TESTING=http://10.0.2.15:3005
. venv/bin/activate
python -m unittest discover -s tests/
deactivate
