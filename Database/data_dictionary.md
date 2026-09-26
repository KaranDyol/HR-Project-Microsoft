# Workforce Management Platform - Data Dictionary

## 1. Overview
This data dictionary documents the schemas for the Workforce Management Platform, encompassing organizational structure, employee profiles, performance management, hiring intelligence, and O*NET standards. The dataset provides a holistic view of human resources, bridging the gap between candidate evaluation, employee lifecycle management, and skills-based performance tracking.

## 2. Entity Relationship Summary
The platform consists of several highly interconnected domains:
- **Foundation Domain:** `departments` are linked to `roles` and `jobs`. `kpis` define generic metrics, customized per role in `role_kpis`.
- **Employee Domain:** `employees` belong to departments/roles and are assigned to `projects` via `employee_projects`. They generate tasks (`employee_tasks`) and quality records (`employee_quality_records`).
- **Performance Domain:** Employee tasks, quality, and goals (`employee_goals`) feed into `employee_kpi_records` and `employee_performance_history`.
- **Hiring Domain:** `jobs` specify requirements (`job_requirements`). `candidates` apply to jobs and bring skills (`candidate_skills`), experience, and education. `interviews` provide qualitative assessment data.
- **Scoring Domain:** Candidate data is compiled into `candidate_job_scores` backed by `candidate_evidence`.
- **Standards Domain:** O*NET tables (`onet_occupations`, `onet_skills`, `onet_occupation_skills`) provide industry-standard skill taxonomies linked via standard IDs, supported by a `skill_training_catalog`.

## 3. Score Traceability
- **Employee Performance Scores:** Traced back from `employee_performance_history` -> `employee_kpi_records` -> raw operational data (`employee_tasks`, `employee_quality_records`, `employee_attendance`, `employee_goals`, `employee_feedback`).
- **Candidate Match Scores:** Traced back from `candidate_job_scores` -> `job_requirements` vs `candidate_skills` (and `candidate_evidence`), `candidate_experience`, `candidate_education`, and `interview_answers`.

---

## 4. Foundation Tables

### 4.1 departments
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| department_id | VARCHAR | Unique identifier for the department | | DEP001 | Yes | System | No |
| department_name | VARCHAR | Name of the department | | Engineering | Yes | User Input | No |
| department_description | TEXT | Description of department functions | | Software engineering and development | No | User Input | No |
| department_head_id | VARCHAR | Employee ID of the department head | | EMP032 | No | System | No |

### 4.2 roles
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| role_id | VARCHAR | Unique identifier for the role | | ROLE001 | Yes | System | No |
| role_name | VARCHAR | Name of the role | | Backend Developer | Yes | User Input | No |
| department_id | VARCHAR | Associated department ID | | DEP001 | Yes | System | No |
| role_description | TEXT | Description of the role responsibilities | | Backend API development... | No | User Input | No |
| seniority_level | VARCHAR | Seniority level of the role | Junior, Mid, Senior, Lead | Mid | Yes | User Input | No |
| minimum_experience_years | INTEGER | Minimum years of experience required | | 2 | Yes | User Input | No |

### 4.3 kpis
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| kpi_id | VARCHAR | Unique identifier for the KPI | | KPI_TASK_COMPLETION | Yes | System | Yes |
| kpi_name | VARCHAR | Name of the KPI | | Task Completion | Yes | User Input | No |
| description | TEXT | Description of what the KPI measures | | Percentage of assigned tasks completed | No | User Input | No |
| measurement_type | VARCHAR | How the KPI is measured | percentage, count, score | percentage | Yes | System | Yes |
| default_direction | VARCHAR | Desired direction of the metric | higher_is_better, lower_is_better | higher_is_better | Yes | System | Yes |
| calculation_method | VARCHAR | Formula used to calculate the KPI | | completed_tasks / assigned_tasks * 100 | Yes | System | Yes |

