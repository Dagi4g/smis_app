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

from peewee import *
from enum import Enum

# Database
db = SqliteDatabase('highschool.db')


# ======== ENUMS ========
class SexEnum(Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class GradeEnum(Enum):
    NINE = "9"
    TEN = "10"
    ELEVEN = "11"
    TWELVE = "12"

class SectionEnum(Enum):
    A = "A"
    B = "B"
    C = "C"


# ======== BASE MODEL ========
class BaseModel(Model):
    class Meta:
        database = db


# ======== GRADE + SECTION ========
class GradeSection(BaseModel):
    grade = CharField(choices=[(g.value, g.value) for g in GradeEnum])
    section = CharField(choices=[(s.value, s.value) for s in SectionEnum])

    class Meta:
        constraints = [
            SQL('UNIQUE(grade, section)')  # Prevent duplicate Grade+Section
        ]


# ======== PERSON BASE CLASS ========
class Person(BaseModel):
    first_name = CharField()
    father_name = CharField()
    grandfather_name = CharField(null=True)
    sex = CharField(choices=[(s.value, s.value) for s in SexEnum], null=True)

    @property
    def full_name(self):
        names = [self.first_name, self.father_name, self.grandfather_name]
        return " ".join(n.title() for n in names if n)


# ======== STUDENT ========
class Student(Person):
    age = IntegerField(constraints=[Check('age >= 10')])
    section = ForeignKeyField(GradeSection, backref='students')

    class Meta:
        constraints = [
            # Ensure same student cannot exist twice in the same section
            SQL('UNIQUE(first_name, father_name, grandfather_name, section_id)')
        ]


# ======== TEACHER ========
class Teacher(Person):
    user_name  = CharField(unique=True)
    
    pass  # You can add extra fields like hire_date, salary, etc.


# ======== SUBJECT ========
class Subject(BaseModel):
    name = CharField(unique=True)


# ======== TEACHING ASSIGNMENT ========
class TeachingAssignment(BaseModel):
    teacher = ForeignKeyField(Teacher, backref='assignments')
    subject = ForeignKeyField(Subject, backref='assignments')
    grade_section = ForeignKeyField(GradeSection, backref='assignments')

    class Meta:
        constraints = [
            SQL('UNIQUE(teacher_id, subject_id, grade_section_id)')
        ]


# ======== CREATE TABLES ========
db.create_tables([
    GradeSection,
    Subject,
    Teacher,
    Student,
    TeachingAssignment
])
