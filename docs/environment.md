# Environment Configuration Guide

This guide provides comprehensive information about AFinCo environment variables, configuration files, and environment-specific settings.

## Overview

AFinCo uses environment variables to manage configuration across different deployment environments (development, staging, production). Environment variables are stored in files within the `env/` directory.

## Environment File Structure

```
env/
├── development.env    # Development environment settings
├── production.env     # Production environment settings
└── staging.env        # Staging environment settings (optional)
```

## Environment Variables Reference

example:

```env
SENTRY_SERVER_NAME=MyServerHostname
SECRET_KEY=5oM3-N1c&_@nD-L0ng-h45h
DJANGO_ENVIRONMENT=development
DJANGO_SECRET_KEY=myAwesomeSecretKey
DJANGO_LOG_LEVEL=WARN
AFINCO_LOG_LEVEL=INFO
AUTH_LDAP_SERVER_URI=ldap://ldapServerIpOrHostname
AUTH_LDAP_BIND_DN=cn=djangoLdapUserName,cn=Users,dc=myDomain,dc=local
AUTH_LDAP_BIND_PASSWORD=ldapUserPassword
AUTH_LDAP_USER_SEARCH_OU=cn=Users,dc=myDomain,dc=local
MYSQL_DATABASE=afincoDb
MYSQL_USER=afincoDbUser
MYSQL_PASSWORD=afincoDbUserPassword
MYSQL_ROOT_PASSWORD=afincoDbRootPassword
MYSQL_HOST=dockerDbContainerName
MYSQL_PORT=dockerDbContainerPort
REGISTER_HOST=escribaRegisterDbServerHostname
REGISTER_PORT=escribaRegisterDbPort
REGISTER_DB=escribaRegisterDb
REGISTER_USER=escribaRegisterDbUser
REGISTER_PASSWORD=escribaRegisterDbUserPassword
```

### Core Django Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_ENVIRONMENT` | Django environment mode | `development` | Yes |
| `DJANGO_SECRET_KEY` | Django secret key for cryptography | - | Yes |
| `DJANGO_LOG_LEVEL` | Django logging level | `INFO` | No |

**Logging Levels**: DEBUG < INFO < WARN < ERROR < CRITICAL

### Database Configuration


#### MySQL Configuration (Production)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MYSQL_DATABASE` | MySQL database name | - | Yes |
| `MYSQL_USER` | MySQL database user | - | Yes |
| `MYSQL_PASSWORD` | MySQL database user password | - | Yes |
| `MYSQL_ROOT_PASSWORD` | MySQL root password | - | Yes |
| `MYSQL_HOST` | MySQL database host | - | Yes |
| `MYSQL_PORT` | MySQL database port | `3306` | Yes |


#### SQLite Configuration (Development)

**Note**: When using SQLite for development, omit all `MYSQL_*` variables.

### Application Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SENTRY_SERVER_NAME` | Sentry server identifier | - | No |
| `AFINCO_LOG_LEVEL` | Application-specific logging level | `INFO` | No |
| `TZ` | Timezone setting | `America/Sao_Paulo` | No |
| `DEBUG` | Application debug mode | `True` (dev), `False` (prod) | No |
| `SECRET_KEY` | Application secret key | - | Yes |

### LDAP Authentication

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AUTH_LDAP_SERVER_URI` | LDAP server URI | - | Yes |
| `AUTH_LDAP_BIND_DN` | LDAP bind distinguished name | - | Yes |
| `AUTH_LDAP_BIND_PASSWORD` | LDAP bind password | - | Yes |
| `AUTH_LDAP_USER_SEARCH_OU` | LDAP user search organizational unit | - | Yes |

### Escriba Register Integration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REGISTER_HOST` | Escriba register database host | - | Yes |
| `REGISTER_PORT` | Escriba register database port | `5432` | Yes |
| `REGISTER_DB` | Escriba register database name | - | Yes |
| `REGISTER_USER` | Escriba register database user | - | Yes |
| `REGISTER_PASSWORD` | Escriba register database password | - | Yes |

## Security Best Practices

### Secret Management

1. **Never commit secrets to version control**
2. **Use strong, unique secrets for each environment**
3. **Rotate secrets regularly**
4. **Use different secrets for each deployment**


### Secret Generation

```bash
# Generate Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate random password
openssl rand -base64 32
```

## Troubleshooting

### Common Environment Issues

1. **Environment variables not loading**
   - Check file exists and has correct format
   - Verify Docker Compose references correct env file
   - Ensure no extra spaces or quotes in values

2. **Database connection fails**
   - Verify all MYSQL_* variables are set for production
   - Ensure SQLite variables are set for development
   - Check database host and port accessibility

3. **LDAP authentication issues**
   - Verify LDAP server URI and credentials
   - Check network connectivity to LDAP server
   - Validate user search OU configuration
