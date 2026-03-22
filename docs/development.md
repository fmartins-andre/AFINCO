# Development Guide

This guide covers local development setup, VSCode remote containers, and SQLite database configuration for AFinCo.

## Quick Start

### Option 1: Docker Development (Recommended)

```bash
# Clone and setup
git clone https://github.com/ri1anapolis/AFINCO
cd AFINCO
mkdir -p env
touch env/development.env

# Start with SQLite
docker-compose -f docker-compose-stagging-sqlite.yml up -d

# Create superuser
docker-compose -f docker-compose-stagging-sqlite.yml exec django uv run manage.py createsuperuser
```

Access at: `http://localhost:8008`

### Option 2: VSCode Remote Container

1. Open project in VSCode
2. Command Palette → `Remote-Containers: Reopen in Container`
3. Install dependencies and setup database:
   ```bash
   uv sync
   uv run app/manage.py makemigrations
   uv run app/manage.py migrate
   uv run app/manage.py collectstatic --noinput
   uv run app/manage.py compress --force
   uv run app/manage.py sync_roles --reset_user_permissions
   uv run app/manage.py runserver
   ```

## Prerequisites

- Docker and Docker Compose
- VSCode (optional, for remote container development)
- Python 3.9+ (for local development)
- uv package manager (recommended for Python dependencies)


##### UV Package Manager Setup

AFinCo uses `uv` as the recommended package manager for Python dependencies. `uv` is significantly faster than `pip` and provides better dependency resolution.


### Access Points

- **Web Interface**: http://localhost:8008
- **Admin Panel**: http://localhost:8008/admin/

## VSCode Remote Container Development

### Container Configuration

The dev container includes:
- **Python 3.9** with development tools
- **Node.js LTS** for frontend development
- **Docker integration**
- **Pre-installed dependencies**

### Setup Process

1. **Reopen in Container**:
   - VSCode Command Palette (`Ctrl+Shift+P`)
   - Select `Remote-Containers: Reopen in Container`

2. **Install Dependencies**:
   ```bash
   uv sync
   ```

   If you need to install packages manually:
   ```bash
   uv add package-name
   ```

   To install development dependencies:
   ```bash
   uv sync --dev
   ```

3. **Database and app Setup**:
   ```bash
   uv run app/manage.py makemigrations
   uv run app/manage.py migrate
   uv run app/manage.py collectstatic --noinput
   uv run app/manage.py compress --force
   uv run app/manage.py sync_roles --reset_user_permissions
   ```

4. **Start Development Server**:
   ```bash
   uv run app/manage.py runserver 0.0.0.0:8000
   ```


## Database Migration: MySQL to SQLite

### Using mysql2sqlite

```bash
# Export MySQL dump
mysqldump -u username -p database_name > production_data.sql

# Convert to SQLite
./mysql2sqlite production_data.sql | sqlite3 development.db

# Copy to application
cp development.db app/db.sqlite3
```

### Using Django Database Dump

```bash
# From production MySQL
docker-compose -f docker-compose.yml exec django uv run manage.py dumpdata --format=yaml > production_data.yaml

# Import to SQLite
uv run manage.py loaddata production_data.yaml
```
