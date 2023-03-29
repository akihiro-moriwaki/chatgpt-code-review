#!/bin/sh
python /main.py --openai_api_key "$1" --github_token "$2" --github_pull_request_id "$3"