### 4.4 role_kpis
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| role_kpi_id | VARCHAR | Unique identifier for the Role-KPI mapping | | RKPI001 | Yes | System | No |
| role_id | VARCHAR | Foreign key to roles | | ROLE001 | Yes | System | No |
| kpi_id | VARCHAR | Foreign key to kpis | | KPI_TASK_COMPLETION | Yes | System | Yes |
| weight | DECIMAL | Weight of this KPI in overall role performance | 0.0 to 1.0 | 0.2 | Yes | System | Yes |
| target_value | DECIMAL | Target goal for the metric | | 50 | Yes | System | Yes |
| minimum_value | DECIMAL | Minimum acceptable value | | 0 | Yes | System | Yes |
| maximum_value | DECIMAL | Maximum possible value | | 100 | Yes | System | Yes |
| measurement_unit | VARCHAR | Unit of measurement | tasks, score, hours, % | tasks | Yes | System | No |
| measurement_type | VARCHAR | Measurement type | count, score, percentage | count | Yes | System | Yes |
| direction | VARCHAR | Desired direction for this specific role | higher_is_better, lower_is_better | higher_is_better | Yes | System | Yes |
| is_mandatory | BOOLEAN | Whether this KPI is mandatory for the role | true, false | true | Yes | System | Yes |
| active | BOOLEAN | Whether this mapping is currently active | true, false | true | Yes | System | No |

---

## 5. Employee Tables

### 5.1 employees
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| employee_id | VARCHAR | Unique identifier for the employee | | EMP001 | Yes | System | No |
| employee_code | VARCHAR | Human-readable employee code | | E001 | Yes | System | No |
| first_name | VARCHAR | Employee's first name | | Amit | Yes | User Input | No |
| last_name | VARCHAR | Employee's last name | | Luthra | Yes | User Input | No |
| email | VARCHAR | Employee's email address | | amit.luthra1@company.com | Yes | System | No |
| phone | VARCHAR | Contact phone number | | +91-7307038657 | No | User Input | No |
| gender | VARCHAR | Employee's gender | Male, Female, Other | Male | No | User Input | No |
| date_of_birth | DATE | Employee's date of birth | | 1996-02-22 | Yes | User Input | No |
| date_of_joining | DATE | Date the employee joined the company | | 2023-09-03 | Yes | System | Yes |
| employment_status | VARCHAR | Current status | active, terminated, leave | active | Yes | System | No |
| employment_type | VARCHAR | Type of employment | full_time, part_time, contract | full_time | Yes | System | No |
| department_id | VARCHAR | Foreign key to departments | | DEP001 | Yes | System | No |
| role_id | VARCHAR | Foreign key to roles | | ROLE001 | Yes | System | No |
| manager_id | VARCHAR | ID of the employee's manager | | EMP034 | No | System | No |
| location | VARCHAR | Primary work location | | Hyderabad | Yes | User Input | No |
| work_mode | VARCHAR | Working mode | onsite, hybrid, remote | hybrid | Yes | User Input | No |
| current_salary | INTEGER | Current annual salary | | 1242000 | Yes | System | No |
| experience_before_joining_years | INTEGER | Prior experience in years | | 3 | No | User Input | Yes |
| education_level | VARCHAR | Highest education level attained | Bachelor's, Master's, PhD | Bachelor's | Yes | User Input | Yes |
| education_field | VARCHAR | Field of study | | Computer Science | Yes | User Input | Yes |
| university | VARCHAR | Graduating university | | NSIT Delhi | No | User Input | No |
| current_level | VARCHAR | Internal job level | L1, L2, L3, L4 | L2 | Yes | System | No |
| created_at | TIMESTAMP | Record creation timestamp | | 2023-09-03T09:00:00 | Yes | System | No |
| updated_at | TIMESTAMP | Record last update timestamp | | 2026-06-30T09:00:00 | Yes | System | No |

### 5.2 projects
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| project_id | VARCHAR | Unique identifier for the project | | PRJ001 | Yes | System | No |
| project_name | VARCHAR | Name of the project | | Atlas Platform | Yes | User Input | No |
| department_id | VARCHAR | Owning department ID | | DEP001 | Yes | System | No |
| description | TEXT | Detailed description of the project | | Core backend microservices platform | No | User Input | No |
| project_type | VARCHAR | Type classification | development, maintenance, research | development | Yes | User Input | No |
| start_date | DATE | Project start date | | 2025-11-07 | Yes | User Input | No |
| end_date | DATE | Project end date | | 2026-04-18 | No | User Input | No |
| status | VARCHAR | Current project status | active, completed, on_hold | completed | Yes | System | No |
| business_priority | VARCHAR | Importance level | low, medium, high, critical | high | Yes | User Input | Yes |
| technology_stack | VARCHAR | Comma-separated list of tech used | | Python,FastAPI,PostgreSQL... | No | User Input | Yes |

