# Deployment Checklist: React 16 + Django + Docker

## Pre-Build Verification
- [x] React 16.14.0 + react-timeseries-charts@0.16.1 compatibility confirmed
- [x] Local build succeeds: `npm run build` (production bundle in `react_project/build/`)
- [x] package-lock.json updated with React 16 dependencies

## Docker Build & Image Creation

### Build Multi-Stage Image
```bash
cd /Users/veselinmarkov/Documents/prog/hive_monitoring
podman build -t hive_monitoring:latest .
```
Expected outcome:
- Stage 1 (react_builder): Installs React 16, builds frontend bundle to `/app/build/`
- Stage 2 (python runtime): Copies bundle into `/var/www/hivebox/`, installs Django + dependencies

### Verify Image Layers
```bash
podman images | grep hive_monitoring
```
Confirm size is reasonable (~500MB–1GB depending on Python deps).

## Container Runtime Tests

### Start MySQL + App Containers (Compose)
```bash
cd /Users/veselinmarkov/Documents/prog/hive_monitoring
docker-compose up -d
# or with podman:
podman-compose up -d
```

### Verify Containers Running
```bash
podman ps
# Expected: both 'db' (MySQL) and 'app' (Django+React) running
```

### Check App Health
```bash
# App should be accessible at localhost:8000 (or configured port)
curl -I http://localhost:8000/
# Expected: HTTP 200 or 302 (redirect)

# Check frontend assets served
curl -I http://localhost:8000/static/js/main.*.js
# Expected: HTTP 200
```

### Verify Database Connection
```bash
# Exec into app container
podman exec -it hive_monitoring_app_1 bash

# Inside container, test Django
python manage.py check
# Expected: all checks pass

# Run migrations if needed
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser
```

### Test API Endpoints
```bash
# Example: test an API endpoint
curl http://localhost:8000/api/hives/
# Should return JSON response
```

### Nginx/React SPA Routing
If using `hive_nginx` config:
- Verify nginx.conf correctly proxies:
  - `/api/*` → Django backend
  - `/` → React SPA static files
- Test SPA navigation:
  ```bash
  curl http://localhost/
  # Should serve React index.html
  ```

## Container Logging & Debugging

### View App Logs
```bash
podman logs hive_monitoring_app_1 -f
# Watch for Django startup messages and errors
```

### View Database Logs
```bash
podman logs hive_monitoring_db_1 -f
# Watch for MySQL startup and connection messages
```

### Enter Container Shell
```bash
podman exec -it hive_monitoring_app_1 bash
# Inside: check `/var/www/hivebox/`, Django settings, etc.
```

## Cleanup & Production Readiness

- [ ] Verify `docker-compose.yml` environment variables are set (DB password, Django settings, etc.)
- [ ] Confirm `DATABASE_URL` in compose matches database container hostname (`db`)
- [ ] Verify Django `settings.py` loads environment variables correctly (django-environ)
- [ ] Test with fresh data: `docker-compose down -v && docker-compose up`
- [ ] Check no hardcoded secrets in code or config files
- [ ] Review `Dockerfile` for production best practices (no `DEBUG=True`, correct user/permissions, etc.)
- [ ] Document deployment steps for team/CI/CD

## Deployment to Target Environment

- [ ] Push image to registry (e.g., Docker Hub, GCP Artifact Registry):
  ```bash
  podman tag hive_monitoring:latest myregistry/hive_monitoring:latest
  podman push myregistry/hive_monitoring:latest
  ```
- [ ] Deploy on target (GCP, AWS, K8s, VPS, etc.):
  - Set environment variables (DB credentials, Django secret key, etc.)
  - Ensure database is initialized and accessible
  - Run migrations on target if database is fresh
  - Verify logs and health endpoints

- [ ] Post-Deployment Smoke Tests
  - [ ] Frontend loads (React app renders)
  - [ ] API endpoints respond
  - [ ] Database queries work
  - [ ] User authentication works (if applicable)

---

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| `npm ci --legacy-peer-deps` fails in Dockerfile | Ensure `Dockerfile` includes `--legacy-peer-deps` in `RUN npm ci` command |
| `NODE_OPTIONS=--openssl-legacy-provider` needed | Already set in `package.json` build script and `Dockerfile` ENV |
| React frontend not served at `/` | Check nginx config or Django static files settings |
| Database connection refused | Verify `DATABASE_URL` uses correct hostname (`db` in compose) and credentials |
| Django migrations not applied | Run `python manage.py migrate` inside container before first use |

---

## Notes

- React 16.14.0 is EOL but stable. No plans to modernize frontend, so this is acceptable for deployment.
- `--legacy-peer-deps` and `NODE_OPTIONS=--openssl-legacy-provider` are pragmatic workarounds for old dependencies.
- Recommend periodic security audits (`npm audit`) to identify critical vulnerabilities.
