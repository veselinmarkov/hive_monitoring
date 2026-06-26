# ============================================================================
# Stage 1: Build React Frontend
# ============================================================================
FROM public.ecr.aws/docker/library/node:18-alpine AS react_builder

WORKDIR /app

# Copy React project files
COPY react_project/package*.json ./

# Install dependencies and bypass legacy peer dependency conflicts
RUN npm ci --only=production --legacy-peer-deps

# Copy React source code
COPY react_project/public ./public
COPY react_project/src ./src

# Ensure OpenSSL legacy provider for Node during build
ENV NODE_OPTIONS=--openssl-legacy-provider

# Build React app for production
RUN npm run build

# ============================================================================
# Stage 2: Build Python/Django Backend
# ============================================================================
FROM public.ecr.aws/docker/library/python:3.12-slim

RUN apt-get update && \
    apt-get --yes install gcc pkg-config python3-dev libmariadb-dev nginx gettext-base && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV APP_HOME /app
WORKDIR $APP_HOME

# Removes output stream buffering, allowing for more efficient logging
ENV PYTHONUNBUFFERED 1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django application code
COPY uwsgi.ini .
COPY hivebox hivebox
COPY web_project web_project
COPY manage.py .env* ./
COPY run_nginx_and_gunicorn.sh .
RUN chmod +x run_nginx_and_gunicorn.sh

# Copy built React app from stage 1
COPY --from=react_builder /app/build /var/www/hivebox

# Setup Nginx
RUN mkdir -p /var/www/hivebox
COPY hive_nginx /etc/nginx/sites-available
RUN rm /etc/nginx/sites-enabled/default

# Run tests
RUN export RUN_TEST=True && python manage.py test --settings=web_project.settings_test

# Start both Nginx and Gunicorn
CMD ./run_nginx_and_gunicorn.sh
