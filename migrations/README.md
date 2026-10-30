# Schema migration note

The original project had no Alembic environment. This hackathon build uses SQLAlchemy's additive `Base.metadata.create_all()` during startup and in `python -m app.init_db`; it creates only missing tables and does not drop, migrate, or reseed existing data. Before PostgreSQL deployment, generate an Alembic baseline from the existing SQLite schema and make future changes through versioned revisions.
