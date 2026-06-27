#!/bin/bash
  
# turn on bash's job control
set -m
  
# Start the primary process and put it in the background
gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 8 --timeout 0 web_project.wsgi:application --log-syslog &

envsubst '\$PORT' < /etc/nginx/sites-available/hive_nginx > /etc/nginx/sites-enabled/hive_nginx
# Start the helper process
nginx -g 'daemon off;'
  
# the my_helper_process might need to know how to wait on the
# primary process to start before it does its work and returns
  
  
# now we bring the primary process back into the foreground
# and leave it there
fg %1