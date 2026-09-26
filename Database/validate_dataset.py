#!/usr/bin/env python3
"""Validate the generated dataset for integrity, volumes, and consistency."""
import csv, os
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def load_csv(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"  {label:45s} [{status}]")
    return condition

def main():
    print("=" * 60)
    print("DATASET VALIDATION")
    print("=" * 60)

    # === File Existence ===
    print("\n--- File Existence ---")
    expected = [
        "departments.csv", "roles.csv", "kpis.csv", "role_kpis.csv",
        "employees.csv", "projects.csv", "employee_projects.csv",
        "employee_tasks.csv", "employee_quality_records.csv",
        "employee_goals.csv", "employee_attendance.csv", "employee_feedback.csv",
        "employee_training.csv", "employee_skills.csv", "employee_kpi_records.csv",
        "employee_performance_history.csv", "jobs.csv", "job_requirements.csv",
        "candidates.csv", "candidate_skills.csv", "candidate_experience.csv",
        "candidate_education.csv", "candidate_certifications.csv",
        "candidate_projects.csv", "interviews.csv", "interview_questions.csv",
        "interview_answers.csv", "candidate_job_scores.csv",
        "candidate_evidence.csv", "skill_training_catalog.csv",
    ]
    onet = ["occupations.csv", "skills.csv", "occupation_skills.csv",
            "knowledge.csv", "abilities.csv", "tasks.csv"]
    missing = []
    for f in expected:
        if not os.path.exists(os.path.join(DATA_DIR, f)):
            missing.append(f)
    for f in onet:
        if not os.path.exists(os.path.join(DATA_DIR, "onet", f)):
            missing.append(f"onet/{f}")
    check("All 36 expected files present", len(missing) == 0)
    if missing:
        for m in missing:
            print(f"    MISSING: {m}")

    # === Referential Integrity ===
    print("\n--- Referential Integrity ---")
    departments = load_csv(os.path.join(DATA_DIR, "departments.csv"))
    roles = load_csv(os.path.join(DATA_DIR, "roles.csv"))
    employees = load_csv(os.path.join(DATA_DIR, "employees.csv"))
    kpis = load_csv(os.path.join(DATA_DIR, "kpis.csv"))
    role_kpis = load_csv(os.path.join(DATA_DIR, "role_kpis.csv"))
    kpi_records = load_csv(os.path.join(DATA_DIR, "employee_kpi_records.csv"))
    emp_skills = load_csv(os.path.join(DATA_DIR, "employee_skills.csv"))
    jobs = load_csv(os.path.join(DATA_DIR, "jobs.csv"))
    job_reqs = load_csv(os.path.join(DATA_DIR, "job_requirements.csv"))
    candidates = load_csv(os.path.join(DATA_DIR, "candidates.csv"))
    cand_skills = load_csv(os.path.join(DATA_DIR, "candidate_skills.csv"))
    interviews = load_csv(os.path.join(DATA_DIR, "interviews.csv"))
    int_questions = load_csv(os.path.join(DATA_DIR, "interview_questions.csv"))

    dept_ids = {d["department_id"] for d in departments}
    role_ids = {r["role_id"] for r in roles}
    emp_ids = {e["employee_id"] for e in employees}
    kpi_ids = {k["kpi_id"] for k in kpis}
    rkpi_ids = {rk["role_kpi_id"] for rk in role_kpis}
    job_ids = {j["job_id"] for j in jobs}
    cand_ids = {c["candidate_id"] for c in candidates}
    int_ids = {i["interview_id"] for i in interviews}

    check("Roles -> Departments", all(r["department_id"] in dept_ids for r in roles))
    check("Employees -> Roles", all(e["role_id"] in role_ids for e in employees))
    check("Employees -> Departments", all(e["department_id"] in dept_ids for e in employees))
    check("RoleKPIs -> Roles", all(rk["role_id"] in role_ids for rk in role_kpis))
    check("RoleKPIs -> KPIs", all(rk["kpi_id"] in kpi_ids for rk in role_kpis))
    check("KPI Records -> Employees", all(r["employee_id"] in emp_ids for r in kpi_records))
    check("KPI Records -> RoleKPIs", all(r["role_kpi_id"] in rkpi_ids for r in kpi_records))
    check("Jobs -> Departments", all(j["department_id"] in dept_ids for j in jobs))
    check("Jobs -> Roles", all(j["role_id"] in role_ids for j in jobs))
    check("Interviews -> Candidates", all(i["candidate_id"] in cand_ids for i in interviews))
    check("Interviews -> Jobs", all(i["job_id"] in job_ids for i in interviews))
    check("IntQuestions -> Interviews", all(q["interview_id"] in int_ids for q in int_questions))

    # === KPI Weight Sums ===
    print("\n--- KPI Weight Sums (per role) ---")
    role_weights = defaultdict(float)
    for rk in role_kpis:
        role_weights[rk["role_id"]] += float(rk["weight"])
    all_valid = True
    for role_id, total in sorted(role_weights.items()):
        if abs(total - 1.0) > 0.02:
            print(f"    {role_id}: {total:.3f} FAIL")
            all_valid = False
    check(f"All {len(role_weights)} roles sum to 1.0", all_valid)

    # === Volume Requirements ===
    print("\n--- Volume Requirements ---")
    volumes = [
        ("employees.csv", 100, "Employees"),
        ("roles.csv", 15, "Roles"),
        ("departments.csv", 8, "Departments"),
        ("employee_kpi_records.csv", 1200, "KPI Records"),
        ("employee_tasks.csv", 5000, "Tasks"),
        ("employee_goals.csv", 500, "Goals"),
        ("employee_feedback.csv", 500, "Feedback"),
        ("employee_training.csv", 500, "Training"),
        ("employee_skills.csv", 800, "Employee Skills"),
        ("jobs.csv", 30, "Jobs"),
        ("candidates.csv", 300, "Candidates"),
        ("candidate_skills.csv", 1500, "Candidate Skills"),
        ("candidate_experience.csv", 600, "Candidate Experience"),
        ("candidate_projects.csv", 600, "Candidate Projects"),
        ("interviews.csv", 150, "Interviews"),
        ("interview_questions.csv", 600, "Interview Questions"),
        ("interview_answers.csv", 600, "Interview Answers"),
    ]
    for fname, min_count, label in volumes:
        data = load_csv(os.path.join(DATA_DIR, fname))
        count = len(data)
        passed = count >= min_count
        marker = "PASS" if passed else "FAIL"
        print(f"  {label:25s}: {count:>6,} (min {min_count:>5,}) [{marker}]")

    # === Score Traceability Sample ===
    print("\n--- Score Traceability (Sample EMP001) ---")
    perf = load_csv(os.path.join(DATA_DIR, "employee_performance_history.csv"))
    emp001_perf = [p for p in perf if p["employee_id"] == "EMP001"]
    if emp001_perf:
        latest = emp001_perf[-1]
        print(f"  EMP001 latest overall_score: {latest['overall_score']}")
        print(f"  KPI score: {latest['kpi_score']}, Feedback: {latest['feedback_score']}")
        print(f"  Goal score: {latest['goal_score']}, Skill: {latest['skill_score']}")
        emp001_kpis = [r for r in kpi_records
                       if r["employee_id"] == "EMP001"
                       and r["period_start"] == latest["period_start"]]
        print(f"  Source KPI records for that period: {len(emp001_kpis)}")
        for kr in emp001_kpis[:3]:
            print(f"    {kr['role_kpi_id']}: actual={kr['actual_value']}, "
                  f"target={kr['target_value']}, norm={kr['normalized_score']}, "
                  f"source={kr['data_source']}")

    print("\n--- Score Traceability (Sample CAN001) ---")
    scores = load_csv(os.path.join(DATA_DIR, "candidate_job_scores.csv"))
    can001_scores = [s for s in scores if s["candidate_id"] == "CAN001"]
    if can001_scores:
        s = can001_scores[0]
        print(f"  CAN001 vs {s['job_id']}: overall={s['overall_match_score']}")
        print(f"  Skill match: {s['required_skill_score']}, Proficiency: {s['skill_proficiency_score']}")
        print(f"  Experience: {s['experience_score']}, Projects: {s['project_relevance_score']}")
        print(f"  Interview: {s['interview_score']}, Problem Solving: {s['problem_solving_score']}")
        print(f"  Education: {s['education_score']}")
        print(f"  Mandatory met: {s['mandatory_requirements_met']}, "
              f"failed: {s['mandatory_requirements_failed']}")

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
