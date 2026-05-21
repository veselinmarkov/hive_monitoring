FROM python:3.12-slim

RUN apt-get update && \
    apt-get --yes install gcc pkg-config python3-dev libmariadb-dev nginx gettext-base && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV APP_HOME /app
WORKDIR $APP_HOME

# Removes output stream buffering, allowing for more efficient logging
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY uwsgi.ini .
COPY hivebox hivebox
COPY web_project web_project
COPY manage.py .env* ./
COPY run_nginx_and_gunicorn.sh .
RUN chmod +x run_nginx_and_gunicorn.sh
RUN mkdir /var/www/hivebox
COPY hive_nginx /etc/nginx/sites-available
RUN rm /etc/nginx/sites-enabled/default

RUN export RUN_TEST=True && python manage.py test --settings=web_project.settings_test

CMD ./run_nginx_and_gunicorn.sh
