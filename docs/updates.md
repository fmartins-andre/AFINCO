# Updates & Maintenance Guide

This guide covers updating procedures, version management, and maintenance tasks for AFinCo.

## Update Strategy

AFinCo follows a **blue-green deployment** strategy for safe updates, running versions in parallel to minimize downtime and allow quick rollback if needed.

### Update Philosophy

- **Safety First**: Never update production without testing
- **Rollback Ready**: Always have a way to revert to previous version
- **Data Integrity**: Ensure backup procedures before any update
- **Zero Downtime**: Minimize service interruption during updates

## Update Procedures

### Pre-Update Checklist

Before any update, ensure you have:

- [ ] **Current backup** taken and verified
- [ ] **Update window** scheduled with stakeholders
- [ ] **Rollback plan** documented and tested
- [ ] **Testing environment** prepared

### Update via docker volume backup

In this method, a whole new implementation is setup in order to completely preserve the old one.

##### 1. Create a new instance of AFinCo

Follow the [deployment](deployment.md) documentation to create a new functional instance;

##### 2. Backup the old instance to the new one

Follow the [backup](backup.md#docker-volume-backup-and-restore-strategy) documentation to create a docker volume backup from the old instance and retore it to the new one.
