<!--
 Copyright 2025 examination8085
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 
     https://www.apache.org/licenses/LICENSE-2.0
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

# SMIS (School Management Information System) - Offline MVP

**Author:** Dagim Genene  
**License:** Apache License 2.0  

---

## Overview

This is an **offline, standalone School Management Information System (SMIS)** designed for high school teachers and administrators.  
The MVP focuses on **attendance management**, allowing teachers to mark attendance for students per section and per day using an **Ethiopian calendar UI**.

The system uses **Python, Kivy, SQLite, and Peewee** for rapid desktop development, and **Passlib** for secure password storage and authentication.

---

## Features

### Admin
- Add teachers and students to the database.
- Automatically generates **teacher usernames**.
- Securely stores passwords using **Passlib**.

### Teacher
- Login using username and password.
- View assigned sections and students.
- Mark attendance with four statuses:
  - Present
  - Absent
  - Late
  - Has Permission
- Attendance is stored in SQLite locally.

### Technical Highlights
- **Offline & Standalone:** No internet required for local usage.  
- **Database:** SQLite + Peewee ORM for efficient data storage and querying.  
- **Secure Authentication:** Teacher passwords hashed using **Passlib (PBKDF2_SHA256)**.  
- **UI:** Minimalistic and clean Kivy interface with grey, white, and watery blue theme.  
- **Ethiopian Calendar Integration:** Teachers select dates in Ethiopian calendar for attendance.

---

## Database Schema

**Tables:**
1. `Teacher` – Teacher info, username, hashed password  
2. `Student` – Student info with grade/section link  
3. `GradeSection` – Combines grade and section  
4. `Assignment` – Links teachers to grade/section  
5. `Attendance` – Stores student attendance with uniqueness constraint  

**Unique constraints:**
- Teacher usernames  
- Grade + Section combination  
- Student + Date + Section for attendance  

---

## Installation

1. Clone the repository:
```bash
git clone <repository_url>
cd smis-offline
