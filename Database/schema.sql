-- ==============================================================================
-- Intelligent Workforce Management Platform — Database Schema
-- Compatible with SQLite and PostgreSQL
-- ==============================================================================

-- ==============================================================================
-- 1. Foundation & Organization Structure
-- ==============================================================================

CREATE TABLE IF NOT EXISTS departments (
    department_id VARCHAR(50) PRIMARY KEY,
    department_name VARCHAR(255) NOT NULL,
    department_description TEXT,
    department_head_id VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS roles (
    role_id VARCHAR(50) PRIMARY KEY,
    role_name VARCHAR(255) NOT NULL,
    department_id VARCHAR(50) NOT NULL REFERENCES departments(department_id),
    role_description TEXT,
    seniority_level VARCHAR(50),
    minimum_experience_years INTEGER
);

CREATE TABLE IF NOT EXISTS kpis (
    kpi_id VARCHAR(50) PRIMARY KEY,
    kpi_name VARCHAR(255) NOT NULL,
    description TEXT,
    measurement_type VARCHAR(50),
    default_direction VARCHAR(50),
    calculation_method TEXT
);

CREATE TABLE IF NOT EXISTS role_kpis (
    role_kpi_id VARCHAR(50) PRIMARY KEY,
    role_id VARCHAR(50) NOT NULL REFERENCES roles(role_id),
    kpi_id VARCHAR(50) NOT NULL REFERENCES kpis(kpi_id),
    weight NUMERIC(5, 4) NOT NULL,
    target_value NUMERIC(10, 2),
    minimum_value NUMERIC(10, 2),
    maximum_value NUMERIC(10, 2),
    measurement_unit VARCHAR(50),
    measurement_type VARCHAR(50),
    direction VARCHAR(50),
    is_mandatory BOOLEAN,
    active BOOLEAN
);

-- ==============================================================================
-- 2. Employees & Core Operations
-- ==============================================================================

CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(50) PRIMARY KEY,
    employee_code VARCHAR(50) UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    gender VARCHAR(20),
    date_of_birth DATE,
    date_of_joining DATE NOT NULL,
    employment_status VARCHAR(50),
    employment_type VARCHAR(50),
    department_id VARCHAR(50) REFERENCES departments(department_id),
    role_id VARCHAR(50) REFERENCES roles(role_id),
    manager_id VARCHAR(50) REFERENCES employees(employee_id),
    location VARCHAR(100),
    work_mode VARCHAR(50),
    current_salary NUMERIC(12, 2),
    experience_before_joining_years NUMERIC(5, 2),
    education_level VARCHAR(100),
    education_field VARCHAR(100),
    university VARCHAR(255),
    current_level VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(50) PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    department_id VARCHAR(50) REFERENCES departments(department_id),
    description TEXT,
    project_type VARCHAR(100),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50),
    business_priority VARCHAR(50),
    technology_stack TEXT
);

CREATE TABLE IF NOT EXISTS employee_projects (
    employee_project_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id),
    project_id VARCHAR(50) NOT NULL REFERENCES projects(project_id),
    role_in_project VARCHAR(100),
    responsibility TEXT,
    allocation_percentage NUMERIC(5, 2),
    start_date DATE,
    end_date DATE,
    contribution_score NUMERIC(5, 2)
);