### 5.3 employee_projects
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| employee_project_id | VARCHAR | Unique assignment identifier | | EP0001 | Yes | System | No |
| employee_id | VARCHAR | Foreign key to employees | | EMP001 | Yes | System | No |
| project_id | VARCHAR | Foreign key to projects | | PRJ001 | Yes | System | No |
| role_in_project | VARCHAR | Role specific to this project | coordinator, contributor, lead | coordinator | Yes | User Input | Yes |
| responsibility | TEXT | Specific responsibilities on project | | Contributing to Atlas Platform | No | User Input | No |
| allocation_percentage | INTEGER | % of time allocated to project | 1-100 | 50 | Yes | System | Yes |
| start_date | DATE | Assignment start date | | 2025-11-07 | Yes | System | No |
| end_date | DATE | Assignment end date | | 2026-04-18 | No | System | No |
| contribution_score | DECIMAL | Derived score of contribution quality | 0-100 | 81.5 | No | System | Yes |

---

## 6. Employee Performance Tables

### 6.1 employee_tasks
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| task_id | VARCHAR | Unique task identifier | | TASK00001 | Yes | System | No |
| employee_id | VARCHAR | Assigned employee ID | | EMP001 | Yes | System | Yes |
| project_id | VARCHAR | Associated project ID | | PRJ014 | Yes | System | No |
| assigned_date | DATE | Date task was assigned | | 2026-03-22 | Yes | System | No |
| due_date | DATE | Task deadline | | 2026-04-09 | Yes | User Input | Yes |
| completed_date | DATE | Actual completion date | | 2026-03-23 | No | System | Yes |
| status | VARCHAR | Task status | in_progress, completed, overdue | completed | Yes | System | Yes |
| priority | VARCHAR | Task priority | low, medium, high | high | Yes | User Input | Yes |
| estimated_hours | DECIMAL | Estimated effort in hours | | 22.0 | Yes | User Input | Yes |
| actual_hours | DECIMAL | Actual effort spent | | 22.1 | No | System | Yes |
| quality_score | DECIMAL | Score assessing task quality | 0-100 | 91.5 | No | Reviewer | Yes |
| rework_required | BOOLEAN | Whether the task needed rework | true, false | false | No | Reviewer | Yes |
| rework_count | INTEGER | Number of times rework occurred | | 0 | No | System | Yes |
| complexity | VARCHAR | Task complexity rating | low, medium, high | high | Yes | User Input | Yes |
| task_type | VARCHAR | Classification of work type | feature, bug, documentation | documentation | Yes | User Input | No |

### 6.2 employee_quality_records
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| quality_record_id | VARCHAR | Unique quality record identifier | | QR0001 | Yes | System | No |
| employee_id | VARCHAR | Employee ID being reviewed | | EMP001 | Yes | System | Yes |
| task_id | VARCHAR | Associated task ID | | TASK00001 | Yes | System | No |
| project_id | VARCHAR | Associated project ID | | PRJ014 | Yes | System | No |
| period | VARCHAR | Review period | | 2026-03 | Yes | System | Yes |
| total_items | INTEGER | Total work items evaluated | | 6 | Yes | Reviewer | Yes |
| defects | INTEGER | Total defects found | | 0 | Yes | Reviewer | Yes |
| critical_defects | INTEGER | Count of critical priority defects | | 0 | Yes | Reviewer | Yes |
| minor_defects | INTEGER | Count of minor priority defects | | 0 | Yes | Reviewer | Yes |
| rework_count | INTEGER | Rework iterations needed | | 1 | Yes | System | Yes |
| quality_rating | DECIMAL | Overall calculated quality score | 0-100 | 88.0 | Yes | System | Yes |
| reviewer_id | VARCHAR | Employee ID of the reviewer | | EMP034 | Yes | System | No |

