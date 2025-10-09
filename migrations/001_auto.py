from playhouse.migrate import SqliteMigrator, migrate
import peewee
from models import db

def run(db, migrate_fn):
    migrator = SqliteMigrator(db)
    db.create_tables([Attendance])
    db.create_tables([GradeSection])
    db.create_tables([Person])
    db.create_tables([Student])
    db.create_tables([Subject])
    db.create_tables([Teacher])
    db.create_tables([TeachingAssignment])