CREATE TABLE IF NOT EXISTS employee_tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id),
    project_id VARCHAR(50) NOT NULL REFERENCES projects(project_id),
    assigned_date DATE NOT NULL,
    due_date DATE NOT NULL,
    completed_date DATE,
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(50),
    estimated_hours NUMERIC(6, 2),
    actual_hours NUMERIC(6, 2),
    quality_score NUMERIC(5, 2),
    rework_required BOOLEAN,
    rework_count INTEGER,
    complexity VARCHAR(50),
    task_type VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS employee_quality_records (
    quality_record_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id),
    task_id VARCHAR(50) REFERENCES employee_tasks(task_id),
    project_id VARCHAR(50) REFERENCES projects(project_id),
    period VARCHAR(20),
    total_items INTEGER,
    defects INTEGER,
    critical_defects INTEGER,
    minor_defects INTEGER,
    rework_count INTEGER,
    quality_rating NUMERIC(5, 2),
    reviewer_id VARCHAR(50) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS employee_goals (
    goal_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id),
    goal_title VARCHAR(255) NOT NULL,
    goal_description TEXT,
    goal_category VARCHAR(100),
    start_date DATE,
    due_date DATE,
    target_value NUMERIC(10, 2),
    actual_value NUMERIC(10, 2),
    achievement_percentage NUMERIC(6, 2),
    weight NUMERIC(5, 4),
    status VARCHAR(50),
    manager_id VARCHAR(50) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS employee_attendance (
    attendance_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id),
    date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    scheduled_hours NUMERIC(5, 2),
    worked_hours NUMERIC(5, 2),
    leave_type VARCHAR(50),
    late_minutes INTEGER,
    overtime_hours NUMERIC(5, 2)
);

CREATE TABLE IF NOT EXISTS employee_feedback (
    feedback_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id),
    reviewer_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id),
    reviewer_role VARCHAR(50),
    period VARCHAR(20),
    technical_skill_rating NUMERIC(3, 1),
    communication_rating NUMERIC(3, 1),
    teamwork_rating NUMERIC(3, 1),
    problem_solving_rating NUMERIC(3, 1),
    leadership_rating NUMERIC(3, 1),
    overall_rating NUMERIC(3, 1),
    comment TEXT,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_training (
    training_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id),
    training_name VARCHAR(255) NOT NULL,
    skill_id VARCHAR(50),
    training_category VARCHAR(100),
    start_date DATE,
    completion_date DATE,
    completion_percentage NUMERIC(5, 2),
    assessment_score NUMERIC(5, 2),
    status VARCHAR(50),
    hours_spent NUMERIC(6, 2)
);

CREATE TABLE IF NOT EXISTS employee_skills (
    employee_skill_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id),
    skill_id VARCHAR(50) NOT NULL,
    proficiency_level VARCHAR(50),
    proficiency_score NUMERIC(5, 2),
    years_of_experience NUMERIC(5, 2),
    last_assessed_date DATE,
    assessment_method VARCHAR(100),
    evidence_source VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS employee_kpi_records (
    record_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id),
    role_kpi_id VARCHAR(50) NOT NULL REFERENCES role_kpis(role_kpi_id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    actual_value NUMERIC(10, 2),
    target_value NUMERIC(10, 2),
    normalized_score NUMERIC(6, 2),
    data_source VARCHAR(100),
    source_record_id VARCHAR(100),
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_performance_history (
    performance_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    kpi_score NUMERIC(5, 2),
    feedback_score NUMERIC(5, 2),
    goal_score NUMERIC(5, 2),
    skill_score NUMERIC(5, 2),
    overall_score NUMERIC(5, 2),
    previous_score NUMERIC(5, 2),
    score_change NUMERIC(5, 2),
    trend_percentage NUMERIC(5, 2)
);

-- ==============================================================================
-- 3. Hiring & Candidate Intelligence
-- ==============================================================================

CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    job_title VARCHAR(255) NOT NULL,
    department_id VARCHAR(50) NOT NULL REFERENCES departments(department_id),
    role_id VARCHAR(50) NOT NULL REFERENCES roles(role_id),
    job_description TEXT,
    seniority_level VARCHAR(50),
    employment_type VARCHAR(50),
    location VARCHAR(100),
    work_mode VARCHAR(50),
    minimum_experience_years INTEGER,
    maximum_experience_years INTEGER,
    education_requirement VARCHAR(100),
    salary_min NUMERIC(12, 2),
    salary_max NUMERIC(12, 2),
    status VARCHAR(50),
    created_date DATE,
    closing_date DATE
);