### 6.3 employee_goals
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| goal_id | VARCHAR | Unique goal identifier | | GOAL0001 | Yes | System | No |
| employee_id | VARCHAR | Employee ID | | EMP001 | Yes | System | Yes |
| goal_title | VARCHAR | Title of the goal | | Complete 2 certifications | Yes | User Input | No |
| goal_description | TEXT | Details of the goal | | Objective: Complete 2 certifications | No | User Input | No |
| goal_category | VARCHAR | Classification of the goal | learning, project, operational | learning | Yes | User Input | No |
| start_date | DATE | Goal start date | | 2026-01-30 | Yes | User Input | No |
| due_date | DATE | Goal target deadline | | 2026-06-02 | Yes | User Input | No |
| target_value | DECIMAL | Target metric to achieve | | 2 | Yes | User Input | Yes |
| actual_value | DECIMAL | Actual achieved metric | | 1.4 | No | System | Yes |
| achievement_percentage| DECIMAL | Calculated % of goal achieved | 0-100 | 69.4 | No | System | Yes |
| weight | DECIMAL | Relative weight of this goal | 0.0-1.0 | 0.15 | Yes | User Input | Yes |
| status | VARCHAR | Current status of the goal | at_risk, on_track, completed | at_risk | Yes | System | No |
| manager_id | VARCHAR | Manager overseeing the goal | | EMP034 | Yes | System | No |

### 6.4 employee_attendance
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| attendance_id | VARCHAR | Unique record identifier | | ATT000001 | Yes | System | No |
| employee_id | VARCHAR | Employee ID | | EMP001 | Yes | System | Yes |
| date | DATE | Date of attendance | | 2026-01-01 | Yes | System | No |
| status | VARCHAR | Attendance status | present, absent, half_day, leave | present | Yes | System | Yes |
| scheduled_hours | DECIMAL | Expected working hours | | 8 | Yes | System | Yes |
| worked_hours | DECIMAL | Actual clocked hours | | 8.4 | No | System | Yes |
| leave_type | VARCHAR | Type of leave if absent | sick, casual, annual | | No | User Input | No |
| late_minutes | INTEGER | Minutes late to shift | | 0 | No | System | Yes |
| overtime_hours | DECIMAL | Hours worked beyond scheduled | | 0.4 | No | System | Yes |

### 6.5 employee_feedback
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| feedback_id | VARCHAR | Unique feedback identifier | | FB0001 | Yes | System | No |
| employee_id | VARCHAR | Employee receiving feedback | | EMP001 | Yes | System | Yes |
| reviewer_id | VARCHAR | Employee providing feedback | | EMP017 | Yes | System | No |
| reviewer_role | VARCHAR | Relationship to employee | peer, manager, subordinate | peer | Yes | System | Yes |
| period | VARCHAR | Feedback cycle period | | 2026-02 | Yes | System | Yes |
| technical_skill_rating| DECIMAL | Rating for technical skills | 1.0-5.0 | 4.3 | Yes | Reviewer | Yes |
| communication_rating | DECIMAL | Rating for communication skills | 1.0-5.0 | 4.0 | Yes | Reviewer | Yes |
| teamwork_rating | DECIMAL | Rating for teamwork | 1.0-5.0 | 4.4 | Yes | Reviewer | Yes |
| problem_solving_rating| DECIMAL | Rating for problem solving | 1.0-5.0 | 4.0 | Yes | Reviewer | Yes |
| leadership_rating | DECIMAL | Rating for leadership skills | 1.0-5.0 | 4.2 | Yes | Reviewer | Yes |
| overall_rating | DECIMAL | Composite feedback score | 1.0-5.0 | 4.2 | Yes | System | Yes |
| comment | TEXT | Qualitative feedback notes | | Strong analytical skills. | No | Reviewer | No |
| created_at | TIMESTAMP | Record creation date | | 2026-02-28T10:00:00 | Yes | System | No |

### 6.6 employee_training
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| training_id | VARCHAR | Unique training instance ID | | TR0001 | Yes | System | No |
| employee_id | VARCHAR | Employee ID taking training | | EMP001 | Yes | System | Yes |
| training_name | VARCHAR | Name of the training course | | Agile & Scrum Certification | Yes | Catalog | No |
| skill_id | VARCHAR | Associated skill ID | | SKILL_128 | Yes | Catalog | Yes |
| training_category | VARCHAR | Type of training | soft_skills, technical, certification| soft_skills | Yes | Catalog | No |
| start_date | DATE | Training start date | | 2026-02-02 | Yes | System | No |
| completion_date | DATE | Training completion date | | 2026-02-25 | No | System | No |
| completion_percentage | DECIMAL | Progress percentage | 0-100 | 100 | No | System | Yes |
| assessment_score | DECIMAL | Score achieved on final test | 0-100 | 54.7 | No | System | Yes |
| status | VARCHAR | Training status | completed, in_progress, enrolled | completed | Yes | System | Yes |
| hours_spent | DECIMAL | Total hours invested | | 49.4 | No | System | Yes |

