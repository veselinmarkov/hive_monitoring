FROM python:3.8-alpine as base

RUN apk update && apk add --no-cache --virtual bash gcc musl-dev linux-headers jpeg-dev zlib-dev mariadb-dev libffi-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#RUN rm /usr/bin/mysql*
COPY uwsgi.ini .
COPY hivebox hivebox
COPY web_project web_project
COPY manage.py .

FROM base as test
RUN apk add --update mysql mysql-client
RUN mysqld_safe &
#RUN python manage.py test --settings=web_project.settings_test
#RUN pip freeze > newreqs.txt

FROM base as production
CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]