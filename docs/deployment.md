# Deployment Guide

This guide covers production deployment, environment configuration, and infrastructure setup for AFinCo.
## Pre-requisites

Ensure your server and docker are up and running correctly


## Deployment Steps


##### 1.  Clone repository to the right location.
```bash
git clone https://github.com/ri1anapolis/AFINCO .
```

##### 2. Setup environment file. Check out [environment envs](environment.md) docs and create `env/production.env` file.
```bash
cp .env.example env/production.env
```

##### 3. Create the backups folder to be mapped into the container.
```bash
mkdir -p env backups
```

##### 4. Initialize database.
Obs.: wait full initialization before go ahead.
```bash
docker-compose -f docker-compose.yml up db
```

##### 5. Build application.
```bash
docker-compose -f docker-compose.yml build
```

##### 6. Start application.
```bash
docker-compose -f docker-compose.yml up -d
```

##### 7. If it's a new setup, you'll need to create the app super user.
```bash
docker-compose -f docker-compose.yml exec django python manage.py createsuperuser
```

##### 8. Test server response in your browser:
```bash
http://my.server:8008
```


## Post-deployment

After getting AfinCo up and running you can start working on it as a fresh instalation or may want to [restore a backup](backup.md)
