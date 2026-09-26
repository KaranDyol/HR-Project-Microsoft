#!/usr/bin/env python3
"""
AI-Driven Intelligent Workforce Management Platform — Database Seeding Script
=============================================================================
Reads synthetic dataset CSV files from the data/ directory, initializes the
database using schema.sql, bulk-loads data into all 36 tables with transactional
integrity, and runs comprehensive validation queries.

Supported Database Engines:
- SQLite (default, self-contained file-based database)
- PostgreSQL (via --db postgres flag)

Usage:
    python seed_database.py                     # Default: SQLite (workforce_management.db)
    python seed_database.py --db sqlite         # Explicit SQLite
    python seed_database.py --db postgres       # PostgreSQL (uses default/env credentials)
    python seed_database.py --db postgres --pg-host localhost --pg-db workforce_db --pg-user postgres
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# SQLite is in standard library
import sqlite3

# Try importing PostgreSQL drivers optionally
try:
    import psycopg2
    from psycopg2 import extras as pg_extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    try:
        import psycopg as psycopg2
        PSYCOPG2_AVAILABLE = True
    except ImportError:
        PSYCOPG2_AVAILABLE = False


# ==============================================================================
# PATH CONFIGURATION (relative to script location)
# ==============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
ONET_DIR = os.path.join(DATA_DIR, "onet")
SCHEMA_FILE = os.path.join(SCRIPT_DIR, "schema.sql")
DEFAULT_SQLITE_PATH = os.path.join(SCRIPT_DIR, "workforce_management.db")


# ==============================================================================
# CSV FILES & TABLE MAPPING (in strict foreign-key dependency order)
# ==============================================================================

TABLE_FILES: List[Tuple[str, str]] = [
    # 1. Foundation & Organization Structure
    ("departments.csv", "departments"),
    ("roles.csv", "roles"),
    ("kpis.csv", "kpis"),
    ("role_kpis.csv", "role_kpis"),
    ("employees.csv", "employees"),
    ("projects.csv", "projects"),
    ("employee_projects.csv", "employee_projects"),
    ("employee_tasks.csv", "employee_tasks"),
    ("employee_quality_records.csv", "employee_quality_records"),
    ("employee_goals.csv", "employee_goals"),
    ("employee_attendance.csv", "employee_attendance"),
    ("employee_feedback.csv", "employee_feedback"),
    ("employee_training.csv", "employee_training"),
    ("employee_skills.csv", "employee_skills"),
    ("employee_kpi_records.csv", "employee_kpi_records"),
    ("employee_performance_history.csv", "employee_performance_history"),
    # 2. Hiring & Candidate Intelligence
    ("jobs.csv", "jobs"),
    ("job_requirements.csv", "job_requirements"),
    ("candidates.csv", "candidates"),
    ("candidate_skills.csv", "candidate_skills"),
    ("candidate_experience.csv", "candidate_experience"),
    ("candidate_education.csv", "candidate_education"),
    ("candidate_certifications.csv", "candidate_certifications"),
    ("candidate_projects.csv", "candidate_projects"),
    ("interviews.csv", "interviews"),
    ("interview_questions.csv", "interview_questions"),
    ("interview_answers.csv", "interview_answers"),
    ("candidate_job_scores.csv", "candidate_job_scores"),
    ("candidate_evidence.csv", "candidate_evidence"),
    ("skill_training_catalog.csv", "skill_training_catalog"),
    # 3. O*NET Workforce Skill Taxonomy (in onet/ directory)
    (os.path.join("onet", "occupations.csv"), "onet_occupations"),
    (os.path.join("onet", "skills.csv"), "onet_skills"),
    (os.path.join("onet", "occupation_skills.csv"), "onet_occupation_skills"),
    (os.path.join("onet", "knowledge.csv"), "onet_knowledge"),
    (os.path.join("onet", "abilities.csv"), "onet_abilities"),
    (os.path.join("onet", "tasks.csv"), "onet_tasks"),
]


# ==============================================================================
# DATABASE ABSTRACTION LAYER
# ==============================================================================

class DatabaseAdapter:
    """Abstract interface supporting both SQLite and PostgreSQL connections."""

    def __init__(self, db_type: str, **kwargs):
        self.db_type = db_type.lower()
        self.kwargs = kwargs
        self.conn = None
        self.cursor = None

    def connect(self):
        if self.db_type == "sqlite":
            db_path = self.kwargs.get("sqlite_path", DEFAULT_SQLITE_PATH)
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()

            # SQLite Performance & Foreign Key Pragmas
            self.cursor.execute("PRAGMA journal_mode = WAL;")
            self.cursor.execute("PRAGMA synchronous = NORMAL;")
            self.cursor.execute("PRAGMA cache_size = -64000;")  # 64MB cache
            self.cursor.execute("PRAGMA foreign_keys = OFF;")    # Defer during loading
        elif self.db_type == "postgres":
            if not PSYCOPG2_AVAILABLE:
                raise ImportError(
                    "PostgreSQL driver (psycopg2 or psycopg) is required for --db postgres.\n"
                    "Install it using: pip install psycopg2-binary"
                )
            pg_url = self.kwargs.get("pg_url")
            if pg_url:
                self.conn = psycopg2.connect(pg_url)
            else:
                self.conn = psycopg2.connect(
                    host=self.kwargs.get("pg_host", os.environ.get("PGHOST", "localhost")),
                    port=int(self.kwargs.get("pg_port", os.environ.get("PGPORT", 5432))),
                    dbname=self.kwargs.get("pg_db", os.environ.get("PGDATABASE", "workforce_management")),
                    user=self.kwargs.get("pg_user", os.environ.get("PGUSER", "postgres")),
                    password=self.kwargs.get("pg_password", os.environ.get("PGPASSWORD", "")),
                )
            self.cursor = self.conn.cursor()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def execute_script(self, script_text: str):
        """Execute a multi-statement DDL script."""
        if self.db_type == "sqlite":
            self.cursor.executescript(script_text)
            self.conn.commit()
        else:
            # PostgreSQL allows executing multi-statement SQL strings directly
            self.cursor.execute(script_text)
            self.conn.commit()

    def get_placeholder(self) -> str:
        """Returns parameter marker for current database type."""
        return "?" if self.db_type == "sqlite" else "%s"

    def enable_foreign_keys(self):
        """Re-enables foreign key checks post-load."""
        if self.db_type == "sqlite":
            self.cursor.execute("PRAGMA foreign_keys = ON;")
        elif self.db_type == "postgres":
            pass

    def bulk_insert(self, table_name: str, columns: List[str], rows: List[List[Any]]):
        """Inserts multiple rows using parameterized queries inside a transaction."""
        if not rows:
            return
        placeholder = self.get_placeholder()
        cols_str = ", ".join(f'"{c}"' for c in columns)
        placeholders_str = ", ".join(placeholder for _ in columns)
        query = f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({placeholders_str})'

        self.cursor.executemany(query, rows)

    def commit(self):
        if self.conn:
            self.conn.commit()

    def rollback(self):
        if self.conn:
            self.conn.rollback()

    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Any]:
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_val(self, query: str, params: Optional[Tuple] = None) -> Any:
        rows = self.fetch_all(query, params)
        if rows and len(rows) > 0:
            return rows[0][0]
        return None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


# ==============================================================================
# DATA TRANSFORMATION & CLEANING HELPERS
# ==============================================================================

def clean_csv_value(val: Any) -> Any:
    """
    Cleans raw CSV strings for SQL insertion:
    - Empty string -> None (SQL NULL)
    - 'true' / 'false' -> Python True / False
    - Preserves all other text/numeric values
    """
    if val is None:
        return None
    if isinstance(val, str):
        v_stripped = val.strip()
        if v_stripped == "":
            return None
        v_lower = v_stripped.lower()
        if v_lower == "true":
            return True
        if v_lower == "false":
            return False
        return v_stripped
    return val


def read_csv_data(file_path: str) -> Tuple[List[str], List[List[Any]]]:
    """Reads CSV file and returns cleaned header list and row tuples."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            raw_header = next(reader)
        except StopIteration:
            return [], []

        headers = [col.strip() for col in raw_header]
        rows = []
        for row in reader:
            if not row or all(c.strip() == "" for c in row):
                continue
            cleaned_row = [clean_csv_value(cell) for cell in row]
            rows.append(cleaned_row)

    return headers, rows


