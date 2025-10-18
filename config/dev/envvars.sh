# In .venv/bin/activate, add this line at the bottom:
# cd $VIRTUAL_ENV && cd .. && source config/dev/envvars.sh

export PORT="65535"
export CACHE_URL="redis://127.0.0.1:6379"
export DJANGO_RUNSERVER_HIDE_WARNING="true"
export DATABASE_URL="postgres://afromart:afromart@localhost/afromart"
export NGROK_DOMAIN="concrete-worthy-rhino.ngrok-free.app"
export TASKDATA=$(python -c 'import os; print(os.path.abspath(os.path.dirname(os.environ["VIRTUAL_ENV"])))')/.taskwarrior
