# Copyright 2025 Dagim Genene
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# migrate.py
import os
import importlib
from models import *
import peewee

# Track applied migrations
class Migration(peewee.Model):
    name = peewee.CharField(unique=True)
    applied = peewee.BooleanField(default=False)
    class Meta:
        database = db

try :
    db.connect()
except peewee.OperationalError:
    pass
db.create_tables([Migration])

MIGRATIONS_FOLDER = "migrations"

for file in sorted(os.listdir(MIGRATIONS_FOLDER)):
    if file.endswith(".py") and not Migration.select().where(Migration.name == file).exists():
        module = importlib.import_module(f"migrations.{file[:-3]}")
        module.run(db, migrate_fn=lambda *args, **kwargs: None)
        Migration.create(name=file, applied=True)
        print(f"Applied {file}")