CREATE TABLE IF NOT EXISTS job_requirements (
    job_requirement_id VARCHAR(50) PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL REFERENCES jobs(job_id),
    skill_id VARCHAR(50) NOT NULL,
    required_proficiency VARCHAR(50),
    required_proficiency_score NUMERIC(5, 2),
    weight NUMERIC(5, 4),
    is_mandatory BOOLEAN,
    requirement_type VARCHAR(50),
    minimum_years NUMERIC(4, 1),
    description TEXT
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_skill_id VARCHAR(50) PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL REFERENCES jobs(job_id),
    skill_id VARCHAR(50) NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'job_requirement'
);

CREATE TABLE IF NOT EXISTS candidates (
    candidate_id VARCHAR(50) PRIMARY KEY,
    candidate_code VARCHAR(50) UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    location VARCHAR(100),
    total_experience_years NUMERIC(4, 1),
    highest_education VARCHAR(100),
    education_field VARCHAR(100),
    current_role VARCHAR(100),
    resume_file VARCHAR(255),
    application_date DATE,
    source VARCHAR(100),
    status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS candidate_skills (
    candidate_skill_id VARCHAR(50) PRIMARY KEY,
    candidate_id VARCHAR(50) NOT NULL REFERENCES candidates(candidate_id),
    skill_id VARCHAR(50) NOT NULL,
    proficiency_level VARCHAR(50),
    proficiency_score NUMERIC(5, 2),
    years_experience NUMERIC(4, 1),
    evidence_text TEXT,
    evidence_source VARCHAR(100),
    confidence_score NUMERIC(5, 4),
    verification_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS candidate_experience (
    experience_id VARCHAR(50) PRIMARY KEY,
    candidate_id VARCHAR(50) NOT NULL REFERENCES candidates(candidate_id),
    company VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    duration_months INTEGER,
    description TEXT,
    technologies TEXT,
    responsibilities TEXT,
    domain VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS candidate_education (
    education_id VARCHAR(50) PRIMARY KEY,
    candidate_id VARCHAR(50) NOT NULL REFERENCES candidates(candidate_id),
    degree VARCHAR(100) NOT NULL,
    field VARCHAR(100) NOT NULL,
    institution VARCHAR(255) NOT NULL,
    start_year INTEGER,
    end_year INTEGER,
    grade VARCHAR(50),
    education_level VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS candidate_certifications (
    certification_id VARCHAR(50) PRIMARY KEY,
    candidate_id VARCHAR(50) NOT NULL REFERENCES candidates(candidate_id),
    certification_name VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255) NOT NULL,
    issue_date DATE,
    expiry_date DATE,
    verification_status VARCHAR(50),
    related_skill_id VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS candidate_projects (
    candidate_project_id VARCHAR(50) PRIMARY KEY,
    candidate_id VARCHAR(50) NOT NULL REFERENCES candidates(candidate_id),
    project_name VARCHAR(255) NOT NULL,
    description TEXT,
    role VARCHAR(100),
    technologies TEXT,
    domain VARCHAR(100),
    duration_months INTEGER,
    complexity VARCHAR(50),
    outcome VARCHAR(100),
    evidence_source VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS interviews (
    interview_id VARCHAR(50) PRIMARY KEY,
    candidate_id VARCHAR(50) NOT NULL REFERENCES candidates(candidate_id),
    job_id VARCHAR(50) NOT NULL REFERENCES jobs(job_id),
    interview_round INTEGER NOT NULL,
    interviewer_id VARCHAR(50) REFERENCES employees(employee_id),
    interview_date DATE,
    status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS interview_questions (
    question_id VARCHAR(50) PRIMARY KEY,
    interview_id VARCHAR(50) NOT NULL REFERENCES interviews(interview_id),
    skill_id VARCHAR(50),
    question TEXT NOT NULL,
    difficulty VARCHAR(50),
    question_type VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS interview_answers (
    answer_id VARCHAR(50) PRIMARY KEY,
    question_id VARCHAR(50) NOT NULL REFERENCES interview_questions(question_id),
    candidate_id VARCHAR(50) NOT NULL REFERENCES candidates(candidate_id),
    answer_text TEXT,
    technical_correctness NUMERIC(4, 2),
    conceptual_understanding NUMERIC(4, 2),
    problem_solving NUMERIC(4, 2),
    practical_reasoning NUMERIC(4, 2),
    communication NUMERIC(4, 2),
    evidence TEXT,
    ai_confidence NUMERIC(5, 4)
);

CREATE TABLE IF NOT EXISTS candidate_job_scores (
    match_id VARCHAR(50) PRIMARY KEY,
    candidate_id VARCHAR(50) NOT NULL REFERENCES candidates(candidate_id),
    job_id VARCHAR(50) NOT NULL REFERENCES jobs(job_id),
    required_skill_score NUMERIC(5, 2),
    skill_proficiency_score NUMERIC(5, 2),
    experience_score NUMERIC(5, 2),
    project_relevance_score NUMERIC(5, 2),
    interview_score NUMERIC(5, 2),
    problem_solving_score NUMERIC(5, 2),
    education_score NUMERIC(5, 2),
    overall_match_score NUMERIC(5, 2),
    mandatory_requirements_met INTEGER,
    mandatory_requirements_failed INTEGER,
    calculation_version VARCHAR(50),
    calculated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidate_evidence (
    evidence_id VARCHAR(50) PRIMARY KEY,
    candidate_id VARCHAR(50) NOT NULL REFERENCES candidates(candidate_id),
    job_id VARCHAR(50) REFERENCES jobs(job_id),
    skill_id VARCHAR(50),
    evidence_type VARCHAR(50),
    source_document VARCHAR(255),
    source_text TEXT,
    evidence_strength VARCHAR(50),
    confidence_score NUMERIC(5, 4),
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidate_resume_extractions (
    extraction_id VARCHAR(50) PRIMARY KEY,
    candidate_id VARCHAR(50) NOT NULL REFERENCES candidates(candidate_id),
    source_document VARCHAR(255) NOT NULL,
    extraction_json TEXT NOT NULL,
    extraction_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS skill_training_catalog (
    training_id VARCHAR(50) PRIMARY KEY,
    skill_id VARCHAR(50) NOT NULL,
    training_name VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty VARCHAR(50),
    duration_hours NUMERIC(6, 2),
    provider VARCHAR(255)
);

-- ==============================================================================
-- 4. O*NET Workforce Skill Taxonomy
-- ==============================================================================

CREATE TABLE IF NOT EXISTS onet_occupations (
    occupation_code VARCHAR(50) PRIMARY KEY,
    occupation_title VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS onet_skills (
    element_id VARCHAR(50) PRIMARY KEY,
    element_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT
);

CREATE TABLE IF NOT EXISTS onet_occupation_skills (
    occupation_code VARCHAR(50) NOT NULL REFERENCES onet_occupations(occupation_code),
    element_id VARCHAR(50) NOT NULL REFERENCES onet_skills(element_id),
    element_name VARCHAR(255),
    scale_id VARCHAR(10) NOT NULL,
    data_value NUMERIC(6, 2) NOT NULL,
    recommend_suppress VARCHAR(5),
    PRIMARY KEY (occupation_code, element_id, scale_id)
);

CREATE TABLE IF NOT EXISTS onet_knowledge (
    element_id VARCHAR(50) PRIMARY KEY,
    element_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT
);

CREATE TABLE IF NOT EXISTS onet_abilities (
    element_id VARCHAR(50) PRIMARY KEY,
    element_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT
);

CREATE TABLE IF NOT EXISTS onet_tasks (
    occupation_code VARCHAR(50) NOT NULL REFERENCES onet_occupations(occupation_code),
    task_id VARCHAR(50) PRIMARY KEY,
    task_description TEXT NOT NULL
);

-- ==============================================================================
-- 5. Performance Indexes
-- ==============================================================================

CREATE INDEX IF NOT EXISTS idx_roles_department ON roles(department_id);
CREATE INDEX IF NOT EXISTS idx_role_kpis_role ON role_kpis(role_id);
CREATE INDEX IF NOT EXISTS idx_role_kpis_kpi ON role_kpis(kpi_id);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_role ON employees(role_id);
CREATE INDEX IF NOT EXISTS idx_employees_manager ON employees(manager_id);
CREATE INDEX IF NOT EXISTS idx_projects_department ON projects(department_id);
CREATE INDEX IF NOT EXISTS idx_emp_proj_emp ON employee_projects(employee_id);
CREATE INDEX IF NOT EXISTS idx_emp_proj_proj ON employee_projects(project_id);
CREATE INDEX IF NOT EXISTS idx_emp_tasks_emp ON employee_tasks(employee_id);
CREATE INDEX IF NOT EXISTS idx_emp_tasks_proj ON employee_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_emp_tasks_status ON employee_tasks(status);
CREATE INDEX IF NOT EXISTS idx_emp_quality_emp ON employee_quality_records(employee_id);
CREATE INDEX IF NOT EXISTS idx_emp_goals_emp ON employee_goals(employee_id);
CREATE INDEX IF NOT EXISTS idx_emp_att_emp ON employee_attendance(employee_id);
CREATE INDEX IF NOT EXISTS idx_emp_att_date ON employee_attendance(date);
CREATE INDEX IF NOT EXISTS idx_emp_fb_emp ON employee_feedback(employee_id);
CREATE INDEX IF NOT EXISTS idx_emp_tr_emp ON employee_training(employee_id);
CREATE INDEX IF NOT EXISTS idx_emp_skills_emp ON employee_skills(employee_id);
CREATE INDEX IF NOT EXISTS idx_emp_kpi_rec_emp ON employee_kpi_records(employee_id);
CREATE INDEX IF NOT EXISTS idx_emp_perf_hist_emp ON employee_performance_history(employee_id);
CREATE INDEX IF NOT EXISTS idx_jobs_dept ON jobs(department_id);
CREATE INDEX IF NOT EXISTS idx_jobs_role ON jobs(role_id);
CREATE INDEX IF NOT EXISTS idx_job_req_job ON job_requirements(job_id);
CREATE INDEX IF NOT EXISTS idx_cand_skills_cand ON candidate_skills(candidate_id);
CREATE INDEX IF NOT EXISTS idx_cand_exp_cand ON candidate_experience(candidate_id);
CREATE INDEX IF NOT EXISTS idx_cand_edu_cand ON candidate_education(candidate_id);
CREATE INDEX IF NOT EXISTS idx_cand_cert_cand ON candidate_certifications(candidate_id);
CREATE INDEX IF NOT EXISTS idx_cand_proj_cand ON candidate_projects(candidate_id);
CREATE INDEX IF NOT EXISTS idx_interviews_cand ON interviews(candidate_id);
CREATE INDEX IF NOT EXISTS idx_interviews_job ON interviews(job_id);
CREATE INDEX IF NOT EXISTS idx_int_questions_int ON interview_questions(interview_id);
CREATE INDEX IF NOT EXISTS idx_int_answers_quest ON interview_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_int_answers_cand ON interview_answers(candidate_id);
CREATE INDEX IF NOT EXISTS idx_cand_scores_cand ON candidate_job_scores(candidate_id);
CREATE INDEX IF NOT EXISTS idx_cand_scores_job ON candidate_job_scores(job_id);
CREATE INDEX IF NOT EXISTS idx_cand_ev_cand ON candidate_evidence(candidate_id);
CREATE INDEX IF NOT EXISTS idx_onet_occ_skills_occ ON onet_occupation_skills(occupation_code);
