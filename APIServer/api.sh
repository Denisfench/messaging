# This shell script runs the Messaging API server.
# Is `user_type` really needed?
cd ..
export user_type="api"
export PYTHONPATH="$PWD"
export FLASK_ENV=development
FLASK_APP=APIServer.api_endpoints flask run --host=127.0.0.1 --port=8000
