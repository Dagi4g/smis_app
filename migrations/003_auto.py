from playhouse.migrate import SqliteMigrator, migrate
import peewee
from models import db

def run(db, migrate_fn):
    migrator = SqliteMigrator(db)
    migrate_fn(migrator.add_column('Teacher', 'role', peewee.TextField(null=True)))