### 6.7 employee_skills
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| employee_skill_id | VARCHAR | Unique identifier for the mapping | | ES0001 | Yes | System | No |
| employee_id | VARCHAR | Employee ID | | EMP001 | Yes | System | Yes |
| skill_id | VARCHAR | Skill ID | | SKILL_031 | Yes | System | Yes |
| proficiency_level | VARCHAR | Qualitative skill level | Beginner, Basic, Intermediate... | Advanced | Yes | Assessment | Yes |
| proficiency_score | INTEGER | Quantitative mapping of level | 0-100 | 82 | Yes | System | Yes |
| years_of_experience | INTEGER | Years applying this skill | | 1 | No | User Input | Yes |
| last_assessed_date | DATE | Date of last skill evaluation | | 2026-04-04 | Yes | System | No |
| assessment_method | VARCHAR | Method used to verify skill | peer_review, self_assessment | peer_review | Yes | System | Yes |
| evidence_source | VARCHAR | Source of the skill evidence | certification, training, project | certification| No | System | Yes |

---

## 7. KPI & Performance Tables

### 7.1 employee_kpi_records
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| record_id | VARCHAR | Unique record identifier | | REC00001 | Yes | System | No |
| employee_id | VARCHAR | Employee ID being measured | | EMP001 | Yes | System | Yes |
| role_kpi_id | VARCHAR | Mapping back to role_kpis | | RKPI001 | Yes | System | Yes |
| period_start | DATE | Start of measurement period | | 2026-01-01 | Yes | System | Yes |
| period_end | DATE | End of measurement period | | 2026-01-31 | Yes | System | Yes |
| actual_value | DECIMAL | Measured raw value | | 80.0 | Yes | System | Yes |
| target_value | DECIMAL | Goal for the period | | 50.0 | Yes | System | Yes |
| normalized_score | DECIMAL | 0-100 mapped performance score| 0-100 | 100 | Yes | System | Yes |
| data_source | VARCHAR | Subsystem providing the metric | task_completion_system | task_completion_system| Yes | System | No |
| source_record_id | VARCHAR | ID of the source aggregate | | TASKS_2026-01 | Yes | System | No |
| created_at | TIMESTAMP | Timestamp of computation | | 2026-01-31T23:59:00 | Yes | System | No |

### 7.2 employee_performance_history
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| performance_id | VARCHAR | Unique snapshot identifier | | PERF0001 | Yes | System | No |
| employee_id | VARCHAR | Employee ID | | EMP001 | Yes | System | No |
| period_start | DATE | Evaluation cycle start | | 2026-01-01 | Yes | System | No |
| period_end | DATE | Evaluation cycle end | | 2026-01-31 | Yes | System | No |
| kpi_score | DECIMAL | Aggregated KPI module score | 0-100 | 90.1 | Yes | System | Yes |
| feedback_score | DECIMAL | Aggregated 360 Feedback score| 0-100 | 0 | Yes | System | Yes |
| goal_score | DECIMAL | Aggregated Goals module score | 0-100 | 0 | Yes | System | Yes |
| skill_score | DECIMAL | Aggregated Skill mapping score| 0-100 | 93.1 | Yes | System | Yes |
| overall_score | DECIMAL | Final weighted performance score| 0-100 | 90.1 | Yes | System | No |
| previous_score | DECIMAL | Overall score from last period| 0-100 | 90.1 | No | System | Yes |
| score_change | DECIMAL | Absolute change in score | | 7.3 | No | System | No |
| trend_percentage | DECIMAL | Relative % growth/decline | | 8.1 | No | System | No |

---

## 8. Hiring Intelligence Tables

