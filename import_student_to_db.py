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

from models import db, Student, GradeSection
from extract_students import MarkListProcessor
from peewee import IntegrityError

def import_students(file_path):
    processor = MarkListProcessor(file_path)
    processor.arrange_by_grade_section()
    data = processor.aranged_dictionary

    for grade_section, students in data.items():
        grade, section = grade_section.split()
        # Ensure GradeSection exists
        grade_section_obj, created = GradeSection.get_or_create(grade=grade, section=section)
        if created:
            print(f'Created new GradeSection: {grade} {section}')

        for student in students:
            if len(student) < 3:
                print(f'Skipping incomplete student data: {student}')
                continue
            
            first_name,father_name,grand_father_name=student[1].split() if len(student[1].split())==3 else (student[1].split()[0],student[1].split()[1],'')
            student = Student(
                first_name=first_name,
                father_name=father_name,   
                grandfather_name=grand_father_name,
                section_id=grade_section_obj,
                sex=student[2],
                age=student[3] if len(student) > 4 else int(grade) + 6
            )
            try : 
                student.save()
            except IntegrityError:
                print(f'student : {student} already exists. in grade {student.section}')
                

        print(f'Imported {len(students)} students into {grade} {section}')

if __name__ == '__main__':
    if not db.is_closed():
        db.close()
    import_students('9th mark.docx')
    db.close()