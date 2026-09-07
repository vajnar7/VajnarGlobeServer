# VajnarGlobeServer
Server for VajnarGlobe client

## Database migration

Run the migration after configuring the database connection environment variables:

```powershell
python migrate.py
```

The migration creates missing tables from the SQLAlchemy models and leaves existing tables unchanged. It uses `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`, with the same defaults as the server.