### 8.1 jobs
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| job_id | VARCHAR | Unique job requisition ID | | JOB001 | Yes | System | No |
| job_title | VARCHAR | External title for the job | | Senior Engineering Manager| Yes | User Input | No |
| department_id | VARCHAR | Hiring department | | DEP001 | Yes | System | No |
| role_id | VARCHAR | Internal role mapping | | ROLE004 | Yes | System | No |
| job_description | TEXT | Description for candidates | | Looking for a senior... | Yes | User Input | No |
| seniority_level | VARCHAR | Expected seniority level | Junior, Mid, Senior, Lead | Senior | Yes | User Input | Yes |
| employment_type | VARCHAR | Work contract type | full_time, part_time, contract | full_time | Yes | User Input | No |
| location | VARCHAR | Base location | | Hyderabad | Yes | User Input | No |
| work_mode | VARCHAR | Work arrangement | onsite, hybrid, remote | hybrid | Yes | User Input | No |
| minimum_experience_years| INTEGER | Min required experience | | 6 | Yes | User Input | Yes |
| maximum_experience_years| INTEGER | Max typical experience | | 11 | No | User Input | Yes |
| education_requirement | VARCHAR | Min degree level required | Bachelor's, Master's, PhD | Bachelor's | Yes | User Input | Yes |
| salary_min | INTEGER | Minimum salary band | | 1500000 | Yes | User Input | No |
| salary_max | INTEGER | Maximum salary band | | 3500000 | Yes | User Input | No |
| status | VARCHAR | Requisition status | open, closed, filled | filled | Yes | System | No |
| created_date | DATE | Job creation date | | 2026-04-20 | Yes | System | No |
| closing_date | DATE | Job target fill/close date | | 2026-06-08 | No | User Input | No |

### 8.2 job_requirements
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| job_requirement_id | VARCHAR | Unique requirement identifier | | JR0001 | Yes | System | No |
| job_id | VARCHAR | Foreign key to jobs | | JOB001 | Yes | System | No |
| skill_id | VARCHAR | Required O*NET/System skill ID | | SKILL_070 | Yes | User Input | Yes |
| required_proficiency | VARCHAR | Expected proficiency level | Beginner to Expert | Advanced | Yes | User Input | No |
| required_proficiency_score| INTEGER | Numeric mapped threshold | 0-100 | 80 | Yes | System | Yes |
| weight | DECIMAL | Importance of this skill | 0.0-1.0 | 0.12 | Yes | System | Yes |
| is_mandatory | BOOLEAN | If lack of skill auto-rejects| true, false | true | Yes | User Input | Yes |
| requirement_type | VARCHAR | Classification of requirement| required, preferred | required | Yes | User Input | Yes |
| minimum_years | INTEGER | Minimum years of experience | | 3 | No | User Input | Yes |
| description | TEXT | Description of the requirement| | Proficiency in Communication| No | User Input | No |

### 8.3 candidates
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| candidate_id | VARCHAR | Unique candidate identifier | | CAN001 | Yes | System | No |
| candidate_code | VARCHAR | Short code for candidate | | C001 | Yes | System | No |
| first_name | VARCHAR | Candidate's first name | | Gaurav | Yes | Candidate| No |
| last_name | VARCHAR | Candidate's last name | | Roy | Yes | Candidate| No |
| email | VARCHAR | Candidate email address | | gaurav.roy1@gmail.com | Yes | Candidate| No |
| phone | VARCHAR | Candidate phone number | | +91-8117172233 | No | Candidate| No |
| location | VARCHAR | Current residence location | | Nagpur | Yes | Candidate| No |
| total_experience_years| DECIMAL | Total aggregate experience | | 14.1 | Yes | Parser | Yes |
| highest_education | VARCHAR | Top degree level achieved | | Master's | Yes | Parser | Yes |
| education_field | VARCHAR | Primary field of study | | Marketing | Yes | Parser | Yes |
| current_role | VARCHAR | Present job title | | Marketing Executive | No | Parser | No |
| resume_file | VARCHAR | Path to resume document | | resumes/CAN001_resume.pdf| Yes | System | No |
| application_date | DATE | Date of initial application | | 2026-09-15 | Yes | System | No |
| source | VARCHAR | Source of the application | linkedin, naukri, referral | linkedin | Yes | System | No |
| status | VARCHAR | Candidate progression status | applied, screening, hired... | rejected | Yes | System | No |

