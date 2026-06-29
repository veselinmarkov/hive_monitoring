# Docker Compose Setup Guide

This Docker Compose configuration sets up the Hivebox application with a MySQL database.

## Quick Start

### 1. Configure Environment Variables

Copy the `.env.example` file to `.env` and update the values as needed:

```bash
cp .env.example .env
```

Edit `.env` to set:
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEVELOP`: Set to `True` for development, `False` for production
- `DEBUG`: Set to `True` for development, `False` for production

### 2. Build and Start Services

Start both the application and database containers:

```bash
docker-compose up --build
```

Or run in detached mode:

```bash
docker-compose up -d --build
```

### 3. Run Database Migrations

In a new terminal, apply Django migrations:

```bash
docker-compose exec app python manage.py migrate
```

### 4. Create a Superuser (Optional)

```bash
docker-compose exec app python manage.py createsuperuser
```

### 5. Access the Application

- **API/Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Nginx**: http://localhost (port 80)

## Services

### Database (MySQL)
- **Container Name**: `hivebox_mysql`
- **Host**: `db` (internal network)
- **Port**: `3306`
- **Database**: `hivebox_db`
- **User**: `hivebox_user`
- **Password**: `hivebox_password` (change in production)
- **Volume**: `mysql_data` (persistent storage)

### Application (Django)
- **Container Name**: `hivebox_app`
- **Ports**: 
  - `8000` (uWSGI)
  - `80` (Nginx)
- **Health Check**: Waits for MySQL to be healthy before starting
- **Volumes**: 
  - Application source code (development hot-reload)
  - Static files volume

## Useful Commands

### View logs
```bash
docker-compose logs -f app
docker-compose logs -f db
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (clean slate)
```bash
docker-compose down -v
```

### Run management commands
```bash
docker-compose exec app python manage.py <command>
```

### Access database shell
```bash
docker-compose exec db mysql -u hivebox_user -p hivebox_db
```

## Environment Variables

The following environment variables are configured in the compose file:

- `DATABASE_URL`: Connection string for MySQL (format: `mysql://user:password@host:port/database`)
- `SECRET_KEY`: Django secret key
- `DEVELOP`: Development mode flag
- `DEBUG`: Debug mode flag
- `PYTHONUNBUFFERED`: Python output buffering flag

## Production Considerations

Before deploying to production:

1. Change all default passwords in the MySQL service
2. Generate a strong `SECRET_KEY`
3. Set `DEVELOP=False` and `DEBUG=False`
4. Use a volume or external database for data persistence
5. Configure proper backup strategies for the MySQL database
6. Use environment-specific `.env` files
7. Consider using docker secrets for sensitive data
8. Set up proper logging and monitoring

## Network

Services communicate via the `hivebox_network` bridge network:
- App connects to database using hostname: `db`
- All containers are on the same network for inter-service communication

## Troubleshooting

### Database connection refused
- Ensure the `db` service is healthy: `docker-compose ps`
- Check database logs: `docker-compose logs db`
- Wait a moment for MySQL to fully initialize (check healthcheck)

### Permission denied on volumes
- Ensure proper file permissions: `chmod +x run_nginx_and_gunicorn.sh`

### Port already in use
- Change port mappings in `docker-compose.yml`
- Example: `"8001:8000"` to use port 8001 instead

### Static files not loading
- Collect static files: `docker-compose exec app python manage.py collectstatic --noinput`