# ==============================================================================
# CORE SEEDING WORKFLOW
# ==============================================================================

def seed_database(
    db: DatabaseAdapter,
    schema_path: str = SCHEMA_FILE,
    data_dir: str = DATA_DIR,
    truncate_existing: bool = True
) -> Dict[str, int]:
    """
    Executes schema.sql and loads data from all CSV files into the database.
    Returns mapping of table names to loaded row counts.
    """
    print("=" * 70)
    print(f"DATABASE SEEDING — Target: {db.db_type.upper()}")
    print("=" * 70)

    # 1. Read and execute schema.sql
    if not os.path.exists(schema_path):
        raise FileNotFoundError(
            f"Schema file not found at: {schema_path}\n"
            "Please ensure schema.sql exists in the script directory."
        )

    print(f"[*] Reading and applying schema: {os.path.basename(schema_path)}...")
    with open(schema_path, mode="r", encoding="utf-8") as f:
        schema_sql = f.read()

    schema_start = time.time()
    db.execute_script(schema_sql)
    schema_duration = (time.time() - schema_start) * 1000
    print(f"    [+] Schema applied successfully in {schema_duration:.1f}ms")

    # 2. Optionally clean existing table data if requested
    if truncate_existing:
        print("[*] Clearing existing table data for clean idempotent seed...")
        # Reverse dependency order for safe deletion
        for _, table_name in reversed(TABLE_FILES):
            try:
                db.cursor.execute(f'DELETE FROM "{table_name}";')
            except Exception:
                pass
        db.commit()

    # 3. Load CSV files in dependency order
    print(f"\n[*] Loading CSV files from: {data_dir}")
    print("-" * 70)
    print(f"{'Table Name':<35} {'CSV Source':<20} {'Rows':>8} {'Time':>8}")
    print("-" * 70)

    records_loaded: Dict[str, int] = {}
    total_start = time.time()

    for rel_csv_path, table_name in TABLE_FILES:
        full_csv_path = os.path.join(data_dir, rel_csv_path)

        if not os.path.exists(full_csv_path):
            print(f"[!] Warning: Missing file {rel_csv_path} for table {table_name}. Skipping.")
            records_loaded[table_name] = 0
            continue

        t0 = time.time()
        headers, rows = read_csv_data(full_csv_path)

        if rows:
            db.bulk_insert(table_name, headers, rows)
            db.commit()

        elapsed_ms = (time.time() - t0) * 1000
        row_count = len(rows)
        records_loaded[table_name] = row_count

        display_src = os.path.basename(rel_csv_path)
        if "onet" in rel_csv_path:
            display_src = f"onet/{display_src}"
        print(f"{table_name:<35} {display_src:<20} {row_count:>8,d} {elapsed_ms:>6.1f}ms")

    total_duration = time.time() - total_start
    total_records = sum(records_loaded.values())

    print("-" * 70)
    print(f"Total Tables Seeded: {len(records_loaded)} | Total Records: {total_records:,} ({total_duration:.2f}s)")
    print("-" * 70)

    # 4. Re-enable foreign keys
    db.enable_foreign_keys()

    return records_loaded