### 8.4 candidate_skills
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| candidate_skill_id | VARCHAR | Unique record identifier | | CS00001 | Yes | System | No |
| candidate_id | VARCHAR | Foreign key to candidates | | CAN001 | Yes | System | Yes |
| skill_id | VARCHAR | Standardized skill ID | | SKILL_048 | Yes | Parser | Yes |
| proficiency_level | VARCHAR | Estimated level | Beginner to Expert | Advanced | Yes | System/AI| No |
| proficiency_score | INTEGER | Numeric estimation of level | 0-100 | 81 | Yes | System/AI| Yes |
| years_experience | DECIMAL | Derived years applied | | 5.3 | No | Parser | Yes |
| evidence_text | TEXT | Text proving skill presence | | Completed Computer Vision...| No | Parser | Yes |
| evidence_source | VARCHAR | Where evidence was found | assessment, interview, resume| assessment | Yes | System | Yes |
| confidence_score | DECIMAL | AI confidence in parsing | 0.0-1.0 | 0.65 | Yes | AI Engine| Yes |
| verification_status| VARCHAR | Whether human verified | unverified, verified, pending| unverified | Yes | System | No |

*(Note: candidate_experience, candidate_education, candidate_certifications, and candidate_projects follow similar standard structures capturing timeline, metadata, and extracted technologies matching skills.)*

---

## 9. Interview Tables

### 9.1 interviews
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| interview_id | VARCHAR | Unique interview session ID | | INT0001 | Yes | System | No |
| candidate_id | VARCHAR | ID of candidate interviewed | | CAN230 | Yes | System | Yes |
| job_id | VARCHAR | ID of the job applied for | | JOB029 | Yes | System | Yes |
| interview_round | INTEGER | Round number | | 1 | Yes | System | No |
| interviewer_id | VARCHAR | Employee conducting interview| | EMP085 | Yes | System | No |
| interview_date | DATE | Date interview was held | | 2026-07-20 | Yes | System | No |
| status | VARCHAR | Current state of interview | scheduled, completed, cancelled| completed | Yes | System | No |

### 9.2 interview_questions
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| question_id | VARCHAR | Unique identifier for question | | Q0001 | Yes | System | No |
| interview_id | VARCHAR | Foreign key to interviews | | INT0001 | Yes | System | No |
| skill_id | VARCHAR | Skill targeted by question | | SKILL_144 | Yes | System | Yes |
| question | TEXT | The actual question text | | How do you handle... | Yes | Interviewer| No |
| difficulty | VARCHAR | Relative difficulty | easy, medium, hard, expert | expert | Yes | System | Yes |
| question_type | VARCHAR | Category of inquiry | technical, behavioral | behavioral | Yes | System | Yes |

### 9.3 interview_answers
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| answer_id | VARCHAR | Unique identifier for answer | | A0001 | Yes | System | No |
| question_id | VARCHAR | Foreign key to questions | | Q0001 | Yes | System | No |
| candidate_id | VARCHAR | Answering candidate | | CAN230 | Yes | System | Yes |
| answer_text | TEXT | Summary or transcript of answer| | Candidate provided a... | Yes | AI/Human | No |
| technical_correctness| DECIMAL | AI/Interviewer score 1-10 | 1.0-10.0 | 8.8 | Yes | Scoring | Yes |
| conceptual_understanding| DECIMAL | AI/Interviewer score 1-10 | 1.0-10.0 | 9.1 | Yes | Scoring | Yes |
| problem_solving | DECIMAL | AI/Interviewer score 1-10 | 1.0-10.0 | 9.1 | Yes | Scoring | Yes |
| practical_reasoning| DECIMAL | AI/Interviewer score 1-10 | 1.0-10.0 | 9.9 | Yes | Scoring | Yes |
| communication | DECIMAL | AI/Interviewer score 1-10 | 1.0-10.0 | 9.7 | Yes | Scoring | Yes |
| evidence | TEXT | Specific proof cited in answer | | Demonstrated understanding...| No | System | No |
| ai_confidence | DECIMAL | AI evaluation confidence level | 0.0-1.0 | 0.77 | Yes | AI Engine| Yes |

---

## 10. Scoring & Evidence Tables

