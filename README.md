# AFinCo - Assistente Financeiro-Contábil

[![Django](https://img.shields.io/badge/Django-3.2+-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()

## 📋 About

AFinCo (Assistente Financeiro-Contábil) means "Financial-Accounting Assistant". It's a specialized web application developed to act as a bridge between cashiers and accountants, streamlining their daily workflows.

This application was specifically designed to address the unique needs of the [Property Registry Office of First District of Anápolis/GO, Brazil](https://ri1anapolis.com.br). It includes integrations with the Escriba Register software, making it highly specialized for registry office operations.

> **Note**: Initially AFINCO was named `contabil`, so you'll find several references to this name throughout the codebase.

## 🎯 Project Status

- **Current Version**: Actively maintained
- **Primary Use**: Production environment at Property Registry Office
- **Development**: Active development with Docker-based workflow
- **Database**: Supports both MySQL (production) and SQLite (development)
- **Architecture**: Django web application with nginx reverse proxy

## 🛠️ Environment Setup

### Prerequisites

- Docker and Docker Compose
- VSCode (optional, for remote container development)
- Python 3.9+ (for local development)
- uv package manager (recommended for Python dependencies)

### Environment Configuration

For detailed environment configuration, see the [Environment Configuration Guide](docs/environment.md).

Quick setup:
```bash
# Create environment file
mkdir -p env
touch env/development.env
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

| Document | Description |
|----------|-------------|
| **[Environment Configuration](docs/environment.md)** | Environment variables, configuration files, and settings |
| **[Development Guide](docs/development.md)** | Local development setup, VSCode containers, SQLite configuration |
| **[Deployment Guide](docs/deployment.md)** | Production deployment, SSL, performance optimization |
| **[Backup & Restore](docs/backup.md)** | Database backups, migration procedures, disaster recovery |
| **[Updates & Maintenance](docs/updates.md)** | Update procedures, version management, maintenance tasks |


## 🏗️ Architecture

### Services Overview

| Service | Purpose | Port |
|---------|---------|------|
| **nginx** | Reverse proxy, static files | 80/443, 8008 |
| **django** | Application server | 8008 |
| **db** | MySQL database | 3306 (production) |

### Database Options

| Environment | Database | File |
|-------------|----------|------|
| **Development** | SQLite | `app/db.sqlite3` |
| **Staging** | MySQL | MySQL container |
| **Production** | MySQL | MySQL container |

### Docker Compose Files

- **`docker-compose.yml`**: Production with MySQL
- **`docker-compose.override.yml`**: Development overrides
- **`docker-compose-stagging-sqlite.yml`**: Development with SQLite

### Development vs Production

| Setting | Development | Production |
|---------|-------------|------------|
| **Database** | SQLite | MySQL |
| **Debug Mode** | Enabled | Disabled |
| **Log Level** | INFO | ERROR |
| **Static Files** | Development server | nginx + WhiteNoise |
| **Environment File** | development.env | production.env |

## 📋 Key Features

- **LDAP Integration**: Active Directory authentication
- **Escriba Register Integration**: Seamless integration with registry software
- **Role-based Access**: Granular user permissions and roles
- **Docker Support**: Containerized deployment for consistency
- **Development Tools**: VSCode remote container support

## 📄 License

Private repository - All rights reserved to the Property Registry Office of First District of Anápolis/GO, Brazil.

---

## 🚀 Getting Started

**For New Users**: Start with the [Development Guide](docs/development.md) for local setup.

**For Deployments**: See the [Deployment Guide](docs/deployment.md) for production setup.

**Maintained By**: [André Martins](https://github.com/fmartins-andre)