# ==============================================================================
# VALIDATION SUITE
# ==============================================================================

def run_validations(db: DatabaseAdapter, records_loaded: Dict[str, int]) -> bool:
    """
    Executes four comprehensive validation checks:
    1. Count rows per table against loaded records
    2. Referential integrity (FK checks: employees.department_id, roles, etc.)
    3. KPI weight sums per role equal 1.0 (with float precision rounding)
    4. Date consistency (employee join dates before performance history dates)

    Returns True if all validation checks pass, False otherwise.
    """
    print("\n" + "=" * 70)
    print("RUNNING DATA VALIDATION CHECKS")
    print("=" * 70)

    all_passed = True

    # -------------------------------------------------------------------------
    # CHECK 1: Table Row Counts
    # -------------------------------------------------------------------------
    print("\n[Check 1/4] Validating Table Row Counts in Database...")
    count_mismatches = 0

    for table_name, expected_count in records_loaded.items():
        try:
            actual_count = db.fetch_val(f'SELECT COUNT(*) FROM "{table_name}";')
            if actual_count != expected_count:
                print(f"    [-] FAIL: {table_name} expected {expected_count}, got {actual_count}")
                count_mismatches += 1
        except Exception as e:
            print(f"    [-] ERROR checking {table_name}: {e}")
            count_mismatches += 1

    if count_mismatches == 0:
        print(f"    [+] PASS: All {len(records_loaded)} tables match loaded record counts.")
    else:
        print(f"    [-] FAIL: {count_mismatches} tables have count mismatches.")
        all_passed = False

    # -------------------------------------------------------------------------
    # CHECK 2: Referential Integrity (Foreign Keys)
    # -------------------------------------------------------------------------
    print("\n[Check 2/4] Validating Referential Integrity (Foreign Keys)...")
    fk_errors = 0

    # 2a. employees.department_id exists in departments
    q_emp_dept = """
        SELECT COUNT(*)
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.department_id
        WHERE e.department_id IS NOT NULL AND d.department_id IS NULL;
    """
    orphaned_dept = db.fetch_val(q_emp_dept) or 0
    if orphaned_dept == 0:
        print("    [+] PASS: employees.department_id -> departments (0 orphaned records)")
    else:
        print(f"    [-] FAIL: employees.department_id has {orphaned_dept} invalid references!")
        fk_errors += 1

    # 2b. employees.role_id exists in roles
    q_emp_role = """
        SELECT COUNT(*)
        FROM employees e
        LEFT JOIN roles r ON e.role_id = r.role_id
        WHERE e.role_id IS NOT NULL AND r.role_id IS NULL;
    """
    orphaned_roles = db.fetch_val(q_emp_role) or 0
    if orphaned_roles == 0:
        print("    [+] PASS: employees.role_id -> roles (0 orphaned records)")
    else:
        print(f"    [-] FAIL: employees.role_id has {orphaned_roles} invalid references!")
        fk_errors += 1

    # 2c. role_kpis.role_id exists in roles & role_kpis.kpi_id exists in kpis
    q_rkpi = """
        SELECT COUNT(*)
        FROM role_kpis rk
        LEFT JOIN roles r ON rk.role_id = r.role_id
        LEFT JOIN kpis k ON rk.kpi_id = k.kpi_id
        WHERE r.role_id IS NULL OR k.kpi_id IS NULL;
    """
    orphaned_rkpi = db.fetch_val(q_rkpi) or 0
    if orphaned_rkpi == 0:
        print("    [+] PASS: role_kpis -> roles & kpis (0 orphaned records)")
    else:
        print(f"    [-] FAIL: role_kpis has {orphaned_rkpi} orphaned role/kpi references!")
        fk_errors += 1

    # 2d. SQLite built-in comprehensive foreign_key_check
    if db.db_type == "sqlite":
        try:
            fk_violations = db.fetch_all("PRAGMA foreign_key_check;")
            if not fk_violations:
                print("    [+] PASS: SQLite full PRAGMA foreign_key_check (0 violations)")
            else:
                print(f"    [-] FAIL: PRAGMA foreign_key_check reported {len(fk_violations)} violations:")
                for viol in fk_violations[:5]:
                    print(f"        Table: {viol[0]}, RowId: {viol[1]}, Target: {viol[2]}")
                fk_errors += len(fk_violations)
        except Exception as e:
            print(f"    [!] Note: PRAGMA foreign_key_check check error: {e}")

    if fk_errors > 0:
        all_passed = False

    # -------------------------------------------------------------------------
    # CHECK 3: KPI Weight Sums Per Role equal 1.0
    # -------------------------------------------------------------------------
    print("\n[Check 3/4] Validating KPI Weight Sums Per Role (Target = 1.00)...")

    # Round sum of weights to 4 decimal places to avoid floating point variance
    q_weights = """
        SELECT role_id, ROUND(SUM(weight), 4) as total_weight, COUNT(*) as kpi_count
        FROM role_kpis
        GROUP BY role_id
        HAVING ROUND(SUM(weight), 4) != 1.0;
    """
    weight_mismatches = db.fetch_all(q_weights)

    total_roles = db.fetch_val("SELECT COUNT(DISTINCT role_id) FROM role_kpis;") or 0

    if not weight_mismatches:
        print(f"    [+] PASS: All {total_roles} roles have exact KPI weight sum of 1.0000.")
    else:
        print(f"    [-] FAIL: {len(weight_mismatches)} roles have weight sums != 1.0:")
        for r_id, total_w, count in weight_mismatches:
            print(f"        Role {r_id}: Sum={total_w} across {count} KPIs (expected 1.0)")
        all_passed = False

    # -------------------------------------------------------------------------
    # CHECK 4: Date Consistency (Join Dates vs Performance Dates)
    # -------------------------------------------------------------------------
    print("\n[Check 4/4] Validating Date Consistency (Join Dates vs Performance Dates)...")

    # Join date should be on or before performance period end
    q_dates = """
        SELECT COUNT(*)
        FROM employee_performance_history p
        JOIN employees e ON p.employee_id = e.employee_id
        WHERE e.date_of_joining > p.period_end;
    """
    date_violations = db.fetch_val(q_dates) or 0

    # Also check task dates (assigned_date <= due_date)
    q_task_dates = """
        SELECT COUNT(*)
        FROM employee_tasks
        WHERE assigned_date > due_date;
    """
    task_date_violations = db.fetch_val(q_task_dates) or 0

    date_errors = 0
    if date_violations == 0:
        print("    [+] PASS: Employee join dates occur before/during performance evaluation periods.")
    else:
        print(f"    [-] FAIL: Found {date_violations} records where employee join date is after performance period end!")
        date_errors += 1

    if task_date_violations == 0:
        print("    [+] PASS: Employee task assigned dates are prior to or on due dates.")
    else:
        print(f"    [-] FAIL: Found {task_date_violations} tasks where assigned_date > due_date!")
        date_errors += 1

    if date_errors > 0:
        all_passed = False

    # -------------------------------------------------------------------------
    # VALIDATION SUMMARY BANNER
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    status_str = "ALL CHECKS PASSED [SUCCESS]" if all_passed else "VALIDATION CHECKS FAILED [FAILURE]"
    print(f"Status: {status_str}")
    print(f"- Row Counts:         {'PASS' if count_mismatches == 0 else 'FAIL'}")
    print(f"- Referential FKeys:  {'PASS' if fk_errors == 0 else 'FAIL'}")
    print(f"- KPI Weight Sums:    {'PASS' if not weight_mismatches else 'FAIL'}")
    print(f"- Date Consistency:   {'PASS' if date_errors == 0 else 'FAIL'}")
    print("=" * 70)

    return all_passed


