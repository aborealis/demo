**ℹ️ Demonstration Project**

![Demo Project](https://img.shields.io/badge/Status-Demo%20Project-blue.svg)
![Code Sample](https://img.shields.io/badge/Purpose-Code%20Sample-orange.svg)

This repository contains code to demonstrate development skills.

# Webinar and Masterclass Portal for Astrological Schools

![Python](https://img.shields.io/badge/Python-3.9-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2-green.svg)
![MariaDB](https://img.shields.io/badge/MiariaDB-11.4-orange.svg)
![Redis](https://img.shields.io/badge/Redis-7.2-red.svg)
![Celery](https://img.shields.io/badge/Celery-5.4-darkgreen.svg)

A platform for publishing and promoting astrological webinars, courses, and events with a content management system for educational organizations.

## 🚀 Key Features

### For Organizations

- **Multitenant architecture** — Superuser creates organizations and assigns managers
- **Content management** — Users create event announcements and blog posts
- **Author system** — Users can register and assign authors to publish blog posts on behalf of the organization. Posts are SEO-optimized

### For Users

- **Advanced search** — Filter events by date, category, and organization
- **Dark/Light theme** — Theme switching with saved preferences
- **Pagination** — Optimized navigation across large volumes of content

### Administration

- **Multi-level admin panel** — Separate interfaces for superadmin, organization managers, and authors
- **Content moderation** — Manage publications via the admin interface

### Integrations

- **Facebook autoposting** — Automatic publishing of new events to a Facebook group
- **Asynchronous tasks** — Background processing with Celery + Redis

## 🛠 Tech Stack

### Backend

- **Python 3.9** — Primary development language
- **Django 4.2** — Web framework
- **Django Templates** — Frontend rendering
- **Celery 5.4** — Asynchronous tasks
- **Redis 7.2** — Message broker and caching

### Frontend

- **Bootstrap 5** — CSS framework
- **JavaScript** — Interactivity
- **CSS3** — Custom styling, dark/light theme support

### Database

- **MariaDB 11.4** — Main relational database

### Deployment

- **Docker** — Containerization
- **Docker Compose** — Service orchestration
- **Nginx 1.26** — Built-in load balancer and DDoS protection

## 📦 Installation and Run

### Prerequisites

- Docker
- Docker Compose
- Facebook Graph API access (for autoposting)

### Quick Start

1. **Download the repository**

```bash
git clone https://github.com/aborealis/demo.git
cd demo/astrohub
```

2. **Configure environment variables**

```bash
nano .env
# Edit the .env file and set your passwords and Facebook group ID/FB token
```

3. **Run the application**

```bash
docker compose up -d --build
```

4. **Collect static file**

```bash
# Enter the container
docker compose exec django zsh
# Within container run:
./manage.py collectstatic
```

5. **Access the application**

- Web app: [http://localhost:8000](http://localhost:8000)
- Admin panel: [http://localhost:8000/admin](http://localhost:8000/admin)
- Default superuser

  - **login**: _demouser_
  - **password**: _demopassword_

> ⚠️ **Note**: This is a demo version with test data. Do not use demo credentials in production.

6. **Create a new superuser (if needed)**

```bash
docker-compose exec django zsh
./manage.py createsuperuser
```

> ⚠️ **Note**: Superuser can create organizations (entities) and users, associated with them. When creating a new user, assign them to the "Organization Representative" group and check the "Staff status" checkbox.

## ⚙️ Configuration

### Key settings in `.env`

```ini
# Facebook API
FB_GROUP_ID=your_group_id
FB_GROUP_TOKEN=your_token
```

### Facebook integration setup

1. Create an app in [Facebook Developers](https://developers.facebook.com/)
2. Obtain a Page Access Token with `publish_pages` permission
3. Add the token and group ID to environment variables

### Facebook token update

1. Check token expiration date:

```bash
curl -X GET "https://graph.facebook.com/debug_token?input_token={long_token}&access_token=your_group_id|your_token"
```

2. Update token
3. Save the current DB state (see below)
4. Full stop and start docker compose:

```bash
docker compose down
docker compose up -d --build
```

### Save the current DB state

1. Enter the container:

```bash
docker compose exec django zsh
```

2. Create a DB dump:

```zsh
mysqldump -h mariadb -u$MARIADB_USER -p$MARIADB_PASSWORD $MARIADB_DATABASE > database.sql
```

3. Move the dump to `astrohub/docker-setup/volumes/sqldump/`

### Restart Django inside the container

1. Enter the container:

```bash
docker compose exec django zsh
```

2. Restart the app:

```zsh
touch ~/reload.ini
```

## 🏗 Project Architecture

```
astrohub/
├── docker-setup/          # Docker setup
│   ├── django/            # Django container config
│   ├── nginx/             # Nginx container config
│   └── volumes/           # Mounted volumes
│       ├── redisdata/     # Redis cache dump
│       ├── sqldump/       # MariaDB dump
│       └── wsgi-socket/   # Django app socket for Nginx
├── README.md
└── source
    ├── check_mariadb.sh   # Startup script
    ├── blog/              # Blog app
    ├── common/            # Shared utilities
    ├── my_events/         # Events publishing app
    ├── my_profile/        # User profile management
    ├── mysite/            # Root Django project config
    ├── static/            # Static files
    │   ├── admin/         # Admin panel assets
    │   ├── img            # App images
    │   │   ├── event/     # Event images
    │   │   ├── logo/      # School logos
    │   │   ├── page/      # Static page images
    │   │   ├── post/      # Post images
    │   │   └── profile    # Author photos
    │   └── pages/         # Page-level styles and scripts
    ├── static_pages/
    │   └── templatetags   # Extra Django template tags
    └── templates          # Page templates, including pagination
        ├── blog/          # Blog templates
        ├── my_events/     # Event templates
        ├── onpage_css/    # Inline styles (for speed)
        └── page_design/   # Navigation panel and header
```

## 👥 User Roles

### 1. Superuser

- Create/manage organizations
- Assign organization managers
- Full access to all data

### 2. Organization Manager

- Create event announcements
- Manage blog authors
- Publish posts on behalf of the organization

### 3. Author

- Write blog posts for the organization
- Edit own materials

### 4. User

- View events and articles
- Use search and filters
- Switch display theme

## 🔄 Asynchronous Tasks

The system uses Celery for background processing:

- **Facebook publishing** — automatic posting of new events

Tasks run automatically upon content creation/updates.

## 🎨 Interface

### Themes

- **Light theme** — clean minimalist style
- **Dark theme** — comfortable night-time reading
- Preferences saved per user

### Responsive design

- Full mobile support
- Optimized layouts for tablets and desktops

## 🚀 Performance

- **Caching queries** with Redis
- **Pagination** for large lists
- **Static file compression**

## 📝 License

This is a commercial project. The code is distributed under a proprietary license.

## 📞 Contacts

For cooperation and technical support:

- Email: [info@integracode.systems](mailto:info@integracode.systems)
- Website: [https://integracode.systems](https://integracode.systems)
