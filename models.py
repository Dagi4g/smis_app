# Copyright 2025 Dagim Genene
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# 
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import peewee
from peewee import Check, SQL
from enum import Enum
from passlib.hash import pbkdf2_sha256
import datetime

# ======== DATABASE ========
db = peewee.SqliteDatabase('highschool.db')


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

class AttendanceStatusEnum(Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    HAS_PERMISSION = "Has Permission"


# ======== BASE MODEL ========
class BaseModel(peewee.Model):
    class Meta:
        database = db


# ======== GRADE + SECTION ========
class GradeSection(BaseModel):
    grade = peewee.CharField(choices=[(g.value, g.value) for g in GradeEnum])
    section = peewee.CharField(choices=[(s.value, s.value) for s in SectionEnum])

    class Meta:
        constraints = [
            SQL('UNIQUE(grade, section)')  # Prevent duplicate Grade+Section
        ]


# ======== PERSON BASE CLASS ========
class Person(BaseModel):
    first_name = peewee.CharField()
    father_name = peewee.CharField()
    grandfather_name = peewee.CharField(null=True)
    sex = peewee.CharField(choices=[(s.value, s.value) for s in SexEnum], null=True)

    @property
    def full_name(self):
        names = [self.first_name, self.father_name, self.grandfather_name]
        return " ".join(n.title() for n in names if n)


# ======== STUDENT ========
class Student(Person):
    age = peewee.IntegerField()
    section = peewee.ForeignKeyField(GradeSection, backref='students')

    class Meta:
        constraints = [
            # Ensure same student cannot exist twice in the same section
            SQL('UNIQUE(first_name, father_name, grandfather_name, section_id)')
        ]


# ======== TEACHER ========
class Teacher(Person):
    username = peewee.CharField(unique=True)
    password_hash = peewee.CharField()  # store hashed password

    # Set password (hash it)
    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    # Verify password
    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)
    
    @classmethod
    def authenticate(cls, username, password):
        try:
            teacher = cls.get(cls.username == username)
            if teacher.verify_password(password):
                return teacher
        except cls.DoesNotExist:
            pass
        return None
    
    

# ======== SUBJECT ========
class Subject(BaseModel):
    name = peewee.CharField(unique=True)


# ======== TEACHING ASSIGNMENT ========
class TeachingAssignment(BaseModel):
    teacher = peewee.ForeignKeyField(Teacher, backref='assignments')
    subject = peewee.ForeignKeyField(Subject, backref='assignments')
    grade_section = peewee.ForeignKeyField(GradeSection, backref='assignments')

    class Meta:
        constraints = [
            SQL('UNIQUE(teacher_id, subject_id, grade_section_id)')
        ]


# ======== ATTENDANCE ========
class Attendance(BaseModel):
    student = peewee.ForeignKeyField(Student, backref='attendances')
    teacher = peewee.ForeignKeyField(Teacher, backref='marked_attendances')
    date = peewee.DateField(default=datetime.date.today)
    status = peewee.CharField(choices=[(s.value, s.value) for s in AttendanceStatusEnum])

    class Meta:
        constraints = [
            SQL('UNIQUE(student_id, teacher_id, date)')
        ]


# ======== CREATE TABLES ========
db.create_tables([
    GradeSection,
    Subject,
    Teacher,
    Student,
    TeachingAssignment,
    Attendance
])