# ==============================================================================
# COMMAND LINE INTERFACE & MAIN ENTRY POINT
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Seed database for AI-Driven Workforce Management Platform from CSV files."
    )
    parser.add_argument(
        "--db",
        choices=["sqlite", "postgres"],
        default="sqlite",
        help="Target database engine: 'sqlite' (default) or 'postgres'"
    )
    parser.add_argument(
        "--sqlite-path",
        default=DEFAULT_SQLITE_PATH,
        help=f"Path to SQLite database file (default: {DEFAULT_SQLITE_PATH})"
    )
    parser.add_argument(
        "--schema-path",
        default=SCHEMA_FILE,
        help=f"Path to schema.sql file (default: {SCHEMA_FILE})"
    )
    parser.add_argument(
        "--data-dir",
        default=DATA_DIR,
        help=f"Path to data directory containing CSV files (default: {DATA_DIR})"
    )
    parser.add_argument(
        "--no-truncate",
        action="store_true",
        help="Do not clear existing table data before inserting"
    )
    # PostgreSQL specific arguments
    parser.add_argument("--pg-host", help="PostgreSQL host (default: localhost or PGHOST env)")
    parser.add_argument("--pg-port", type=int, help="PostgreSQL port (default: 5432 or PGPORT env)")
    parser.add_argument("--pg-db", help="PostgreSQL database name (default: workforce_management or PGDATABASE env)")
    parser.add_argument("--pg-user", help="PostgreSQL user (default: postgres or PGUSER env)")
    parser.add_argument("--pg-password", help="PostgreSQL password (or PGPASSWORD env)")
    parser.add_argument("--pg-url", help="PostgreSQL connection URI (e.g. postgresql://user:pass@host:5432/dbname)")

    return parser.parse_args()


