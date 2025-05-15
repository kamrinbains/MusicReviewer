#!/bin/sh
python manage.py migrate
npx @tailwindcss/cli -i ./static/src/styles.css -o ./static/dist/styles.css
python manage.py runserver 0.0.0.0:80