### 10.1 candidate_job_scores
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| match_id | VARCHAR | Unique snapshot of match | | MATCH0001 | Yes | System | No |
| candidate_id | VARCHAR | Candidate evaluated | | CAN001 | Yes | System | No |
| job_id | VARCHAR | Target job requisition | | JOB018 | Yes | System | No |
| required_skill_score| DECIMAL | Alignment with required skills | 0-100 | 0 | Yes | System | Yes |
| skill_proficiency_score| DECIMAL| Depth of mapped skills | 0-100 | 79.1 | Yes | System | Yes |
| experience_score | DECIMAL | Match to tenure requirements | 0-100 | 100 | Yes | System | Yes |
| project_relevance_score| DECIMAL| Relevance of past projects | 0-100 | 42.5 | Yes | System | Yes |
| interview_score | DECIMAL | Aggregated interview results | 0-100 | 48.3 | No | System | Yes |
| problem_solving_score| DECIMAL| Specialized problem solving rating| 0-100 | 43.3 | No | System | Yes |
| education_score | DECIMAL | Alignment with education needs | 0-100 | 81.8 | Yes | System | Yes |
| overall_match_score| DECIMAL | Final weighted algorithm score | 0-100 | 46.8 | Yes | System | No |
| mandatory_requirements_met| INTEGER | Count of strict filters passed | | 0 | Yes | System | Yes |
| mandatory_requirements_failed| INTEGER | Count of strict filters failed| | 3 | Yes | System | Yes |
| calculation_version| DECIMAL | Engine algorithm version | | 1.0 | Yes | System | No |
| calculated_at | TIMESTAMP | Time of computation | | 2026-09-15T12:00:00 | Yes | System | No |

---

## 11. O*NET Tables

These tables mirror the standard O*NET classification system ensuring skills, titles, and occupations map to international standards.

### 11.1 onet_occupations & onet_skills
Provides the canonical taxonomy dictionaries. `onet_occupations` maps `occupation_code` (e.g., `15-1252.00`) to standard titles (e.g., `Software Developers`). `onet_skills` maps `element_id` (e.g., `2.A.1.a`) to standard skill names (e.g., `Reading Comprehension`).

### 11.2 onet_occupation_skills
A standard relational mapping showing the importance (`scale_id=IM`) and required level (`scale_id=LV`) of a given O*NET skill (`element_id`) for a specific occupation (`occupation_code`).

---

## 12. Training Catalog

### 12.1 skill_training_catalog
| Field | Data Type | Description | Allowed Values | Example | Required | Source | Used For Calculation |
|---|---|---|---|---|---|---|---|
| training_id | VARCHAR | Unique ID of the course | | TC0001 | Yes | System | No |
| skill_id | VARCHAR | Skill being taught | | SKILL_001 | Yes | System | Yes |
| training_name | VARCHAR | Title of the training | | Practical Python Workshop | Yes | Content | No |
| description | TEXT | Description of the curriculum | | Comprehensive training... | No | Content | No |
| difficulty | VARCHAR | Level of the course | beginner, intermediate, expert| expert | Yes | Content | No |
| duration_hours | INTEGER | Expected hours to complete | | 40 | Yes | Content | No |
| provider | VARCHAR | Vendor or internal source | | Microsoft Learn | Yes | Content | No |

---

## 13. Proficiency Level Mapping

The system relies on a quantitative mapping of qualitative human assessment to standardize analytics across both employee performance and candidate hiring:
* **Beginner:** 25
* **Basic:** 40
* **Intermediate:** 60
* **Advanced:** 80
* **Expert:** 95

---

## 14. Score Calculation Formulas

### 14.1 Employee Performance Score
The `overall_score` inside `employee_performance_history` is a weighted average of individual module scores. By default, standard configurations use:
```
Overall Performance Score = 
  (KPI Score * 0.40) +
  (Goal Achievement Score * 0.30) +
  (Feedback Score (Normalized to 100) * 0.15) +
  (Skill Assessment Score * 0.15)
```
*Note: Custom weights can be adjusted at the department or role level. KPI Scores are aggregated using the `weight` column configured in `role_kpis`.*

### 14.2 Candidate Match Score
The `overall_match_score` inside `candidate_job_scores` provides an ATS ranking capability. The formula adjusts dynamically based on available data (e.g., pre-interview vs post-interview).
A typical post-interview calculation weights:
```
Overall Match Score =
  (Required Skill Match Score * 0.35) + 
  (Interview Score * 0.25) +
  (Experience & Project Relevance * 0.20) +
  (Problem Solving & Assessment Score * 0.10) +
  (Education Match * 0.10)
```
*A hard filter applies first: If `mandatory_requirements_failed > 0`, the candidate may be auto-rejected regardless of the high composite match score.*