def main():
    args = parse_args()

    # Configure database adapter
    adapter_kwargs = {
        "sqlite_path": args.sqlite_path,
        "pg_host": args.pg_host,
        "pg_port": args.pg_port,
        "pg_db": args.pg_db,
        "pg_user": args.pg_user,
        "pg_password": args.pg_password,
        "pg_url": args.pg_url,
    }

    db = DatabaseAdapter(db_type=args.db, **adapter_kwargs)

    try:
        db.connect()
        if args.db == "sqlite":
            print(f"[*] Connected to SQLite database: {os.path.abspath(args.sqlite_path)}")
        else:
            host_info = args.pg_url or f"{args.pg_host or 'localhost'}:{args.pg_port or 5432}/{args.pg_db or 'workforce_management'}"
            print(f"[*] Connected to PostgreSQL database: {host_info}")

        # Execute seeding
        records_loaded = seed_database(
            db=db,
            schema_path=args.schema_path,
            data_dir=args.data_dir,
            truncate_existing=not args.no_truncate
        )

        # Execute validations
        passed = run_validations(db, records_loaded)

        if not passed:
            print("\n[!] WARNING: Database seeding completed with validation issues.")
            sys.exit(1)
        else:
            print("\n[✓] Database seeding and all validation checks completed successfully!")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n[!] Seeding interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n[X] FATAL ERROR during database seeding:\n{e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
