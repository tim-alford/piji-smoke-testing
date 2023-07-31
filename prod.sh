#!/bin/bash
export WEBSITE_FOR_TESTING=https://newsindex.piji.com.au
python -m unittest discover -s tests/
