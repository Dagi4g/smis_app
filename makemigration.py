# makemigrations.py
import os
import json
from models import BaseModel
import inspect

MIGRATIONS_FOLDER = "migrations"
SNAPSHOT_FILE = f"{MIGRATIONS_FOLDER}/.schema_snapshot.json"

os.makedirs(MIGRATIONS_FOLDER, exist_ok=True)
from models import *

def get_models():
    models = []
    for name, obj in inspect.getmembers(__import__("models")):
        if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel:
            fields = [f.name for f in obj._meta.sorted_fields]
            models.append({"name": obj.__name__, "fields": fields})
    return models

current_schema = get_models()

# Load previous snapshot
if os.path.exists(SNAPSHOT_FILE):
    with open(SNAPSHOT_FILE, "r") as f:
        old_schema = json.load(f)
else:
    old_schema = []

# Compare and detect new tables/fields
migrations_to_create = []

for model in current_schema:
    old_model = next((m for m in old_schema if m["name"] == model["name"]), None)
    if not old_model:
        # New table
        migrations_to_create.append({"type": "create_table", "model": model})
    else:
        # Check new fields
        new_fields = set(model["fields"]) - set(old_model["fields"])
        for field in new_fields:
            migrations_to_create.append({"type": "add_field", "model": model["name"], "field": field})

# Generate migration scripts
if migrations_to_create:
    existing_files = os.listdir(MIGRATIONS_FOLDER)
    migration_number = len(existing_files) + 1
    file_name = f"{migration_number:03d}_auto.py"
    file_path = os.path.join(MIGRATIONS_FOLDER, file_name)

    with open(file_path, "w") as f:
        f.write("from playhouse.migrate import SqliteMigrator, migrate\n")
        f.write("import peewee\n")
        f.write("from models import *\n\n")
        f.write("def run(db, migrate_fn):\n")
        f.write("    migrator = SqliteMigrator(db)\n")
        for mig in migrations_to_create:
            if mig["type"] == "create_table":
                f.write(f"    db.create_tables([{mig['model']['name']}])\n")
            elif mig["type"] == "add_field":
                f.write(f"    migrate_fn(migrator.add_column('{mig['model']}', '{mig['field']}', peewee.TextField(null=True)))\n")

    print(f"Created migration {file_name}")

# Update snapshot
with open(SNAPSHOT_FILE, "w") as f:
    json.dump(current_schema, f, indent=4)
