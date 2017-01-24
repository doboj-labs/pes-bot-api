release: python manage.py migrate
release: python loaddata team_data.json
web: gunicorn pesBotApi.wsgi --log-file -
