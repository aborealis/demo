# Dockerized Django + React (Vite) — Demo

This repository is a demonstration template for a full-stack application with an asynchronous Django backend (ASGI, Celery, Redis), WebSocket support, and a frontend built with React + TypeScript (Vite).
It is intended to showcase containerization skills and environment setup for development and deployment.

The project includes:

- Nginx configuration (dev mode)
- MariaDB with SQL dumps
- Redis and Celery
- Ready-to-use devcontainers for VS Code

## 📁 Repository Structure

- **`docker-compose.yml`** — configuration for all Docker services
- **`source/backend/`** — minimal Django project (ASGI, Channels, Celery, Redis, basic settings)
- **`source/frontend/`** — React + TypeScript application built with Vite
- **`docker-setup/`** — Dockerfiles and configuration for `django`, `nginx`, `mariadb`, `redis`, `celery`, and `react`
- **`volumes/`** — volumes for gunicorn socket, Redis data, and SQL dumps

## 🏗 Architecture (dev mode)

| Component                | Description                                                        | Port     |
| ------------------------ | ------------------------------------------------------------------ | -------- |
| **Nginx**                | Handles HTTP and WebSocket, proxies to Django, serves static files | `8000`   |
| **Django (ASGI)**        | Backend API + WebSocket routing (via Nginx upstream)               | internal |
| **React (Vite)**         | Frontend dev server                                                | `8001`   |
| **Redis**                | Celery broker + WebSocket backend                                  | internal |
| **Celery worker + beat** | Asynchronous tasks                                                 | internal |

> In production, a separate Nginx configuration as a reverse proxy is expected (the dev Nginx container can be disabled).

## ⚙️ Host Requirements

- `docker` + `docker compose` (preferably in rootless mode)
- Installed `nginx` and `certbot` for SSL
- Configured `ufw` or other firewall

### Redis: enable overcommit memory

To ensure stable Redis operation, memory overcommit should be enabled:

```bash
echo 'vm.overcommit_memory = 1' | sudo tee /etc/sysctl.d/99-overcommit.conf
sudo sysctl --system
```

## 🚀 Quick Start (dev)

1. Clone the repository:

```bash
git clone https://github.com/aborealis/demo.git
cd demo/dockerization
```

2. Build and start the containers:

```bash
docker compose up -d --build
```

3. Open in your browser:

- Frontend: **[http://127.0.0.1:8001](http://127.0.0.1:8001)**
- Django API: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

## 🧩 Devcontainers (VS Code)

The repository includes ready-to-use devcontainer configurations for backend and frontend.

To open the project in a container:

1. Open the project in VS Code
2. Select: **Remote Containers → Reopen in Container**

This will provide a fully configured development environment with all dependencies and extensions installed.

## 🛠 Useful Docker Commands

List all containers:

```bash
docker compose ps -a
```

Enter a container:

```bash
docker compose exec <container> zsh
```

> _All containers except Redis use `zsh`. Redis uses `sh`._

View container logs:

```bash
docker compose logs -f <container>
```

Connect to MariaDB from the Django container:

```bash
mysql -h mariadb -u$MARIADB_USER -p$MARIADB_PASSWORD demo
```

## ✔ Summary

This project is a fully functional Docker environment example for Django ASGI + React, which can be:

- used as a development template,
- adapted for production,
- deployed on any orchestrator.
