#!/bin/sh
# Script to setup heroku deploy.


if [[ -z "$1" ] || [ -z "$2"]]
then
    echo "Usage: heroku.sh [app] [start_script]."
    exit 1
fi

curl https://cli-assets.heroku.com/install.sh | sh
heroku login
heroku create $1
# set up heroku app as remote for this repo
heroku git:remote -a $1
heroku config:set PYTHONPATH="/app"
heroku config:set MESSAGING_HOME="/app"
echo "web: gunicorn $2:app" > Procfile
git add Procfile
echo "Enter your deploy code in .travis.yml
