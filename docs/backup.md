# Backup & Restore Guide

This guide covers backup strategies, restore procedures, and database migration for AFinCo.

## Overview

AFinCo uses [django-dbbackup](https://github.com/django-dbbackup/django-dbbackup) package for automated backup management. The system supports both MySQL (production) and SQLite (development) databases.

## Backup Storage Locations

### Container Storage
- **Location**: `/var/backups/` within Django container
- **Volume Mount**: `./backups:/var/backups` (host directory)
- **Persistence**: Backups are persisted on host machine

### File Locations

| Environment | Database File | Backup Directory |
|-------------|---------------|------------------|
| Development | `app/db.sqlite3` | `backups/` |
| Production | MySQL Container | `backups/` |
| Staging | SQLite Container | `backups/` |


## Built-in Backup Commands

### Database Backup

Create backup of database
```bash
docker-compose exec django uv run manage.py dbbackup
```

### Database Restore

Restore most recent backup
```bash
docker-compose exec django uv run manage.py dbrestore
```

### Backup Management

```bash
# List available backups
docker-compose exec django uv run manage.py listbackups

# Show backup details
docker-compose exec django uv run manage.py listbackups --detail

# Clean old backups
docker-compose exec django uv run manage.py clean_old_backups --days=30
```

## Docker volume backup and restore strategy

This is a strategy usually used on upgrading AFinCo, that consists in copying the content of docker volume to another docker volume.

##### 1. Create a docker volume backup from the current version:

In this step we need to mount the current docker volume and a target folder to a docker image. This [docker doc](https://docs.docker.com/storage/volumes/#backup-a-container) may help you.

Check the docker volume name in the docker-compose file and choose or create a new folder to save the resulting backup.

```bash
docker run --rm -v afinco_db_storage:/from -v ./backups:/to ubuntu bash -c "cd /from && tar -cvf /to/backup.tar ."
```

Check if tar file exists in the target folder and if it has valid data.

##### 2. Create a new folder to the new AFINCO version:

```bash
mkdir AFINCO_NEW && cd AFINCO_NEW
git clone https://github.com/ri1anapolis/AFINCO .
```

Remember to copy the env files to this new folder.

##### 3. Create a new docker volume and restore the backup:

Please note that the docker-compose command will auto generate a new volume if the given volume name couldn't be found. Also note tha it'll look for a volume prefixed with the folder name, so, if the folder name is `afinco` and the given volume name in the `docker-compose.yml` file is `db_storage`, the name of the resulting docker volume should be `afinco_db_storage`!

Also make sure the backup is accessible to the new location.

```bash
docker volume create afinco_db_storage_new
docker run --rm -v /path/to/backup/folder:/from -v afinco_db_storage_new:/to ubuntu -c "cd /to && tar -xvf /from/backup.tar --strip 1"
```

Remember to modify the `docker-compose.yml` file to set the new volume name.

```bash
sed -i 's/db_storage/db_storage_new/g' docker-compose.yml
```

##### 4. Run the new AFINCO version:

Rebuild the AFINCO image to avoid any problem, then, if everything is fine, the new AFINCO version should go up and run with no problems.

```bash
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up
```

**Note**: Make sure the previous version is stopped and deactivated!

#####
---
Now, the new version is running apart from the previous one, and if anything goes wrong just switch back to the existing stable version.

Once everything is fine, stable and with any problems, just get rid of the old version.
