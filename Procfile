release: python manage.py migrate
release: python manage.py loaddata team_data.json
web: gunicorn pesBotApi.wsgi --log-file -
