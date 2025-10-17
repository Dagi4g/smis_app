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
from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, CheckConstraint,
    UniqueConstraint, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from enum import Enum
from passlib.hash import pbkdf2_sha256
import datetime

Base = declarative_base()

# ======== ENUMS ========
class SexEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class GradeEnum(str, Enum):
    NINE = "9"
    TEN = "10"
    ELEVEN = "11"
    TWELVE = "12"

class SectionEnum(str, Enum):
    A = "A"
    B = "B"
    C = "C"

class AttendanceStatusEnum(str, Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    HAS_PERMISSION = "Has Permission"

# ======== GRADE + SECTION ========
class GradeSection(Base):
    __tablename__ = "grade_section"

    id = Column(Integer, primary_key=True)
    grade = Column(String, nullable=False)
    section = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('grade', 'section', name='uix_grade_section'),
    )

    students = relationship("Student", back_populates="section")
    assignments = relationship("TeachingAssignment", back_populates="grade_section")

    def __str__(self):
        return f"{self.grade} {self.section}"
    
    def __repr__(self):
        return f"<GradeSection(grade={self.grade}, section={self.section})>"

# ======== PERSON BASE CLASS ========
class Person(Base):
    __abstract__ = True  # Not a table itself

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    father_name = Column(String, nullable=False)
    grandfather_name = Column(String, nullable=True)
    sex = Column(String, nullable=True)

    @property
    def full_name(self):
        names = [self.first_name, self.father_name, self.grandfather_name]
        return " ".join(n.title() for n in names if n)

    def __str__(self):
        return self.full_name

# ======== STUDENT ========
class Student(Person):
    __tablename__ = "student"

    age = Column(Integer, nullable=False)
    section_id = Column(Integer, ForeignKey("grade_section.id"), nullable=False)
    section = relationship("GradeSection", back_populates="students")

    attendances = relationship("Attendance", back_populates="student")

    __table_args__ = (
        UniqueConstraint('first_name', 'father_name', 'grandfather_name', 'section_id', name='uix_student_fullname_section'),
    )
    
    
    def __str__(self):
        return f"{self.full_name} - {self.section}"
    
    def __repr__(self):
        return f"<Student(full_name={self.full_name}, section={self.section})>"

# ======== TEACHER ========
class Teacher(Person):
    __tablename__ = "teacher"

    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)

    assignments = relationship("TeachingAssignment", back_populates="teacher")
    marked_attendances = relationship("Attendance", back_populates="teacher")

    __table_args__ = (
        UniqueConstraint('first_name', 'father_name', 'grandfather_name', name='uix_teacher'),
        CheckConstraint("role IN ('admin','teacher')", name='check_role')
    )

    # ---- Password methods ----

    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)


    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

    # ---- Generate system username/code ----
    
    @classmethod
    def generate_code(cls, session, role):
        last = session.query(cls).order_by(cls.id.desc()).first()
        next_id = (last.id + 1) if last else 1
        return f"STF{next_id:03d}" if role == "admin" else f"TH{next_id:05d}"

    # ---- Create teacher ----
        print(f"Dear {teacher.full_name}, your username is {username}.please change your password upon first login.")
        return teacher
    @classmethod
    def authenticate(cls, session, username, password):
        teacher = session.query(cls).filter_by(username=username).first()
        if teacher and teacher.verify_password(password):
            return teacher
        return None
    
    
    @classmethod
    def create_teacher(cls, session, **kwargs):
        user_name = cls.generate_code(session, kwargs.get('role'))
        teacher = cls(first_name=kwargs.get('first_name'),
                    father_name=kwargs.get('father_name'),
                    grandfather_name=kwargs.get('grandfather_name'),
                    sex=kwargs.get('sex'),
                    username=user_name,
                    role=kwargs.get('role'))
        teacher.set_password(kwargs.get('password'))
        session.add(teacher)
        session.commit()
        
        return teacher
    
    def __repr__(self):
        return f"<Teacher(full_name={self.full_name}, username={self.username}, role={self.role})>"
    
    def __str__(self):
        return f"{self.full_name} ({self.username})"
# ======== SUBJECT ========
class Subject(Base):
    __tablename__ = "subject"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    assignments = relationship("TeachingAssignment", back_populates="subject")

# ======== TEACHING ASSIGNMENT ========
class TeachingAssignment(Base):
    __tablename__ = "teaching_assignment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teacher.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subject.id"), nullable=False)
    grade_section_id = Column(Integer, ForeignKey("grade_section.id"), nullable=False)

    teacher = relationship("Teacher", back_populates="assignments")
    subject = relationship("Subject", back_populates="assignments")
    grade_section = relationship("GradeSection", back_populates="assignments")

    __table_args__ = (
        UniqueConstraint('teacher_id', 'subject_id', 'grade_section_id', name='uix_teacher_subject_section'),
    )

# ======== ATTENDANCE ========
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher.id"), nullable=False)
    date = Column(Date, default=datetime.date.today, nullable=False)
    status = Column(String, nullable=False)

    student = relationship("Student", back_populates="attendances")
    teacher = relationship("Teacher", back_populates="marked_attendances")

    __table_args__ = (
        UniqueConstraint('student_id', 'teacher_id', 'date', name='uix_attendance'),
    )

# ======== DATABASE SETUP ========
engine = create_engine("sqlite:///highschool.db", echo=True, future=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
