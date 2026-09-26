#!/usr/bin/env python3
"""
AI-Driven Intelligent Workforce Management Platform — Dataset Generator
======================================================================
Generates 35+ interconnected CSV files with realistic, correlated synthetic data.

Systems supported:
1. Employee Performance Intelligence
2. Candidate-Job Hiring/Capability Intelligence
3. Workforce Skill Graph (O*NET 31.0)

Every calculated score has traceable source data.
"""

import csv
import os
import random
import math
from datetime import datetime, date, timedelta
from collections import defaultdict
import hashlib

random.seed(42)

# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "data")
ONET_DIR = os.path.join(OUTPUT_DIR, "onet")

# ============================================================
# DATE RANGES
# ============================================================
PERF_START = date(2026, 1, 1)
PERF_END = date(2026, 6, 30)
PERF_MONTHS = [
    (date(2026, 1, 1), date(2026, 1, 31)),
    (date(2026, 2, 1), date(2026, 2, 28)),
    (date(2026, 3, 1), date(2026, 3, 31)),
    (date(2026, 4, 1), date(2026, 4, 30)),
    (date(2026, 5, 1), date(2026, 5, 31)),
    (date(2026, 6, 1), date(2026, 6, 30)),
]

# ============================================================
# NAME DATA (Indian names for realism)
# ============================================================
MALE_FIRST = [
    "Rahul", "Amit", "Vikram", "Arjun", "Rohit", "Suresh", "Rajesh", "Sanjay",
    "Deepak", "Manish", "Anil", "Vijay", "Gaurav", "Nitin", "Pankaj", "Ashok",
    "Ravi", "Manoj", "Sachin", "Ajay", "Karan", "Varun", "Nikhil", "Harsh",
    "Tushar", "Kunal", "Pranav", "Siddharth", "Aarav", "Aditya", "Ankit",
    "Mohit", "Ishaan", "Dhruv", "Vivek", "Akash", "Neeraj", "Tarun", "Yash",
    "Shubham", "Abhinav", "Rishabh", "Dev", "Mayank", "Chirag", "Jatin",
    "Rohan", "Sameer", "Alok", "Naveen",
]
FEMALE_FIRST = [
    "Priya", "Anjali", "Neha", "Pooja", "Shruti", "Kavita", "Sunita", "Meera",
    "Divya", "Ananya", "Sneha", "Ritu", "Swati", "Nisha", "Pallavi", "Geeta",
    "Seema", "Aarti", "Rekha", "Sapna", "Tanvi", "Ishita", "Simran", "Kriti",
    "Aditi", "Rashmi", "Komal", "Bhavna", "Deepika", "Harini", "Megha",
    "Sonal", "Jyoti", "Namita", "Chitra", "Lakshmi", "Vidya", "Mansi",
    "Payal", "Tanya", "Radhika", "Mitali", "Sonali", "Kirti", "Aparna",
    "Archana", "Garima", "Nandini", "Shivani", "Ritika",
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Reddy", "Nair",
    "Iyer", "Joshi", "Mehta", "Shah", "Agarwal", "Mishra", "Rao", "Bhat",
    "Desai", "Kulkarni", "Pillai", "Menon", "Chopra", "Malhotra", "Kapoor",
    "Srivastava", "Thakur", "Saxena", "Goyal", "Jain", "Bansal", "Chauhan",
    "Tiwari", "Pandey", "Das", "Roy", "Sen", "Bose", "Mukherjee", "Chatterjee",
    "Ghosh", "Dutta", "Bhatt", "Rawat", "Rathore", "Mathur", "Arora",
    "Dhawan", "Sethi", "Luthra", "Khanna", "Bhatia",
]
UNIVERSITIES = [
    "IIT Delhi", "IIT Bombay", "IIT Madras", "IIT Kanpur", "IIT Kharagpur",
    "BITS Pilani", "NIT Trichy", "NIT Warangal", "NIT Surathkal",
    "Delhi University", "Mumbai University", "Anna University",
    "Jadavpur University", "VIT Vellore", "Manipal University",
    "IIIT Hyderabad", "ISI Kolkata", "NSIT Delhi", "COEP Pune",
    "PEC Chandigarh", "SRM University", "Amity University", "Christ University",
    "Symbiosis Pune", "IIIT Bangalore",
]
LOCATIONS = [
    "Bangalore", "Mumbai", "Delhi NCR", "Hyderabad", "Pune", "Chennai",
    "Kolkata", "Ahmedabad", "Jaipur", "Noida", "Gurgaon", "Kochi",
]
COMPANIES = [
    "Infosys", "TCS", "Wipro", "HCL Technologies", "Tech Mahindra",
    "Cognizant", "Capgemini", "Accenture", "IBM India", "Oracle India",
    "Microsoft India", "Amazon India", "Google India", "Flipkart", "Paytm",
    "Zomato", "Swiggy", "Razorpay", "CRED", "PhonePe", "Ola", "Byju's",
    "Freshworks", "Zoho", "MakeMyTrip", "Myntra", "Nykaa", "PolicyBazaar",
    "Lenskart", "CarDekho", "Groww", "Zerodha", "Delhivery", "Meesho",
    "upGrad", "Unacademy", "Dream11", "ICICI Bank", "HDFC Bank",
    "Kotak Mahindra Bank", "Reliance Industries", "Tata Motors",
]

# ============================================================
# EMPLOYEE PERFORMANCE ARCHETYPES
# ============================================================
EMP_ARCHETYPES = {
    "top_performer": {
        "weight": 0.15,
        "task_completion": (85, 98), "on_time": (90, 100), "quality": (85, 95),
        "goal_achievement": (85, 100), "attendance": (95, 100),
        "feedback": (4.0, 5.0), "learning": (80, 100),
        "skill_proficiency": (75, 95),
    },
    "solid_performer": {
        "weight": 0.30,
        "task_completion": (75, 90), "on_time": (80, 95), "quality": (75, 90),
        "goal_achievement": (70, 90), "attendance": (90, 98),
        "feedback": (3.5, 4.5), "learning": (65, 85),
        "skill_proficiency": (60, 80),
    },
    "average": {
        "weight": 0.30,
        "task_completion": (60, 80), "on_time": (65, 85), "quality": (65, 80),
        "goal_achievement": (55, 75), "attendance": (85, 95),
        "feedback": (3.0, 4.0), "learning": (50, 70),
        "skill_proficiency": (45, 70),
    },
    "underperformer": {
        "weight": 0.15,
        "task_completion": (40, 65), "on_time": (45, 70), "quality": (50, 70),
        "goal_achievement": (35, 60), "attendance": (75, 90),
        "feedback": (2.5, 3.5), "learning": (30, 55),
        "skill_proficiency": (30, 55),
    },
    "struggling": {
        "weight": 0.10,
        "task_completion": (25, 50), "on_time": (30, 55), "quality": (40, 60),
        "goal_achievement": (20, 45), "attendance": (65, 85),
        "feedback": (2.0, 3.0), "learning": (20, 40),
        "skill_proficiency": (20, 40),
    },
}

CAND_ARCHETYPES = {
    "strong_all_around": {
        "weight": 0.15,
        "skill_match": (80, 95), "proficiency": (75, 95), "experience": (80, 95),
        "projects": (75, 95), "interview": (80, 95), "education": (80, 95),
    },
    "strong_tech_weak_soft": {
        "weight": 0.15,
        "skill_match": (80, 95), "proficiency": (80, 95), "experience": (70, 85),
        "projects": (75, 90), "interview": (45, 65), "education": (70, 85),
    },
    "experienced_skill_gaps": {
        "weight": 0.15,
        "skill_match": (55, 70), "proficiency": (50, 70), "experience": (80, 95),
        "projects": (70, 85), "interview": (60, 80), "education": (70, 85),
    },
    "junior_talented": {
        "weight": 0.15,
        "skill_match": (75, 90), "proficiency": (70, 90), "experience": (30, 50),
        "projects": (60, 80), "interview": (70, 90), "education": (80, 95),
    },
    "good_resume_weak_interview": {
        "weight": 0.10,
        "skill_match": (75, 90), "proficiency": (70, 85), "experience": (75, 90),
        "projects": (70, 85), "interview": (35, 55), "education": (75, 90),
    },
    "good_interview_limited_exp": {
        "weight": 0.10,
        "skill_match": (65, 80), "proficiency": (60, 75), "experience": (35, 55),
        "projects": (50, 70), "interview": (80, 95), "education": (70, 85),
    },
    "partial_match": {
        "weight": 0.10,
        "skill_match": (45, 65), "proficiency": (45, 65), "experience": (50, 70),
        "projects": (45, 65), "interview": (50, 70), "education": (55, 75),
    },
    "weak": {
        "weight": 0.10,
        "skill_match": (20, 45), "proficiency": (20, 45), "experience": (25, 50),
        "projects": (20, 45), "interview": (25, 50), "education": (30, 55),
    },
}

# ============================================================
# PROFICIENCY MAPPING
# ============================================================
PROFICIENCY_MAP = {
    "Beginner": 25, "Basic": 40, "Intermediate": 60, "Advanced": 80, "Expert": 95,
}
PROFICIENCY_LEVELS = list(PROFICIENCY_MAP.keys())

# ============================================================
# SKILL DEFINITIONS (155 skills)
# ============================================================
# (skill_id, skill_name, category, description)
SKILLS_DATA = [
    ("SKILL_001", "Python", "Programming Language", "Python programming language"),
    ("SKILL_002", "Java", "Programming Language", "Java programming language"),
    ("SKILL_003", "JavaScript", "Programming Language", "JavaScript programming language"),
    ("SKILL_004", "TypeScript", "Programming Language", "TypeScript programming language"),
    ("SKILL_005", "C++", "Programming Language", "C++ programming language"),
    ("SKILL_006", "C#", "Programming Language", "C# programming language"),
    ("SKILL_007", "Go", "Programming Language", "Go programming language"),
    ("SKILL_008", "Rust", "Programming Language", "Rust programming language"),
    ("SKILL_009", "PHP", "Programming Language", "PHP programming language"),
    ("SKILL_010", "Ruby", "Programming Language", "Ruby programming language"),
    ("SKILL_011", "Kotlin", "Programming Language", "Kotlin programming language"),
    ("SKILL_012", "Swift", "Programming Language", "Swift programming language"),
    ("SKILL_013", "Scala", "Programming Language", "Scala programming language"),
    ("SKILL_014", "R", "Programming Language", "R programming language for statistics"),
    ("SKILL_015", "HTML/CSS", "Web Technology", "HTML and CSS web markup and styling"),
    ("SKILL_016", "React", "Web Technology", "React JavaScript library for UI"),
    ("SKILL_017", "Angular", "Web Technology", "Angular web application framework"),
    ("SKILL_018", "Vue.js", "Web Technology", "Vue.js progressive JavaScript framework"),
    ("SKILL_019", "Node.js", "Web Technology", "Node.js server-side JavaScript runtime"),
    ("SKILL_020", "Django", "Web Technology", "Django Python web framework"),
    ("SKILL_021", "Flask", "Web Technology", "Flask Python micro web framework"),
    ("SKILL_022", "FastAPI", "Web Technology", "FastAPI modern Python web framework"),
    ("SKILL_023", "Spring Boot", "Web Technology", "Spring Boot Java framework"),
    ("SKILL_024", ".NET Framework", "Web Technology", "Microsoft .NET development framework"),
    ("SKILL_025", "REST API Design", "Web Technology", "RESTful API architecture and design"),
    ("SKILL_026", "GraphQL", "Web Technology", "GraphQL query language for APIs"),
    ("SKILL_027", "SQL", "Database", "Structured Query Language"),
    ("SKILL_028", "PostgreSQL", "Database", "PostgreSQL relational database"),
    ("SKILL_029", "MySQL", "Database", "MySQL relational database"),
    ("SKILL_030", "MongoDB", "Database", "MongoDB NoSQL document database"),
    ("SKILL_031", "Redis", "Database", "Redis in-memory data store"),
    ("SKILL_032", "Elasticsearch", "Database", "Elasticsearch search and analytics engine"),
    ("SKILL_033", "Oracle Database", "Database", "Oracle relational database system"),
    ("SKILL_034", "Apache Cassandra", "Database", "Cassandra distributed NoSQL database"),
    ("SKILL_035", "Amazon DynamoDB", "Database", "AWS managed NoSQL database"),
    ("SKILL_036", "AWS", "Cloud Platform", "Amazon Web Services cloud platform"),
    ("SKILL_037", "Microsoft Azure", "Cloud Platform", "Microsoft Azure cloud services"),
    ("SKILL_038", "Google Cloud Platform", "Cloud Platform", "Google Cloud Platform services"),
    ("SKILL_039", "Docker", "DevOps", "Docker containerization platform"),
    ("SKILL_040", "Kubernetes", "DevOps", "Kubernetes container orchestration"),
    ("SKILL_041", "CI/CD Pipelines", "DevOps", "Continuous integration and deployment"),
    ("SKILL_042", "Terraform", "DevOps", "Terraform infrastructure as code"),
    ("SKILL_043", "Jenkins", "DevOps", "Jenkins automation server"),
    ("SKILL_044", "Ansible", "DevOps", "Ansible configuration management"),
    ("SKILL_045", "Machine Learning", "Data Science", "Machine learning algorithms and techniques"),
    ("SKILL_046", "Deep Learning", "Data Science", "Deep neural network architectures"),
    ("SKILL_047", "Natural Language Processing", "Data Science", "NLP text analysis techniques"),
    ("SKILL_048", "Computer Vision", "Data Science", "Image and video analysis with ML"),
    ("SKILL_049", "Data Analysis", "Data Science", "Statistical data analysis and interpretation"),
    ("SKILL_050", "Statistical Modeling", "Data Science", "Statistical model building"),
    ("SKILL_051", "TensorFlow", "Data Science", "TensorFlow ML framework"),
    ("SKILL_052", "PyTorch", "Data Science", "PyTorch deep learning framework"),
    ("SKILL_053", "Pandas", "Data Science", "Python data manipulation library"),
    ("SKILL_054", "NumPy", "Data Science", "Python numerical computing library"),
    ("SKILL_055", "Apache Spark", "Data Science", "Distributed data processing engine"),
    ("SKILL_056", "Tableau", "Data Science", "Tableau data visualization platform"),
    ("SKILL_057", "Power BI", "Data Science", "Microsoft Power BI analytics"),
    ("SKILL_058", "Cybersecurity", "Security", "Information security practices"),
    ("SKILL_059", "Network Security", "Security", "Network protection and monitoring"),
    ("SKILL_060", "Penetration Testing", "Security", "Security vulnerability testing"),
    ("SKILL_061", "OWASP Security", "Security", "OWASP web application security"),
    ("SKILL_062", "Identity and Access Management", "Security", "IAM systems and protocols"),
    ("SKILL_063", "Agile Methodology", "Project Management", "Agile software development"),
    ("SKILL_064", "Scrum", "Project Management", "Scrum framework practices"),
    ("SKILL_065", "Kanban", "Project Management", "Kanban workflow management"),
    ("SKILL_066", "Waterfall", "Project Management", "Waterfall project methodology"),
    ("SKILL_067", "Project Management", "Project Management", "Project planning and execution"),
    ("SKILL_068", "JIRA", "Project Management", "JIRA project tracking tool"),
    ("SKILL_069", "Product Management", "Project Management", "Product lifecycle management"),
    ("SKILL_070", "Communication", "Soft Skill", "Verbal and written communication"),
    ("SKILL_071", "Leadership", "Soft Skill", "Team leadership and guidance"),
    ("SKILL_072", "Teamwork", "Soft Skill", "Collaborative team participation"),
    ("SKILL_073", "Problem Solving", "Soft Skill", "Analytical problem resolution"),
    ("SKILL_074", "Critical Thinking", "Soft Skill", "Objective analysis and evaluation"),
    ("SKILL_075", "Time Management", "Soft Skill", "Effective time allocation and prioritization"),
    ("SKILL_076", "Presentation Skills", "Soft Skill", "Public speaking and presentations"),
    ("SKILL_077", "Negotiation", "Soft Skill", "Negotiation and persuasion techniques"),
    ("SKILL_078", "Conflict Resolution", "Soft Skill", "Managing and resolving conflicts"),
    ("SKILL_079", "Mentoring", "Soft Skill", "Coaching and mentoring others"),
    ("SKILL_080", "Financial Analysis", "Business", "Financial data analysis and reporting"),
    ("SKILL_081", "Accounting", "Business", "Accounting principles and practices"),
    ("SKILL_082", "Budgeting", "Business", "Budget planning and management"),
    ("SKILL_083", "Market Analysis", "Business", "Market research and competitive analysis"),
    ("SKILL_084", "Business Strategy", "Business", "Strategic business planning"),
    ("SKILL_085", "CRM Systems", "Business", "Customer relationship management software"),
    ("SKILL_086", "Salesforce", "Business", "Salesforce CRM platform"),
    ("SKILL_087", "Digital Marketing", "Business", "Online marketing strategies"),
    ("SKILL_088", "SEO/SEM", "Business", "Search engine optimization and marketing"),
    ("SKILL_089", "Content Marketing", "Business", "Content strategy and marketing"),
    ("SKILL_090", "Brand Management", "Business", "Brand strategy and positioning"),
    ("SKILL_091", "Talent Acquisition", "Human Resources", "Recruitment and hiring processes"),
    ("SKILL_092", "Employee Relations", "Human Resources", "Employee engagement and relations"),
    ("SKILL_093", "Compensation and Benefits", "Human Resources", "Pay and benefits administration"),
    ("SKILL_094", "Performance Management", "Human Resources", "Employee performance evaluation"),
    ("SKILL_095", "Training and Development", "Human Resources", "Employee training programs"),
    ("SKILL_096", "HR Analytics", "Human Resources", "HR data analysis and insights"),
    ("SKILL_097", "Labor Law Compliance", "Human Resources", "Employment law compliance"),
    ("SKILL_098", "Supply Chain Management", "Operations", "Supply chain planning and execution"),
    ("SKILL_099", "Logistics Management", "Operations", "Transportation and logistics"),
    ("SKILL_100", "Quality Assurance", "Operations", "Quality control processes"),
    ("SKILL_101", "Process Improvement", "Operations", "Business process optimization"),
    ("SKILL_102", "Six Sigma", "Operations", "Six Sigma quality methodology"),
    ("SKILL_103", "Lean Management", "Operations", "Lean principles and practices"),
    ("SKILL_104", "UI/UX Design", "Design", "User interface and experience design"),
    ("SKILL_105", "Figma", "Design", "Figma design and prototyping tool"),
    ("SKILL_106", "Adobe Creative Suite", "Design", "Adobe design software suite"),
    ("SKILL_107", "Prototyping", "Design", "Rapid prototyping techniques"),
    ("SKILL_108", "User Research", "Design", "User behavior research methods"),
    ("SKILL_109", "Networking", "IT Infrastructure", "Computer networking fundamentals"),
    ("SKILL_110", "System Administration", "IT Infrastructure", "System admin and maintenance"),
    ("SKILL_111", "Linux", "IT Infrastructure", "Linux operating system administration"),
    ("SKILL_112", "Windows Server", "IT Infrastructure", "Windows Server administration"),
    ("SKILL_113", "Technical Writing", "IT Infrastructure", "Technical documentation"),
    ("SKILL_114", "IT Service Management", "IT Infrastructure", "ITSM practices and ITIL"),
    ("SKILL_115", "System Design", "Architecture", "Large-scale system architecture"),
    ("SKILL_116", "Distributed Systems", "Architecture", "Distributed computing systems"),
    ("SKILL_117", "High Availability Architecture", "Architecture", "Fault-tolerant system design"),
    ("SKILL_118", "Scalability Patterns", "Architecture", "System scaling strategies"),
    ("SKILL_119", "Unit Testing", "Testing", "Unit test development and execution"),
    ("SKILL_120", "Integration Testing", "Testing", "Integration test strategies"),
    ("SKILL_121", "Selenium", "Testing", "Selenium web testing framework"),
    ("SKILL_122", "Performance Testing", "Testing", "Load and performance testing"),
    ("SKILL_123", "Test Automation", "Testing", "Automated test frameworks"),
    ("SKILL_124", "Android Development", "Mobile", "Android app development"),
    ("SKILL_125", "iOS Development", "Mobile", "iOS app development"),
    ("SKILL_126", "React Native", "Mobile", "React Native cross-platform dev"),
    ("SKILL_127", "Git/Version Control", "DevOps", "Git version control system"),
    ("SKILL_128", "Microservices Architecture", "Architecture", "Microservices design patterns"),
    ("SKILL_129", "Event-Driven Architecture", "Architecture", "Event-driven system design"),
    ("SKILL_130", "API Gateway Management", "Architecture", "API gateway design and management"),
    ("SKILL_131", "ETL Pipelines", "Data Engineering", "Extract-transform-load workflows"),
    ("SKILL_132", "Data Warehousing", "Data Engineering", "Data warehouse design"),
    ("SKILL_133", "Apache Kafka", "Data Engineering", "Kafka event streaming platform"),
    ("SKILL_134", "Apache Airflow", "Data Engineering", "Airflow workflow orchestration"),
    ("SKILL_135", "Data Modeling", "Data Engineering", "Database schema and data modeling"),
    ("SKILL_136", "Google Analytics", "Analytics", "Google Analytics web analytics"),
    ("SKILL_137", "A/B Testing", "Analytics", "Experiment design and A/B tests"),
    ("SKILL_138", "Mixpanel", "Analytics", "Mixpanel product analytics"),
    ("SKILL_139", "Blockchain", "Emerging Technology", "Blockchain and distributed ledger"),
    ("SKILL_140", "Internet of Things", "Emerging Technology", "IoT device and systems"),
    ("SKILL_141", "Augmented Reality", "Emerging Technology", "AR application development"),
    ("SKILL_142", "Edge Computing", "Emerging Technology", "Edge computing infrastructure"),
    ("SKILL_143", "Generative AI", "Emerging Technology", "Generative AI models and applications"),
    ("SKILL_144", "Customer Relationship Management", "Customer Service", "CRM strategy and practices"),
    ("SKILL_145", "Active Listening", "Customer Service", "Active listening communication"),
    ("SKILL_146", "Empathy", "Customer Service", "Empathetic customer interaction"),
    ("SKILL_147", "Issue Resolution", "Customer Service", "Customer issue troubleshooting"),
    ("SKILL_148", "Service Level Management", "Customer Service", "SLA management and tracking"),
    ("SKILL_149", "Risk Management", "Business", "Risk assessment and mitigation"),
    ("SKILL_150", "Compliance Management", "Business", "Regulatory compliance management"),
    ("SKILL_151", "Vendor Management", "Business", "Third-party vendor management"),
    ("SKILL_152", "Stakeholder Management", "Business", "Stakeholder communication and alignment"),
    ("SKILL_153", "Strategic Planning", "Business", "Long-term strategic planning"),
    ("SKILL_154", "Business Process Automation", "Business", "Workflow and process automation"),
    ("SKILL_155", "Data Visualization", "Data Science", "Data visualization techniques and tools"),
]

SKILL_IDS = [s[0] for s in SKILLS_DATA]
SKILL_MAP = {s[0]: s[1] for s in SKILLS_DATA}

# ============================================================
# ROLE-SKILL MAPPINGS
# ============================================================
ROLE_SKILLS = {
    "ROLE001": ["SKILL_001", "SKILL_002", "SKILL_003", "SKILL_007", "SKILL_019",
                "SKILL_020", "SKILL_021", "SKILL_022", "SKILL_023", "SKILL_025",
                "SKILL_026", "SKILL_027", "SKILL_028", "SKILL_030", "SKILL_031",
                "SKILL_039", "SKILL_040", "SKILL_041", "SKILL_127", "SKILL_128",
                "SKILL_115", "SKILL_119", "SKILL_063"],
    "ROLE002": ["SKILL_003", "SKILL_004", "SKILL_015", "SKILL_016", "SKILL_017",
                "SKILL_018", "SKILL_019", "SKILL_025", "SKILL_026", "SKILL_127",
                "SKILL_104", "SKILL_105", "SKILL_119", "SKILL_063", "SKILL_068"],
    "ROLE003": ["SKILL_039", "SKILL_040", "SKILL_041", "SKILL_042", "SKILL_043",
                "SKILL_044", "SKILL_036", "SKILL_037", "SKILL_038", "SKILL_111",
                "SKILL_110", "SKILL_127", "SKILL_109", "SKILL_128", "SKILL_133"],
    "ROLE004": ["SKILL_067", "SKILL_063", "SKILL_071", "SKILL_070", "SKILL_115",
                "SKILL_152", "SKILL_079", "SKILL_153", "SKILL_075", "SKILL_072"],
    "ROLE005": ["SKILL_119", "SKILL_120", "SKILL_121", "SKILL_122", "SKILL_123",
                "SKILL_100", "SKILL_001", "SKILL_003", "SKILL_027", "SKILL_063",
                "SKILL_068"],
    "ROLE006": ["SKILL_091", "SKILL_092", "SKILL_093", "SKILL_094", "SKILL_096",
                "SKILL_097", "SKILL_070", "SKILL_072", "SKILL_075"],
    "ROLE007": ["SKILL_071", "SKILL_091", "SKILL_092", "SKILL_093", "SKILL_094",
                "SKILL_095", "SKILL_096", "SKILL_097", "SKILL_153", "SKILL_070"],
    "ROLE008": ["SKILL_070", "SKILL_077", "SKILL_085", "SKILL_086", "SKILL_076",
                "SKILL_083", "SKILL_144", "SKILL_075", "SKILL_073"],
    "ROLE009": ["SKILL_071", "SKILL_070", "SKILL_077", "SKILL_085", "SKILL_086",
                "SKILL_084", "SKILL_083", "SKILL_152", "SKILL_153"],
    "ROLE010": ["SKILL_087", "SKILL_088", "SKILL_089", "SKILL_090", "SKILL_083",
                "SKILL_136", "SKILL_137", "SKILL_070", "SKILL_155", "SKILL_069"],
    "ROLE011": ["SKILL_080", "SKILL_081", "SKILL_082", "SKILL_049", "SKILL_050",
                "SKILL_057", "SKILL_149", "SKILL_150", "SKILL_027"],
    "ROLE012": ["SKILL_098", "SKILL_099", "SKILL_101", "SKILL_102", "SKILL_103",
                "SKILL_067", "SKILL_152", "SKILL_071", "SKILL_075"],
    "ROLE013": ["SKILL_144", "SKILL_145", "SKILL_146", "SKILL_147", "SKILL_148",
                "SKILL_070", "SKILL_085", "SKILL_073"],
    "ROLE014": ["SKILL_069", "SKILL_063", "SKILL_108", "SKILL_083", "SKILL_152",
                "SKILL_070", "SKILL_049", "SKILL_076", "SKILL_137", "SKILL_073"],
    "ROLE015": ["SKILL_001", "SKILL_014", "SKILL_045", "SKILL_046", "SKILL_047",
                "SKILL_049", "SKILL_050", "SKILL_051", "SKILL_052", "SKILL_053",
                "SKILL_054", "SKILL_027", "SKILL_155", "SKILL_055", "SKILL_135"],
    "ROLE016": ["SKILL_111", "SKILL_112", "SKILL_110", "SKILL_109", "SKILL_039",
                "SKILL_114", "SKILL_044", "SKILL_058"],
    "ROLE017": ["SKILL_058", "SKILL_059", "SKILL_060", "SKILL_061", "SKILL_062",
                "SKILL_111", "SKILL_001", "SKILL_150", "SKILL_109"],
}

# ============================================================
# O*NET 31.0 DATA (Real identifiers and realistic values)
# ============================================================
ONET_OCCUPATIONS_DATA = [
    ("15-1252.00", "Software Developers", "Research, design, and develop computer and network software or specialized utility programs."),
    ("15-1254.00", "Web Developers", "Design, create, and modify websites. Analyze user needs to implement website content, graphics, performance, and capacity."),
    ("15-1211.00", "Computer Systems Analysts", "Analyze science, engineering, business, and other data processing problems to develop and implement solutions."),
    ("15-1212.00", "Information Security Analysts", "Plan, implement, upgrade, or monitor security measures for the protection of computer networks and information."),
    ("15-1242.00", "Database Administrators and Architects", "Administer, test, and implement computer databases, applying knowledge of database management systems."),
    ("15-2051.00", "Data Scientists", "Develop and implement methods to collect, process, and analyze large datasets to identify patterns and trends."),
    ("11-3021.00", "Computer and Information Systems Managers", "Plan, direct, or coordinate activities in electronic data processing, information systems, systems analysis, and computer programming."),
    ("11-2022.00", "Sales Managers", "Plan, direct, or coordinate the actual distribution or movement of a product or service to the customer."),
    ("11-2021.00", "Advertising and Promotions Managers", "Plan, direct, or coordinate advertising policies and programs or produce collateral materials."),
    ("13-2051.00", "Financial Analysts", "Conduct quantitative analyses of information involving investment programs or financial data of public or private institutions."),
    ("11-3121.00", "Human Resources Managers", "Plan, direct, or coordinate human resources activities and staff of an organization."),
    ("13-1071.00", "Human Resources Specialists", "Recruit, screen, interview, or place individuals within an organization."),
    ("11-1021.00", "General and Operations Managers", "Plan, direct, or coordinate the operations of public or private sector organizations."),
    ("43-4051.00", "Customer Service Representatives", "Interact with customers to provide basic or scripted information in response to routine inquiries about products and services."),
    ("13-2011.00", "Accountants and Auditors", "Examine, analyze, and interpret accounting records to prepare financial statements or give advice."),
    ("13-1111.00", "Management Analysts", "Conduct organizational studies and evaluations, design systems and procedures, and conduct work simplification and measurement studies."),
    ("13-1082.00", "Project Management Specialists", "Analyze and coordinate the schedule, timeline, procurement, staffing, and budget of a product or project."),
    ("27-3042.00", "Technical Writers", "Write technical materials, such as equipment manuals, appendices, or operating and maintenance instructions."),
    ("13-1161.00", "Market Research Analysts and Marketing Specialists", "Research conditions in local, regional, national, or online markets."),
    ("13-1151.00", "Training and Development Specialists", "Design or conduct work-related training and development programs to improve performance."),
]

ONET_SKILL_ELEMENTS = [
    ("2.A.1.a", "Reading Comprehension", "Understanding written sentences and paragraphs in work-related documents."),
    ("2.A.1.b", "Active Listening", "Giving full attention to what other people are saying, taking time to understand the points being made."),
    ("2.A.1.c", "Writing", "Communicating effectively in writing as appropriate for the needs of the audience."),
    ("2.A.1.d", "Speaking", "Talking to others to convey information effectively."),
    ("2.A.1.e", "Mathematics", "Using mathematics to solve problems."),
    ("2.A.1.f", "Science", "Using scientific rules and methods to solve problems."),
    ("2.A.2.a", "Critical Thinking", "Using logic and reasoning to identify the strengths and weaknesses of alternative solutions."),
    ("2.A.2.b", "Active Learning", "Understanding the implications of new information for both current and future problem-solving."),
    ("2.A.2.c", "Learning Strategies", "Selecting and using training/instructional methods and procedures appropriate for the situation."),
    ("2.A.2.d", "Monitoring", "Monitoring/assessing performance of yourself, other individuals, or organizations to make improvements."),
    ("2.B.1.a", "Social Perceptiveness", "Being aware of others' reactions and understanding why they react as they do."),
    ("2.B.1.b", "Coordination", "Adjusting actions in relation to others' actions."),
    ("2.B.1.c", "Persuasion", "Persuading others to change their minds or behavior."),
    ("2.B.1.d", "Negotiation", "Bringing others together and trying to reconcile differences."),
    ("2.B.1.e", "Instructing", "Teaching others how to do something."),
    ("2.B.1.f", "Service Orientation", "Actively looking for ways to help people."),
    ("2.B.2.i", "Complex Problem Solving", "Identifying complex problems and reviewing related information to develop and evaluate options."),
    ("2.B.3.a", "Operations Analysis", "Analyzing needs and product requirements to create a design."),
    ("2.B.3.b", "Technology Design", "Generating or adapting equipment and technology to serve user needs."),
    ("2.B.3.e", "Programming", "Writing computer programs for various purposes."),
    ("2.B.4.e", "Quality Control Analysis", "Conducting tests and inspections to evaluate quality or performance."),
    ("2.B.4.g", "Judgment and Decision Making", "Considering the relative costs and benefits of potential actions to choose the most appropriate one."),
    ("2.B.4.h", "Systems Analysis", "Determining how a system should work and how changes will affect outcomes."),
    ("2.B.5.a", "Time Management", "Managing one's own time and the time of others."),
    ("2.B.5.b", "Management of Financial Resources", "Determining how money will be spent to get the work done."),
    ("2.B.5.c", "Management of Material Resources", "Obtaining and seeing to the appropriate use of equipment, facilities, and materials."),
    ("2.B.5.d", "Management of Personnel Resources", "Motivating, developing, and directing people as they work."),
]

ONET_KNOWLEDGE_ELEMENTS = [
    ("2.C.1.a", "Administration and Management", "Knowledge of business and management principles involved in strategic planning and resource allocation."),
    ("2.C.1.b", "Clerical", "Knowledge of administrative and clerical procedures and systems such as word processing and file management."),
    ("2.C.1.c", "Economics and Accounting", "Knowledge of economic and accounting principles and practices, financial markets, and banking."),
    ("2.C.1.d", "Sales and Marketing", "Knowledge of principles and methods for showing, promoting, and selling products or services."),
    ("2.C.1.e", "Customer and Personal Service", "Knowledge of principles and processes for providing customer and personal services."),
    ("2.C.1.f", "Personnel and Human Resources", "Knowledge of principles and procedures for personnel recruitment and selection."),
    ("2.C.2.a", "Production and Processing", "Knowledge of raw materials, production processes, quality control, and costs."),
    ("2.C.3.a", "Computers and Electronics", "Knowledge of circuit boards, processors, electronic equipment, and computer hardware and software."),
    ("2.C.3.b", "Engineering and Technology", "Knowledge of the practical application of engineering science and technology."),
    ("2.C.3.d", "Design", "Knowledge of design techniques, tools, and principles involved in production of precision technical plans."),
    ("2.C.4.a", "Mathematics", "Knowledge of arithmetic, algebra, geometry, calculus, statistics, and their applications."),
    ("2.C.4.c", "Psychology", "Knowledge of human behavior and performance, individual differences, and motivation."),
    ("2.C.4.e", "English Language", "Knowledge of the structure and content of the English language including the meaning and spelling of words."),
    ("2.C.7.a", "Telecommunications", "Knowledge of transmission, broadcasting, switching, control, and operation of telecommunications systems."),
    ("2.C.7.b", "Communications and Media", "Knowledge of media production, communication, and dissemination techniques and methods."),
]

ONET_ABILITY_ELEMENTS = [
    ("1.A.1.a.1", "Oral Comprehension", "The ability to listen to and understand information and ideas presented through spoken words and sentences."),
    ("1.A.1.a.2", "Written Comprehension", "The ability to read and understand information and ideas presented in writing."),
    ("1.A.1.b.1", "Oral Expression", "The ability to communicate information and ideas in speaking so others will understand."),
    ("1.A.1.b.2", "Written Expression", "The ability to communicate information and ideas in writing so others will understand."),
    ("1.A.1.b.3", "Fluency of Ideas", "The ability to come up with a number of ideas about a topic."),
    ("1.A.1.b.4", "Originality", "The ability to come up with unusual or clever ideas about a given topic or situation."),
    ("1.A.1.b.5", "Problem Sensitivity", "The ability to tell when something is wrong or is likely to go wrong."),
    ("1.A.1.c.1", "Deductive Reasoning", "The ability to apply general rules to specific problems to produce answers that make sense."),
    ("1.A.1.c.2", "Inductive Reasoning", "The ability to combine pieces of information to form general rules or conclusions."),
    ("1.A.1.d.1", "Information Ordering", "The ability to arrange things or actions in a certain order according to a specific rule or set of rules."),
    ("1.A.1.e.1", "Mathematical Reasoning", "The ability to choose the right mathematical methods or formulas to solve a problem."),
    ("1.A.1.f.1", "Number Facility", "The ability to add, subtract, multiply, or divide quickly and correctly."),
    ("1.A.2.a.2", "Flexibility of Closure", "The ability to identify or detect a known pattern that is hidden in other distracting material."),
    ("1.A.2.b.1", "Selective Attention", "The ability to concentrate on a task over a period of time without being distracted."),
    ("1.A.2.b.2", "Time Sharing", "The ability to shift back and forth between two or more activities or sources of information."),
    ("1.A.4.a.1", "Near Vision", "The ability to see details at close range within a few feet of the observer."),
]

# Realistic importance/level for selected occupations × skills
# {occ_code: {element_id: (importance, level)}}
ONET_OCC_SKILL_RATINGS = {
    "15-1252.00": {
        "2.A.1.a": (3.75, 4.25), "2.A.1.b": (3.88, 3.75), "2.A.1.c": (3.50, 3.75),
        "2.A.2.a": (4.25, 4.88), "2.A.2.b": (4.12, 4.50), "2.B.2.i": (4.38, 4.63),
        "2.B.3.a": (3.88, 4.12), "2.B.3.b": (4.12, 5.00), "2.B.3.e": (4.75, 5.75),
        "2.B.4.g": (4.00, 4.50), "2.B.4.h": (4.12, 4.75), "2.B.5.a": (3.75, 3.88),
    },
    "15-1254.00": {
        "2.A.1.a": (3.62, 3.88), "2.A.1.b": (3.75, 3.50), "2.A.1.c": (3.38, 3.50),
        "2.A.2.a": (4.00, 4.50), "2.A.2.b": (4.00, 4.25), "2.B.2.i": (4.12, 4.25),
        "2.B.3.a": (3.75, 4.00), "2.B.3.b": (4.25, 5.12), "2.B.3.e": (4.50, 5.50),
        "2.B.4.g": (3.88, 4.25), "2.B.4.h": (3.88, 4.38), "2.B.5.a": (3.62, 3.75),
    },
    "15-1211.00": {
        "2.A.1.a": (4.00, 4.50), "2.A.1.b": (4.12, 4.25), "2.A.1.c": (3.88, 4.12),
        "2.A.1.d": (3.88, 4.00), "2.A.2.a": (4.38, 5.00), "2.A.2.b": (4.00, 4.38),
        "2.B.2.i": (4.25, 4.50), "2.B.3.a": (4.12, 4.50), "2.B.4.g": (4.25, 4.75),
        "2.B.4.h": (4.50, 5.12), "2.B.5.a": (3.88, 4.00),
    },
    "15-1212.00": {
        "2.A.1.a": (3.88, 4.25), "2.A.1.b": (3.75, 3.75), "2.A.1.c": (3.62, 3.88),
        "2.A.2.a": (4.25, 4.88), "2.A.2.b": (4.25, 4.75), "2.B.2.i": (4.38, 4.50),
        "2.B.3.b": (3.88, 4.50), "2.B.4.e": (3.75, 4.12), "2.B.4.g": (4.12, 4.50),
        "2.B.4.h": (4.12, 4.50), "2.B.5.a": (3.75, 3.88),
    },
    "15-1242.00": {
        "2.A.1.a": (3.75, 4.12), "2.A.1.b": (3.62, 3.50), "2.A.1.c": (3.38, 3.62),
        "2.A.2.a": (4.12, 4.75), "2.A.2.b": (3.88, 4.25), "2.B.2.i": (4.00, 4.25),
        "2.B.3.a": (3.88, 4.25), "2.B.3.b": (3.75, 4.38), "2.B.3.e": (4.12, 4.88),
        "2.B.4.g": (3.88, 4.25), "2.B.4.h": (4.00, 4.50),
    },
    "15-2051.00": {
        "2.A.1.a": (4.00, 4.50), "2.A.1.c": (3.75, 4.00), "2.A.1.e": (4.25, 4.75),
        "2.A.2.a": (4.50, 5.12), "2.A.2.b": (4.25, 4.75), "2.B.2.i": (4.50, 4.88),
        "2.B.3.a": (4.12, 4.50), "2.B.3.e": (4.25, 5.12), "2.B.4.g": (4.12, 4.62),
        "2.B.4.h": (4.25, 4.88), "2.B.5.a": (3.62, 3.75),
    },
    "11-3021.00": {
        "2.A.1.a": (4.12, 4.50), "2.A.1.b": (4.25, 4.38), "2.A.1.c": (3.88, 4.12),
        "2.A.1.d": (4.25, 4.50), "2.A.2.a": (4.38, 5.00), "2.A.2.d": (4.12, 4.50),
        "2.B.1.a": (3.88, 4.12), "2.B.1.b": (4.12, 4.38), "2.B.2.i": (4.25, 4.50),
        "2.B.4.g": (4.38, 4.88), "2.B.5.a": (4.12, 4.38), "2.B.5.d": (4.25, 4.62),
    },
    "11-2022.00": {
        "2.A.1.b": (4.12, 4.12), "2.A.1.d": (4.38, 4.62), "2.A.2.a": (4.00, 4.38),
        "2.A.2.d": (3.88, 4.12), "2.B.1.a": (4.00, 4.25), "2.B.1.b": (4.12, 4.25),
        "2.B.1.c": (4.38, 4.50), "2.B.1.d": (4.12, 4.25), "2.B.4.g": (4.25, 4.62),
        "2.B.5.a": (4.00, 4.25), "2.B.5.b": (3.88, 4.00), "2.B.5.d": (4.12, 4.38),
    },
    "11-2021.00": {
        "2.A.1.b": (3.88, 3.75), "2.A.1.c": (3.88, 4.12), "2.A.1.d": (4.12, 4.25),
        "2.A.2.a": (4.12, 4.50), "2.A.2.b": (3.88, 4.12), "2.B.1.a": (3.75, 3.88),
        "2.B.1.b": (4.00, 4.12), "2.B.1.c": (4.25, 4.38), "2.B.4.g": (4.12, 4.50),
        "2.B.5.a": (3.88, 4.00), "2.B.5.b": (4.00, 4.25),
    },
    "13-2051.00": {
        "2.A.1.a": (4.12, 4.62), "2.A.1.c": (3.88, 4.12), "2.A.1.e": (4.38, 4.88),
        "2.A.2.a": (4.38, 5.00), "2.A.2.b": (4.00, 4.38), "2.B.2.i": (4.12, 4.38),
        "2.B.4.g": (4.25, 4.75), "2.B.4.h": (3.88, 4.25), "2.B.5.a": (3.75, 3.88),
    },
    "11-3121.00": {
        "2.A.1.a": (3.88, 4.12), "2.A.1.b": (4.25, 4.25), "2.A.1.c": (3.75, 3.88),
        "2.A.1.d": (4.25, 4.38), "2.A.2.a": (4.12, 4.50), "2.A.2.d": (4.00, 4.25),
        "2.B.1.a": (4.12, 4.25), "2.B.1.b": (4.00, 4.12), "2.B.1.d": (4.25, 4.38),
        "2.B.4.g": (4.38, 4.75), "2.B.5.a": (4.00, 4.12), "2.B.5.d": (4.38, 4.62),
    },
    "13-1071.00": {
        "2.A.1.a": (3.75, 3.88), "2.A.1.b": (4.12, 4.00), "2.A.1.d": (4.00, 4.12),
        "2.A.2.a": (3.88, 4.12), "2.B.1.a": (4.00, 4.12), "2.B.1.b": (3.75, 3.88),
        "2.B.1.c": (3.88, 3.88), "2.B.4.g": (4.00, 4.25), "2.B.5.a": (3.88, 4.00),
    },
    "11-1021.00": {
        "2.A.1.a": (4.00, 4.25), "2.A.1.b": (4.25, 4.25), "2.A.1.d": (4.38, 4.50),
        "2.A.2.a": (4.38, 4.88), "2.A.2.d": (4.25, 4.50), "2.B.1.a": (4.00, 4.12),
        "2.B.1.b": (4.25, 4.38), "2.B.1.d": (4.12, 4.12), "2.B.4.g": (4.50, 5.00),
        "2.B.5.a": (4.25, 4.50), "2.B.5.b": (4.12, 4.25), "2.B.5.d": (4.38, 4.62),
    },
    "43-4051.00": {
        "2.A.1.a": (3.50, 3.38), "2.A.1.b": (4.12, 3.88), "2.A.1.d": (4.00, 3.88),
        "2.A.2.a": (3.50, 3.50), "2.B.1.a": (3.88, 3.75), "2.B.1.f": (4.38, 4.25),
        "2.B.2.i": (3.38, 3.25), "2.B.4.g": (3.62, 3.50), "2.B.5.a": (3.50, 3.38),
    },
    "13-2011.00": {
        "2.A.1.a": (4.12, 4.50), "2.A.1.c": (3.75, 4.00), "2.A.1.e": (4.25, 4.62),
        "2.A.2.a": (4.25, 4.75), "2.A.2.b": (3.88, 4.12), "2.B.2.i": (3.88, 3.88),
        "2.B.4.e": (3.88, 4.12), "2.B.4.g": (4.12, 4.50), "2.B.5.a": (3.88, 4.00),
    },
    "13-1111.00": {
        "2.A.1.a": (4.25, 4.62), "2.A.1.b": (4.25, 4.25), "2.A.1.c": (4.00, 4.25),
        "2.A.1.d": (4.12, 4.25), "2.A.2.a": (4.50, 5.12), "2.A.2.b": (4.12, 4.50),
        "2.B.2.i": (4.38, 4.62), "2.B.4.g": (4.38, 4.88), "2.B.4.h": (4.25, 4.75),
        "2.B.5.a": (4.00, 4.12),
    },
    "13-1082.00": {
        "2.A.1.a": (3.88, 4.12), "2.A.1.b": (4.12, 4.00), "2.A.1.c": (3.88, 4.00),
        "2.A.1.d": (4.12, 4.12), "2.A.2.a": (4.12, 4.50), "2.A.2.d": (4.00, 4.25),
        "2.B.1.b": (4.12, 4.25), "2.B.2.i": (4.00, 4.12), "2.B.4.g": (4.25, 4.62),
        "2.B.5.a": (4.25, 4.38), "2.B.5.b": (3.75, 3.88),
    },
    "27-3042.00": {
        "2.A.1.a": (4.38, 4.75), "2.A.1.b": (3.88, 3.75), "2.A.1.c": (4.62, 5.25),
        "2.A.2.a": (4.00, 4.38), "2.A.2.b": (3.88, 4.12), "2.B.2.i": (3.62, 3.75),
        "2.B.4.g": (3.75, 4.00), "2.B.5.a": (3.88, 4.00),
    },
    "13-1161.00": {
        "2.A.1.a": (4.12, 4.50), "2.A.1.b": (3.88, 3.75), "2.A.1.c": (3.88, 4.12),
        "2.A.1.e": (3.88, 4.12), "2.A.2.a": (4.25, 4.75), "2.A.2.b": (4.00, 4.38),
        "2.B.2.i": (4.00, 4.12), "2.B.4.g": (4.12, 4.50), "2.B.5.a": (3.75, 3.88),
    },
    "13-1151.00": {
        "2.A.1.a": (3.88, 4.00), "2.A.1.b": (4.12, 4.00), "2.A.1.c": (3.75, 3.88),
        "2.A.1.d": (4.25, 4.38), "2.A.2.a": (3.88, 4.12), "2.A.2.c": (4.25, 4.50),
        "2.B.1.a": (3.88, 3.88), "2.B.1.e": (4.38, 4.50), "2.B.4.g": (3.88, 4.12),
        "2.B.5.a": (3.75, 3.88),
    },
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def write_csv(filepath, records, fieldnames):
    """Write list of dicts to CSV."""
    full_path = os.path.join(OUTPUT_DIR, filepath) if not os.path.isabs(filepath) else filepath
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"  Wrote {len(records):>6,} rows -> {filepath}")

def rand_date(start, end):
    """Random date between start and end (inclusive)."""
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(0, delta)))

def arc_val(archetype_ranges, key, noise=5):
    """Get a random value from archetype range with optional noise."""
    lo, hi = archetype_ranges[key]
    base = random.uniform(lo, hi)
    base += random.uniform(-noise, noise)
    return max(0, min(100, base))

def clamp(val, lo=0, hi=100):
    return max(lo, min(hi, val))

def gen_email(first, last, idx):
    domains = ["company.com"]
    return f"{first.lower()}.{last.lower()}{idx}@{domains[0]}"

def gen_phone():
    return f"+91-{random.randint(70000,99999)}{random.randint(10000,99999)}"

def working_days(start, end):
    """Get list of working days (Mon-Fri) between start and end."""
    days = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days

def assign_archetype(archetypes):
    """Weighted random archetype assignment."""
    names = list(archetypes.keys())
    weights = [archetypes[n]["weight"] for n in names]
    return random.choices(names, weights=weights, k=1)[0]


# ============================================================
# DEPARTMENT GENERATOR
# ============================================================
def generate_departments():
    data = [
        ("DEP001", "Engineering", "Software engineering and development"),
        ("DEP002", "Human Resources", "HR management and employee services"),
        ("DEP003", "Sales", "Revenue generation and client management"),
        ("DEP004", "Marketing", "Brand management and marketing campaigns"),
        ("DEP005", "Finance", "Financial planning and accounting"),
        ("DEP006", "Operations", "Business operations and process management"),
        ("DEP007", "Customer Support", "Customer service and support"),
        ("DEP008", "Product", "Product strategy and management"),
        ("DEP009", "Data Science", "Data analytics and machine learning"),
        ("DEP010", "IT", "IT infrastructure and security"),
    ]
    return [{"department_id": d[0], "department_name": d[1],
             "department_description": d[2], "department_head_id": ""} for d in data]


# ============================================================
# ROLE GENERATOR
# ============================================================
def generate_roles():
    data = [
        ("ROLE001", "Backend Developer", "DEP001", "Backend API development and services", "Mid", 2),
        ("ROLE002", "Frontend Developer", "DEP001", "Frontend UI development and design", "Mid", 2),
        ("ROLE003", "DevOps Engineer", "DEP001", "CI/CD, infrastructure, and deployment", "Mid", 3),
        ("ROLE004", "Engineering Manager", "DEP001", "Engineering team leadership and planning", "Senior", 6),
        ("ROLE005", "QA Engineer", "DEP001", "Quality assurance and test automation", "Mid", 2),
        ("ROLE006", "HR Specialist", "DEP002", "Recruitment, onboarding, and HR operations", "Mid", 2),
        ("ROLE007", "HR Manager", "DEP002", "HR strategy and team management", "Senior", 5),
        ("ROLE008", "Sales Executive", "DEP003", "Client acquisition and revenue generation", "Junior", 1),
        ("ROLE009", "Sales Manager", "DEP003", "Sales team leadership and strategy", "Senior", 5),
        ("ROLE010", "Marketing Specialist", "DEP004", "Digital marketing and campaign management", "Mid", 2),
        ("ROLE011", "Financial Analyst", "DEP005", "Financial modeling and analysis", "Mid", 2),
        ("ROLE012", "Operations Manager", "DEP006", "Process optimization and operations management", "Senior", 5),
        ("ROLE013", "Support Specialist", "DEP007", "Customer issue resolution and support", "Junior", 1),
        ("ROLE014", "Product Manager", "DEP008", "Product roadmap and feature planning", "Senior", 4),
        ("ROLE015", "Data Scientist", "DEP009", "ML model development and data analysis", "Mid", 3),
        ("ROLE016", "System Administrator", "DEP010", "Server and infrastructure management", "Mid", 2),
        ("ROLE017", "Security Analyst", "DEP010", "Security monitoring and threat analysis", "Mid", 3),
    ]
    return [{"role_id": r[0], "role_name": r[1], "department_id": r[2],
             "role_description": r[3], "seniority_level": r[4],
             "minimum_experience_years": r[5]} for r in data]


# ============================================================
# KPI GENERATOR
# ============================================================
def generate_kpis():
    data = [
        ("KPI_TASK_COMPLETION", "Task Completion", "Percentage of assigned tasks completed", "percentage", "higher_is_better", "completed_tasks / assigned_tasks * 100"),
        ("KPI_GOAL_ACHIEVEMENT", "Goal Achievement", "Weighted goal completion rate", "percentage", "higher_is_better", "sum(goal_achievement * weight) / sum(weight)"),
        ("KPI_QUALITY", "Quality", "Quality score based on defect rate and rework", "score", "higher_is_better", "100 - (defect_rate * severity_factor)"),
        ("KPI_ONTIME_DELIVERY", "On-Time Delivery", "Percentage of tasks completed on or before due date", "percentage", "higher_is_better", "on_time_tasks / completed_tasks * 100"),
        ("KPI_ATTENDANCE", "Attendance", "Attendance rate excluding approved leaves", "percentage", "higher_is_better", "present_days / scheduled_days * 100"),
        ("KPI_CUSTOMER_SAT", "Customer Satisfaction", "Average customer satisfaction rating", "rating", "higher_is_better", "avg(customer_rating)"),
        ("KPI_REVENUE", "Revenue Achievement", "Revenue achieved vs target", "percentage", "higher_is_better", "actual_revenue / target_revenue * 100"),
        ("KPI_SALES_CONVERSION", "Sales Conversion", "Lead to customer conversion rate", "percentage", "higher_is_better", "conversions / leads * 100"),
        ("KPI_TECHNICAL_SKILL", "Technical Skill", "Technical proficiency assessment score", "score", "higher_is_better", "avg(skill_assessment_scores)"),
        ("KPI_COLLABORATION", "Collaboration", "Peer and manager collaboration rating", "rating", "higher_is_better", "avg(collaboration_ratings)"),
        ("KPI_LEARNING", "Learning", "Training completion and skill development", "score", "higher_is_better", "training_completion * 0.6 + assessment_score * 0.4"),
        ("KPI_PROJECT_CONTRIBUTION", "Project Contribution", "Contribution to project outcomes", "score", "higher_is_better", "avg(project_contribution_scores)"),
    ]
    return [{"kpi_id": k[0], "kpi_name": k[1], "description": k[2],
             "measurement_type": k[3], "default_direction": k[4],
             "calculation_method": k[5]} for k in data]


# ============================================================
# ROLE KPI GENERATOR
# ============================================================
def generate_role_kpis(roles, kpis):
    """Generate role-specific KPI configurations. Weights sum to 1.0 per role."""
    # (role_id, kpi_id, weight, target, min, max, unit, mtype, direction, mandatory)
    configs = [
        # Backend Developer
        ("ROLE001", "KPI_TASK_COMPLETION", 0.20, 50, 0, 100, "tasks", "count", "higher_is_better", True),
        ("ROLE001", "KPI_QUALITY", 0.20, 90, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE001", "KPI_ONTIME_DELIVERY", 0.15, 85, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE001", "KPI_TECHNICAL_SKILL", 0.15, 80, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE001", "KPI_COLLABORATION", 0.10, 4.0, 1, 5, "rating", "rating", "higher_is_better", False),
        ("ROLE001", "KPI_LEARNING", 0.10, 75, 0, 100, "score", "score", "higher_is_better", False),
        ("ROLE001", "KPI_PROJECT_CONTRIBUTION", 0.10, 75, 0, 100, "score", "score", "higher_is_better", False),
        # Frontend Developer
        ("ROLE002", "KPI_TASK_COMPLETION", 0.20, 45, 0, 100, "tasks", "count", "higher_is_better", True),
        ("ROLE002", "KPI_QUALITY", 0.20, 88, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE002", "KPI_ONTIME_DELIVERY", 0.15, 85, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE002", "KPI_TECHNICAL_SKILL", 0.15, 78, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE002", "KPI_COLLABORATION", 0.10, 4.0, 1, 5, "rating", "rating", "higher_is_better", False),
        ("ROLE002", "KPI_LEARNING", 0.10, 75, 0, 100, "score", "score", "higher_is_better", False),
        ("ROLE002", "KPI_PROJECT_CONTRIBUTION", 0.10, 75, 0, 100, "score", "score", "higher_is_better", False),
        # DevOps Engineer
        ("ROLE003", "KPI_TASK_COMPLETION", 0.20, 40, 0, 100, "tasks", "count", "higher_is_better", True),
        ("ROLE003", "KPI_QUALITY", 0.20, 92, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE003", "KPI_ONTIME_DELIVERY", 0.15, 88, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE003", "KPI_TECHNICAL_SKILL", 0.20, 82, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE003", "KPI_COLLABORATION", 0.10, 4.0, 1, 5, "rating", "rating", "higher_is_better", False),
        ("ROLE003", "KPI_LEARNING", 0.15, 78, 0, 100, "score", "score", "higher_is_better", False),
        # Engineering Manager
        ("ROLE004", "KPI_GOAL_ACHIEVEMENT", 0.25, 85, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE004", "KPI_COLLABORATION", 0.20, 4.2, 1, 5, "rating", "rating", "higher_is_better", True),
        ("ROLE004", "KPI_PROJECT_CONTRIBUTION", 0.20, 80, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE004", "KPI_TECHNICAL_SKILL", 0.10, 75, 0, 100, "score", "score", "higher_is_better", False),
        ("ROLE004", "KPI_ONTIME_DELIVERY", 0.15, 85, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE004", "KPI_QUALITY", 0.10, 88, 0, 100, "score", "score", "higher_is_better", False),
        # QA Engineer
        ("ROLE005", "KPI_QUALITY", 0.30, 95, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE005", "KPI_TASK_COMPLETION", 0.20, 60, 0, 100, "tasks", "count", "higher_is_better", True),
        ("ROLE005", "KPI_ONTIME_DELIVERY", 0.15, 85, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE005", "KPI_TECHNICAL_SKILL", 0.15, 78, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE005", "KPI_COLLABORATION", 0.10, 4.0, 1, 5, "rating", "rating", "higher_is_better", False),
        ("ROLE005", "KPI_LEARNING", 0.10, 75, 0, 100, "score", "score", "higher_is_better", False),
        # HR Specialist
        ("ROLE006", "KPI_TASK_COMPLETION", 0.20, 40, 0, 100, "tasks", "count", "higher_is_better", True),
        ("ROLE006", "KPI_GOAL_ACHIEVEMENT", 0.20, 80, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE006", "KPI_COLLABORATION", 0.20, 4.0, 1, 5, "rating", "rating", "higher_is_better", True),
        ("ROLE006", "KPI_ATTENDANCE", 0.15, 95, 0, 100, "percent", "percentage", "higher_is_better", False),
        ("ROLE006", "KPI_LEARNING", 0.10, 70, 0, 100, "score", "score", "higher_is_better", False),
        ("ROLE006", "KPI_CUSTOMER_SAT", 0.15, 4.0, 1, 5, "rating", "rating", "higher_is_better", False),
        # HR Manager
        ("ROLE007", "KPI_GOAL_ACHIEVEMENT", 0.25, 85, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE007", "KPI_COLLABORATION", 0.20, 4.2, 1, 5, "rating", "rating", "higher_is_better", True),
        ("ROLE007", "KPI_ATTENDANCE", 0.10, 95, 0, 100, "percent", "percentage", "higher_is_better", False),
        ("ROLE007", "KPI_CUSTOMER_SAT", 0.15, 4.2, 1, 5, "rating", "rating", "higher_is_better", False),
        ("ROLE007", "KPI_PROJECT_CONTRIBUTION", 0.15, 78, 0, 100, "score", "score", "higher_is_better", False),
        ("ROLE007", "KPI_LEARNING", 0.15, 75, 0, 100, "score", "score", "higher_is_better", False),
        # Sales Executive
        ("ROLE008", "KPI_REVENUE", 0.30, 100, 0, 200, "percent", "percentage", "higher_is_better", True),
        ("ROLE008", "KPI_SALES_CONVERSION", 0.25, 25, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE008", "KPI_CUSTOMER_SAT", 0.15, 4.0, 1, 5, "rating", "rating", "higher_is_better", False),
        ("ROLE008", "KPI_TASK_COMPLETION", 0.10, 35, 0, 100, "tasks", "count", "higher_is_better", False),
        ("ROLE008", "KPI_GOAL_ACHIEVEMENT", 0.10, 80, 0, 100, "percent", "percentage", "higher_is_better", False),
        ("ROLE008", "KPI_ATTENDANCE", 0.10, 92, 0, 100, "percent", "percentage", "higher_is_better", False),
        # Sales Manager
        ("ROLE009", "KPI_REVENUE", 0.30, 100, 0, 200, "percent", "percentage", "higher_is_better", True),
        ("ROLE009", "KPI_SALES_CONVERSION", 0.20, 28, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE009", "KPI_GOAL_ACHIEVEMENT", 0.20, 85, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE009", "KPI_COLLABORATION", 0.15, 4.2, 1, 5, "rating", "rating", "higher_is_better", False),
        ("ROLE009", "KPI_PROJECT_CONTRIBUTION", 0.15, 80, 0, 100, "score", "score", "higher_is_better", False),
        # Marketing Specialist
        ("ROLE010", "KPI_TASK_COMPLETION", 0.20, 40, 0, 100, "tasks", "count", "higher_is_better", True),
        ("ROLE010", "KPI_GOAL_ACHIEVEMENT", 0.20, 80, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE010", "KPI_ONTIME_DELIVERY", 0.15, 85, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE010", "KPI_COLLABORATION", 0.15, 4.0, 1, 5, "rating", "rating", "higher_is_better", False),
        ("ROLE010", "KPI_LEARNING", 0.15, 72, 0, 100, "score", "score", "higher_is_better", False),
        ("ROLE010", "KPI_PROJECT_CONTRIBUTION", 0.15, 75, 0, 100, "score", "score", "higher_is_better", False),
        # Financial Analyst
        ("ROLE011", "KPI_QUALITY", 0.25, 92, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE011", "KPI_TASK_COMPLETION", 0.20, 38, 0, 100, "tasks", "count", "higher_is_better", True),
        ("ROLE011", "KPI_GOAL_ACHIEVEMENT", 0.20, 82, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE011", "KPI_TECHNICAL_SKILL", 0.15, 80, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE011", "KPI_ONTIME_DELIVERY", 0.10, 88, 0, 100, "percent", "percentage", "higher_is_better", False),
        ("ROLE011", "KPI_ATTENDANCE", 0.10, 95, 0, 100, "percent", "percentage", "higher_is_better", False),
        # Operations Manager
        ("ROLE012", "KPI_GOAL_ACHIEVEMENT", 0.25, 85, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE012", "KPI_QUALITY", 0.20, 90, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE012", "KPI_ONTIME_DELIVERY", 0.20, 88, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE012", "KPI_COLLABORATION", 0.15, 4.2, 1, 5, "rating", "rating", "higher_is_better", False),
        ("ROLE012", "KPI_ATTENDANCE", 0.10, 95, 0, 100, "percent", "percentage", "higher_is_better", False),
        ("ROLE012", "KPI_PROJECT_CONTRIBUTION", 0.10, 78, 0, 100, "score", "score", "higher_is_better", False),
        # Support Specialist
        ("ROLE013", "KPI_CUSTOMER_SAT", 0.30, 4.2, 1, 5, "rating", "rating", "higher_is_better", True),
        ("ROLE013", "KPI_TASK_COMPLETION", 0.20, 55, 0, 100, "tasks", "count", "higher_is_better", True),
        ("ROLE013", "KPI_QUALITY", 0.15, 85, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE013", "KPI_ATTENDANCE", 0.15, 95, 0, 100, "percent", "percentage", "higher_is_better", False),
        ("ROLE013", "KPI_COLLABORATION", 0.10, 3.8, 1, 5, "rating", "rating", "higher_is_better", False),
        ("ROLE013", "KPI_LEARNING", 0.10, 70, 0, 100, "score", "score", "higher_is_better", False),
        # Product Manager
        ("ROLE014", "KPI_GOAL_ACHIEVEMENT", 0.25, 85, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE014", "KPI_COLLABORATION", 0.20, 4.2, 1, 5, "rating", "rating", "higher_is_better", True),
        ("ROLE014", "KPI_PROJECT_CONTRIBUTION", 0.20, 82, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE014", "KPI_TASK_COMPLETION", 0.15, 38, 0, 100, "tasks", "count", "higher_is_better", False),
        ("ROLE014", "KPI_QUALITY", 0.10, 85, 0, 100, "score", "score", "higher_is_better", False),
        ("ROLE014", "KPI_LEARNING", 0.10, 75, 0, 100, "score", "score", "higher_is_better", False),
        # Data Scientist
        ("ROLE015", "KPI_TECHNICAL_SKILL", 0.25, 82, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE015", "KPI_QUALITY", 0.20, 90, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE015", "KPI_TASK_COMPLETION", 0.15, 35, 0, 100, "tasks", "count", "higher_is_better", True),
        ("ROLE015", "KPI_PROJECT_CONTRIBUTION", 0.15, 80, 0, 100, "score", "score", "higher_is_better", False),
        ("ROLE015", "KPI_LEARNING", 0.15, 80, 0, 100, "score", "score", "higher_is_better", False),
        ("ROLE015", "KPI_GOAL_ACHIEVEMENT", 0.10, 80, 0, 100, "percent", "percentage", "higher_is_better", False),
        # System Administrator
        ("ROLE016", "KPI_TASK_COMPLETION", 0.20, 45, 0, 100, "tasks", "count", "higher_is_better", True),
        ("ROLE016", "KPI_QUALITY", 0.20, 90, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE016", "KPI_ONTIME_DELIVERY", 0.15, 88, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE016", "KPI_TECHNICAL_SKILL", 0.20, 80, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE016", "KPI_ATTENDANCE", 0.10, 95, 0, 100, "percent", "percentage", "higher_is_better", False),
        ("ROLE016", "KPI_COLLABORATION", 0.15, 3.8, 1, 5, "rating", "rating", "higher_is_better", False),
        # Security Analyst
        ("ROLE017", "KPI_QUALITY", 0.25, 93, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE017", "KPI_TECHNICAL_SKILL", 0.25, 84, 0, 100, "score", "score", "higher_is_better", True),
        ("ROLE017", "KPI_TASK_COMPLETION", 0.15, 38, 0, 100, "tasks", "count", "higher_is_better", True),
        ("ROLE017", "KPI_ONTIME_DELIVERY", 0.15, 88, 0, 100, "percent", "percentage", "higher_is_better", True),
        ("ROLE017", "KPI_LEARNING", 0.10, 80, 0, 100, "score", "score", "higher_is_better", False),
        ("ROLE017", "KPI_GOAL_ACHIEVEMENT", 0.10, 80, 0, 100, "percent", "percentage", "higher_is_better", False),
    ]
    records = []
    for i, c in enumerate(configs, 1):
        records.append({
            "role_kpi_id": f"RKPI{i:03d}",
            "role_id": c[0], "kpi_id": c[1], "weight": c[2],
            "target_value": c[3], "minimum_value": c[4], "maximum_value": c[5],
            "measurement_unit": c[6], "measurement_type": c[7],
            "direction": c[8], "is_mandatory": str(c[9]).lower(), "active": "true",
        })
    return records


# ============================================================
# EMPLOYEE GENERATOR
# ============================================================
def generate_employees(departments, roles):
    # Distribution of employees per role
    role_counts = {
        "ROLE001": 15, "ROLE002": 10, "ROLE003": 6, "ROLE004": 4, "ROLE005": 6,
        "ROLE006": 5, "ROLE007": 2, "ROLE008": 10, "ROLE009": 3, "ROLE010": 5,
        "ROLE011": 5, "ROLE012": 3, "ROLE013": 8, "ROLE014": 4, "ROLE015": 6,
        "ROLE016": 4, "ROLE017": 4,
    }
    role_lookup = {r["role_id"]: r for r in roles}
    dept_lookup = {d["department_id"]: d for d in departments}

    employees = []
    emp_idx = 0
    used_names = set()

    # Manager roles for hierarchy
    manager_roles = {"ROLE004", "ROLE007", "ROLE009", "ROLE012"}

    for role_id, count in role_counts.items():
        role = role_lookup[role_id]
        dept_id = role["department_id"]
        seniority = role["seniority_level"]
        min_exp = role["minimum_experience_years"]

        for _ in range(count):
            emp_idx += 1
            gender = random.choice(["Male", "Female"])
            if gender == "Male":
                first = random.choice(MALE_FIRST)
            else:
                first = random.choice(FEMALE_FIRST)
            last = random.choice(LAST_NAMES)
            # Ensure unique name combo
            while (first, last) in used_names:
                last = random.choice(LAST_NAMES)
            used_names.add((first, last))

            # Archetype assignment
            archetype = assign_archetype(EMP_ARCHETYPES)

            exp_before = max(min_exp, random.randint(min_exp, min_exp + 8))
            if seniority == "Junior":
                exp_before = random.randint(0, 2)
            elif seniority == "Mid":
                exp_before = random.randint(2, 7)
            elif seniority == "Senior":
                exp_before = random.randint(5, 15)

            dob_year = 2026 - 22 - exp_before - random.randint(0, 5)
            dob = date(dob_year, random.randint(1, 12), random.randint(1, 28))

            join_year = 2026 - random.randint(1, max(1, min(exp_before, 6)))
            join_date = date(join_year, random.randint(1, 12), random.randint(1, 28))
            if join_date > date(2025, 12, 1):
                join_date = date(2025, random.randint(1, 11), random.randint(1, 28))

            education_levels = ["Bachelor's", "Master's", "PhD"]
            if seniority == "Senior":
                ed_level = random.choice(["Master's", "PhD", "Bachelor's", "Master's"])
            else:
                ed_level = random.choice(["Bachelor's", "Master's", "Bachelor's"])

            ed_fields = {
                "DEP001": ["Computer Science", "Software Engineering", "Information Technology", "Electronics"],
                "DEP002": ["Human Resource Management", "Business Administration", "Psychology"],
                "DEP003": ["Business Administration", "Marketing", "Economics", "Commerce"],
                "DEP004": ["Marketing", "Mass Communication", "Business Administration"],
                "DEP005": ["Finance", "Accounting", "Economics", "Commerce", "Business Administration"],
                "DEP006": ["Operations Management", "Business Administration", "Industrial Engineering"],
                "DEP007": ["Business Administration", "Communication", "Information Technology"],
                "DEP008": ["Business Administration", "Computer Science", "Design"],
                "DEP009": ["Data Science", "Statistics", "Computer Science", "Mathematics"],
                "DEP010": ["Computer Science", "Information Technology", "Cybersecurity", "Networking"],
            }

            salary_ranges = {
                "Junior": (400000, 800000),
                "Mid": (800000, 1800000),
                "Senior": (1500000, 3500000),
            }
            sal_lo, sal_hi = salary_ranges.get(seniority, (600000, 1500000))
            salary = round(random.randint(sal_lo, sal_hi), -3)

            level_map = {"Junior": "L1", "Mid": random.choice(["L2", "L3"]),
                         "Senior": random.choice(["L4", "L5"])}

            emp = {
                "employee_id": f"EMP{emp_idx:03d}",
                "employee_code": f"E{emp_idx:03d}",
                "first_name": first,
                "last_name": last,
                "email": gen_email(first, last, emp_idx),
                "phone": gen_phone(),
                "gender": gender,
                "date_of_birth": dob.isoformat(),
                "date_of_joining": join_date.isoformat(),
                "employment_status": "active",
                "employment_type": "full_time",
                "department_id": dept_id,
                "role_id": role_id,
                "manager_id": "",  # filled later
                "location": random.choice(LOCATIONS),
                "work_mode": random.choice(["onsite", "remote", "hybrid", "hybrid", "hybrid"]),
                "current_salary": salary,
                "experience_before_joining_years": exp_before,
                "education_level": ed_level,
                "education_field": random.choice(ed_fields.get(dept_id, ["General"])),
                "university": random.choice(UNIVERSITIES),
                "current_level": level_map.get(seniority, "L2"),
                "created_at": join_date.isoformat() + "T09:00:00",
                "updated_at": "2026-06-30T09:00:00",
                "_archetype": archetype,  # internal, removed before CSV write
                "_role_id": role_id,
            }
            employees.append(emp)

    # Assign managers
    dept_managers = {}
    for emp in employees:
        if emp["_role_id"] in manager_roles:
            dept_managers.setdefault(emp["department_id"], []).append(emp["employee_id"])
    for emp in employees:
        if emp["_role_id"] not in manager_roles:
            managers = dept_managers.get(emp["department_id"], [])
            if managers:
                emp["manager_id"] = random.choice(managers)
        elif emp["_role_id"] in manager_roles:
            # Managers report to other managers or are top-level
            other_mgrs = [m for m in dept_managers.get(emp["department_id"], [])
                          if m != emp["employee_id"]]
            if other_mgrs:
                emp["manager_id"] = other_mgrs[0]

    # Set department heads
    for dept in departments:
        mgrs = dept_managers.get(dept["department_id"], [])
        if mgrs:
            dept["department_head_id"] = mgrs[0]

    return employees


# ============================================================
# PROJECT GENERATOR
# ============================================================
def generate_projects(departments):
    project_data = [
        ("PRJ001", "Atlas Platform", "DEP001", "Core backend microservices platform", "development", "high", "Python,FastAPI,PostgreSQL,Docker,Kubernetes"),
        ("PRJ002", "Nova Dashboard", "DEP001", "Real-time analytics dashboard", "development", "high", "React,TypeScript,Node.js,Redis,GraphQL"),
        ("PRJ003", "Shield Security", "DEP010", "Security monitoring and threat detection system", "development", "critical", "Python,Elasticsearch,AWS,Docker"),
        ("PRJ004", "Velocity CI/CD", "DEP001", "CI/CD pipeline modernization", "infrastructure", "high", "Jenkins,Docker,Kubernetes,Terraform,AWS"),
        ("PRJ005", "Prism Analytics", "DEP009", "ML-powered business analytics platform", "data_science", "high", "Python,TensorFlow,Spark,PostgreSQL"),
        ("PRJ006", "Horizon CRM", "DEP003", "Next-gen customer relationship management", "development", "medium", "Salesforce,React,Node.js,PostgreSQL"),
        ("PRJ007", "Pulse Marketing", "DEP004", "Marketing automation and campaign manager", "development", "medium", "Python,Django,React,Redis"),
        ("PRJ008", "Nexus HR", "DEP002", "HR management and employee portal", "development", "medium", "Python,Django,React,PostgreSQL"),
        ("PRJ009", "Quantum Finance", "DEP005", "Financial reporting and budgeting system", "development", "high", "Python,PostgreSQL,Power BI,React"),
        ("PRJ010", "Meridian Ops", "DEP006", "Operations management and tracking", "development", "medium", "Python,FastAPI,MongoDB,React"),
        ("PRJ011", "Echo Support", "DEP007", "AI-powered customer support platform", "development", "medium", "Python,NLP,React,PostgreSQL,Redis"),
        ("PRJ012", "Catalyst Mobile", "DEP001", "Cross-platform mobile application", "development", "high", "React Native,Node.js,Firebase"),
        ("PRJ013", "Apex Data Lake", "DEP009", "Enterprise data lake and ETL pipelines", "data_science", "high", "Spark,Kafka,Airflow,AWS,Python"),
        ("PRJ014", "Forge DevTools", "DEP001", "Internal developer tools and SDK", "development", "medium", "Go,Docker,Kubernetes,gRPC"),
        ("PRJ015", "Zenith Product", "DEP008", "Product analytics and roadmap management", "development", "medium", "React,Node.js,PostgreSQL,Mixpanel"),
        ("PRJ016", "Titan Infrastructure", "DEP010", "Cloud infrastructure migration", "infrastructure", "critical", "AWS,Terraform,Ansible,Docker"),
        ("PRJ017", "Orbit Marketing Analytics", "DEP004", "Marketing data analytics pipeline", "data_science", "medium", "Python,Google Analytics,Tableau,BigQuery"),
        ("PRJ018", "Genesis Onboarding", "DEP002", "New employee onboarding automation", "development", "low", "Python,Django,React"),
        ("PRJ019", "Vanguard Sales AI", "DEP003", "AI-powered sales forecasting", "data_science", "high", "Python,Scikit-learn,PostgreSQL,React"),
        ("PRJ020", "Pinnacle QA", "DEP001", "Test automation framework", "development", "medium", "Python,Selenium,Jenkins,Docker"),
        ("PRJ021", "Ember Training", "DEP002", "Learning management system", "development", "low", "Django,React,PostgreSQL"),
        ("PRJ022", "Radiant Branding", "DEP004", "Brand management and asset platform", "development", "low", "React,Node.js,AWS S3"),
        ("PRJ023", "Citadel Compliance", "DEP005", "Regulatory compliance tracking", "development", "high", "Python,PostgreSQL,React,Docker"),
        ("PRJ024", "Helix Data Pipeline", "DEP009", "Real-time data streaming pipeline", "data_science", "high", "Kafka,Spark,Python,Cassandra"),
        ("PRJ025", "Phoenix Legacy Migration", "DEP001", "Legacy system modernization", "infrastructure", "critical", "Java,Spring Boot,PostgreSQL,Docker"),
        ("PRJ026", "Summit Executive Dashboard", "DEP008", "C-suite reporting dashboard", "development", "high", "React,D3.js,Node.js,PostgreSQL"),
        ("PRJ027", "Sentinel Monitoring", "DEP010", "Infrastructure monitoring and alerting", "infrastructure", "high", "Prometheus,Grafana,Python,Docker"),
        ("PRJ028", "Aurora Content Platform", "DEP004", "Content management and publishing", "development", "medium", "Django,React,Elasticsearch,AWS"),
        ("PRJ029", "Nebula API Gateway", "DEP001", "API gateway and rate limiting service", "infrastructure", "high", "Go,Redis,Docker,Kubernetes"),
        ("PRJ030", "Stellar Customer Insights", "DEP003", "Customer behavior analytics", "data_science", "medium", "Python,Pandas,Tableau,PostgreSQL"),
    ]
    records = []
    for p in project_data:
        start_offset = random.randint(-60, 30)  # relative to PERF_START
        start = PERF_START + timedelta(days=start_offset)
        duration = random.randint(60, 200)
        end = start + timedelta(days=duration)
        status = "active" if end > PERF_END else "completed"
        if start > PERF_END:
            status = "planned"
        records.append({
            "project_id": p[0], "project_name": p[1], "department_id": p[2],
            "description": p[3], "project_type": p[4],
            "start_date": start.isoformat(), "end_date": end.isoformat(),
            "status": status, "business_priority": p[5], "technology_stack": p[6],
        })
    return records


# ============================================================
# EMPLOYEE-PROJECT GENERATOR
# ============================================================
def generate_employee_projects(employees, projects):
    records = []
    ep_id = 0
    proj_by_dept = defaultdict(list)
    for p in projects:
        proj_by_dept[p["department_id"]].append(p)
    # Also add some cross-dept projects
    all_projects = list(projects)

    for emp in employees:
        dept_projs = proj_by_dept.get(emp["department_id"], [])
        # Each employee works on 1-3 projects
        n_projects = random.randint(1, min(3, max(1, len(dept_projs))))
        chosen = random.sample(dept_projs, min(n_projects, len(dept_projs))) if dept_projs else random.sample(all_projects, 1)

        for proj in chosen:
            ep_id += 1
            role_names = ["developer", "contributor", "lead", "reviewer", "tester", "analyst", "coordinator"]
            archetype = emp["_archetype"]
            contrib_base = arc_val(EMP_ARCHETYPES[archetype], "task_completion", noise=8)
            records.append({
                "employee_project_id": f"EP{ep_id:04d}",
                "employee_id": emp["employee_id"],
                "project_id": proj["project_id"],
                "role_in_project": random.choice(role_names),
                "responsibility": f"Contributing to {proj['project_name']}",
                "allocation_percentage": random.choice([20, 30, 40, 50, 60, 70, 80, 100]),
                "start_date": proj["start_date"],
                "end_date": proj["end_date"],
                "contribution_score": round(clamp(contrib_base), 1),
            })
    return records


# ============================================================
# EMPLOYEE TASK GENERATOR (5000+)
# ============================================================
def generate_tasks(employees, projects, employee_projects):
    records = []
    task_id = 0
    # Map employee to their projects
    emp_projs = defaultdict(list)
    for ep in employee_projects:
        emp_projs[ep["employee_id"]].append(ep["project_id"])

    task_types = ["feature", "bug_fix", "enhancement", "documentation", "review",
                  "testing", "deployment", "research", "design", "maintenance"]
    complexities = ["low", "medium", "high", "critical"]
    priorities = ["low", "medium", "high", "urgent"]

    for emp in employees:
        archetype = emp["_archetype"]
        arc = EMP_ARCHETYPES[archetype]
        projs = emp_projs.get(emp["employee_id"], ["PRJ001"])

        # ~50-60 tasks per employee over 6 months
        n_tasks = random.randint(45, 65)
        for _ in range(n_tasks):
            task_id += 1
            proj_id = random.choice(projs)
            assigned = rand_date(PERF_START, PERF_END - timedelta(days=7))
            complexity = random.choices(complexities, weights=[30, 40, 20, 10], k=1)[0]
            est_hours = {"low": random.uniform(2, 8), "medium": random.uniform(6, 20),
                         "high": random.uniform(16, 40), "critical": random.uniform(30, 60)}[complexity]
            due_days = {"low": random.randint(2, 5), "medium": random.randint(4, 10),
                        "high": random.randint(7, 21), "critical": random.randint(14, 30)}[complexity]
            due = assigned + timedelta(days=due_days)
            priority = random.choices(priorities, weights=[20, 40, 30, 10], k=1)[0]

            # Determine completion based on archetype
            completion_rate = arc_val(arc, "task_completion", noise=8) / 100
            is_completed = random.random() < completion_rate

            if is_completed:
                on_time_rate = arc_val(arc, "on_time", noise=8) / 100
                is_on_time = random.random() < on_time_rate
                if is_on_time:
                    completed = rand_date(assigned, due)
                else:
                    late_days = random.randint(1, 7)
                    completed = due + timedelta(days=late_days)
                status = "completed"
            elif due < PERF_END:
                completed = None
                status = random.choice(["overdue", "in_progress"])
            else:
                completed = None
                status = random.choice(["assigned", "in_progress"])

            # Quality score based on archetype
            quality_base = arc_val(arc, "quality", noise=8)
            rework = random.random() < (1 - quality_base / 100) * 0.5
            rework_count = random.randint(1, 3) if rework else 0
            actual_hours = est_hours * random.uniform(0.7, 1.5)

            records.append({
                "task_id": f"TASK{task_id:05d}",
                "employee_id": emp["employee_id"],
                "project_id": proj_id,
                "assigned_date": assigned.isoformat(),
                "due_date": due.isoformat(),
                "completed_date": completed.isoformat() if completed else "",
                "status": status,
                "priority": priority,
                "estimated_hours": round(est_hours, 1),
                "actual_hours": round(actual_hours, 1),
                "quality_score": round(clamp(quality_base), 1) if is_completed else "",
                "rework_required": str(rework).lower() if is_completed else "",
                "rework_count": rework_count if is_completed else "",
                "complexity": complexity,
                "task_type": random.choice(task_types),
            })
    return records


# ============================================================
# QUALITY RECORDS GENERATOR
# ============================================================
def generate_quality_records(employees, tasks, projects):
    records = []
    qr_id = 0
    # Group tasks by employee and month
    emp_month_tasks = defaultdict(list)
    for t in tasks:
        if t["status"] == "completed":
            emp_id = t["employee_id"]
            month = t["completed_date"][:7]  # YYYY-MM
            emp_month_tasks[(emp_id, month)].append(t)

    for (emp_id, month), month_tasks in emp_month_tasks.items():
        emp = next(e for e in employees if e["employee_id"] == emp_id)
        archetype = emp["_archetype"]
        arc = EMP_ARCHETYPES[archetype]
        quality_base = arc_val(arc, "quality", noise=5) / 100

        total_items = len(month_tasks)
        if total_items < 3:
            continue

        defect_rate = clamp(1 - quality_base, 0, 0.4)
        defects = max(0, int(total_items * defect_rate * random.uniform(0.5, 1.5)))
        critical = max(0, int(defects * random.uniform(0.1, 0.3)))
        minor = defects - critical
        rework = sum(1 for t in month_tasks if t.get("rework_required") == "true")

        # Pick a random reviewer from managers
        reviewer_id = emp.get("manager_id", "")

        qr_id += 1
        quality_rating = round(clamp(quality_base * 100 + random.uniform(-5, 5)), 1)
        records.append({
            "quality_record_id": f"QR{qr_id:04d}",
            "employee_id": emp_id,
            "task_id": month_tasks[0]["task_id"],  # representative task
            "project_id": month_tasks[0]["project_id"],
            "period": month,
            "total_items": total_items,
            "defects": defects,
            "critical_defects": critical,
            "minor_defects": minor,
            "rework_count": rework,
            "quality_rating": quality_rating,
            "reviewer_id": reviewer_id,
        })
    return records


# ============================================================
# GOALS GENERATOR (500+)
# ============================================================
def generate_goals(employees):
    records = []
    goal_id = 0
    categories = ["individual", "team", "project", "business", "learning"]
    goal_templates = [
        ("Complete {} training modules", "learning", 10),
        ("Deliver {} feature releases", "project", 5),
        ("Achieve {}% code coverage", "individual", 80),
        ("Mentor {} junior developers", "team", 3),
        ("Reduce bug count by {}%", "individual", 30),
        ("Complete {} certifications", "learning", 2),
        ("Improve customer satisfaction by {} points", "business", 5),
        ("Process {} support tickets", "individual", 200),
        ("Generate {} qualified leads", "business", 50),
        ("Automate {} manual processes", "project", 5),
        ("Publish {} technical articles", "learning", 4),
        ("Achieve {}% SLA compliance", "business", 95),
        ("Reduce response time by {}%", "individual", 20),
        ("Complete {} cross-team collaborations", "team", 4),
        ("Achieve revenue target of {} lakhs", "business", 50),
    ]

    for emp in employees:
        archetype = emp["_archetype"]
        arc = EMP_ARCHETYPES[archetype]
        n_goals = random.randint(4, 7)

        chosen_templates = random.sample(goal_templates, min(n_goals, len(goal_templates)))
        for template, cat, target in chosen_templates:
            goal_id += 1
            goal_title = template.format(target)
            start = rand_date(PERF_START, PERF_START + timedelta(days=30))
            due = rand_date(PERF_END - timedelta(days=30), PERF_END)

            achievement_pct = arc_val(arc, "goal_achievement", noise=10)
            actual = round(target * achievement_pct / 100, 1)

            if achievement_pct >= 100:
                status = "completed"
            elif achievement_pct >= 70:
                status = "on_track"
            elif achievement_pct >= 40:
                status = "at_risk"
            else:
                status = "behind"

            weight = round(random.choice([0.15, 0.20, 0.25, 0.10]), 2)

            records.append({
                "goal_id": f"GOAL{goal_id:04d}",
                "employee_id": emp["employee_id"],
                "goal_title": goal_title,
                "goal_description": f"Objective: {goal_title}",
                "goal_category": cat,
                "start_date": start.isoformat(),
                "due_date": due.isoformat(),
                "target_value": target,
                "actual_value": actual,
                "achievement_percentage": round(clamp(achievement_pct), 1),
                "weight": weight,
                "status": status,
                "manager_id": emp.get("manager_id", ""),
            })
    return records


# ============================================================
# ATTENDANCE GENERATOR
# ============================================================
def generate_attendance(employees):
    records = []
    att_id = 0
    w_days = working_days(PERF_START, PERF_END)
    leave_types = ["sick", "casual", "earned", "personal", "emergency"]

    # Identify holidays (Republic Day, Holi, etc.)
    holidays = {
        date(2026, 1, 26), date(2026, 3, 10), date(2026, 3, 30),
        date(2026, 4, 14), date(2026, 5, 1), date(2026, 6, 17),
    }

    for emp in employees:
        archetype = emp["_archetype"]
        arc = EMP_ARCHETYPES[archetype]
        att_rate = arc_val(arc, "attendance", noise=3) / 100

        for day in w_days:
            att_id += 1
            if day in holidays:
                status = "holiday"
                scheduled = 8
                worked = 0
                leave_type = ""
                late = 0
                overtime = 0
            elif random.random() > att_rate:
                # Absent or leave
                if random.random() < 0.7:
                    status = "leave"
                    leave_type = random.choice(leave_types)
                else:
                    status = "absent"
                    leave_type = ""
                scheduled = 8
                worked = 0
                late = 0
                overtime = 0
            else:
                # Present
                is_remote = random.random() < 0.3
                status = "remote" if is_remote else "present"
                scheduled = 8
                worked = round(random.uniform(7.0, 9.5), 1)
                leave_type = ""
                late = random.choice([0, 0, 0, 0, 0, 5, 10, 15, 20, 30]) if random.random() < 0.15 else 0
                overtime = round(max(0, worked - 8), 1)

                # Half day occasionally
                if random.random() < 0.03:
                    status = "half_day"
                    worked = round(random.uniform(3.5, 4.5), 1)
                    overtime = 0

            records.append({
                "attendance_id": f"ATT{att_id:06d}",
                "employee_id": emp["employee_id"],
                "date": day.isoformat(),
                "status": status,
                "scheduled_hours": scheduled,
                "worked_hours": worked,
                "leave_type": leave_type,
                "late_minutes": late,
                "overtime_hours": overtime,
            })
    return records


# ============================================================
# FEEDBACK GENERATOR (500+)
# ============================================================
def generate_feedback(employees):
    records = []
    fb_id = 0
    reviewer_roles = ["manager", "peer", "self", "subordinate"]
    emp_by_dept = defaultdict(list)
    for e in employees:
        emp_by_dept[e["department_id"]].append(e)

    comments_positive = [
        "Consistently delivers high-quality work.", "Excellent team player with strong communication.",
        "Proactive in identifying and solving problems.", "Shows strong technical leadership.",
        "Great at mentoring junior team members.", "Reliable and always meets deadlines.",
        "Brings innovative ideas to the team.", "Strong analytical and problem-solving skills.",
    ]
    comments_neutral = [
        "Meets expectations in most areas.", "Good work but could improve on communication.",
        "Delivers on time but quality needs improvement.", "Adequate performance with room for growth.",
        "Handles routine tasks well.", "Needs to take more initiative.",
    ]
    comments_negative = [
        "Needs significant improvement in meeting deadlines.", "Communication skills require development.",
        "Quality of work has been inconsistent.", "Needs to be more proactive in team settings.",
    ]

    for emp in employees:
        archetype = emp["_archetype"]
        arc = EMP_ARCHETYPES[archetype]

        # Each employee gets 3-7 feedback records across periods
        n_fb = random.randint(4, 7)
        for _ in range(n_fb):
            fb_id += 1
            period_idx = random.randint(0, 5)
            period = PERF_MONTHS[period_idx][0].strftime("%Y-%m")

            # Select reviewer
            rev_role = random.choice(reviewer_roles)
            if rev_role == "self":
                reviewer_id = emp["employee_id"]
            elif rev_role == "manager":
                reviewer_id = emp.get("manager_id") or emp["employee_id"]
            else:
                dept_emps = [e for e in emp_by_dept[emp["department_id"]]
                             if e["employee_id"] != emp["employee_id"]]
                reviewer_id = random.choice(dept_emps)["employee_id"] if dept_emps else emp["employee_id"]

            def rating(key="feedback"):
                base = arc_val(arc, key, noise=0.3)
                lo, hi = arc[key]
                return round(clamp(random.uniform(lo, hi), 1, 5), 1)

            tech_r = rating()
            comm_r = rating()
            team_r = rating()
            ps_r = rating()
            lead_r = rating()
            overall_r = round((tech_r + comm_r + team_r + ps_r + lead_r) / 5, 1)

            if overall_r >= 4.0:
                comment = random.choice(comments_positive)
            elif overall_r >= 3.0:
                comment = random.choice(comments_neutral)
            else:
                comment = random.choice(comments_negative)

            records.append({
                "feedback_id": f"FB{fb_id:04d}",
                "employee_id": emp["employee_id"],
                "reviewer_id": reviewer_id,
                "reviewer_role": rev_role,
                "period": period,
                "technical_skill_rating": tech_r,
                "communication_rating": comm_r,
                "teamwork_rating": team_r,
                "problem_solving_rating": ps_r,
                "leadership_rating": lead_r,
                "overall_rating": overall_r,
                "comment": comment,
                "created_at": PERF_MONTHS[period_idx][1].isoformat() + "T10:00:00",
            })
    return records


# ============================================================
# TRAINING GENERATOR (500+)
# ============================================================
def generate_training(employees, skills_data):
    records = []
    tr_id = 0
    categories = ["technical", "soft_skills", "certification", "leadership", "compliance", "domain"]
    statuses = ["completed", "in_progress", "enrolled", "dropped"]
    training_names = [
        "Advanced Python Programming", "React Masterclass", "AWS Solutions Architect Prep",
        "Docker & Kubernetes Bootcamp", "Machine Learning Fundamentals", "Leadership Excellence",
        "Effective Communication Workshop", "Agile & Scrum Certification", "Data Analysis with Pandas",
        "Cybersecurity Essentials", "SQL Performance Tuning", "Cloud Architecture Design",
        "Deep Learning Specialization", "Product Management Fundamentals", "Financial Modeling",
        "Project Management Professional Prep", "DevOps Best Practices", "UX Research Methods",
        "Digital Marketing Strategy", "Six Sigma Green Belt", "Negotiation Skills",
        "Time Management Mastery", "Technical Writing Excellence", "Blockchain Fundamentals",
        "NLP with Transformers", "System Design Interview Prep", "API Design Best Practices",
        "Test Automation Framework", "Data Visualization Masterclass", "Salesforce Administration",
    ]

    for emp in employees:
        archetype = emp["_archetype"]
        arc = EMP_ARCHETYPES[archetype]
        n_trainings = random.randint(4, 7)
        role_skills = ROLE_SKILLS.get(emp["_role_id"], SKILL_IDS[:10])

        chosen_trainings = random.sample(training_names, min(n_trainings, len(training_names)))
        for tname in chosen_trainings:
            tr_id += 1
            skill_id = random.choice(role_skills) if role_skills else random.choice(SKILL_IDS[:30])
            start = rand_date(PERF_START, PERF_END - timedelta(days=14))
            duration_days = random.randint(7, 60)
            completion_date = start + timedelta(days=duration_days)

            learning_base = arc_val(arc, "learning", noise=10) / 100
            status = random.choices(statuses, weights=[50, 25, 15, 10], k=1)[0]
            if status == "completed":
                completion_pct = 100
                assessment = round(clamp(learning_base * 100 + random.uniform(-10, 10)), 1)
            elif status == "in_progress":
                completion_pct = random.randint(30, 80)
                assessment = ""
                completion_date = ""
            elif status == "enrolled":
                completion_pct = 0
                assessment = ""
                completion_date = ""
            else:
                completion_pct = random.randint(10, 40)
                assessment = ""

            records.append({
                "training_id": f"TR{tr_id:04d}",
                "employee_id": emp["employee_id"],
                "training_name": tname,
                "skill_id": skill_id,
                "training_category": random.choice(categories),
                "start_date": start.isoformat(),
                "completion_date": completion_date if isinstance(completion_date, str) else completion_date.isoformat() if completion_date else "",
                "completion_percentage": completion_pct,
                "assessment_score": assessment,
                "status": status,
                "hours_spent": round(random.uniform(5, 60), 1),
            })
    return records


# ============================================================
# EMPLOYEE SKILLS GENERATOR (800+)
# ============================================================
def generate_employee_skills(employees, skills_data):
    records = []
    es_id = 0
    assessment_methods = ["self_assessment", "manager_assessment", "certification", "project_work", "peer_review"]
    evidence_sources = ["project", "certification", "training", "work_experience", "assessment"]

    for emp in employees:
        archetype = emp["_archetype"]
        arc = EMP_ARCHETYPES[archetype]
        role_skills = ROLE_SKILLS.get(emp["_role_id"], SKILL_IDS[:8])

        # Each employee has 6-12 skills
        extra_skills = random.sample([s for s in SKILL_IDS if s not in role_skills],
                                     min(random.randint(1, 4), len(SKILL_IDS) - len(role_skills)))
        all_skills = list(role_skills) + extra_skills
        n_skills = min(len(all_skills), random.randint(6, 12))
        chosen = random.sample(all_skills, n_skills)

        for skill_id in chosen:
            es_id += 1
            prof_base = arc_val(arc, "skill_proficiency", noise=10)

            # Determine proficiency level from score
            if prof_base >= 85:
                level = "Expert"
            elif prof_base >= 70:
                level = "Advanced"
            elif prof_base >= 50:
                level = "Intermediate"
            elif prof_base >= 30:
                level = "Basic"
            else:
                level = "Beginner"

            prof_score = PROFICIENCY_MAP[level] + random.randint(-5, 5)
            prof_score = clamp(prof_score, 10, 100)

            years_exp = min(int(emp["experience_before_joining_years"]),
                           random.randint(1, max(1, int(emp["experience_before_joining_years"]))))

            records.append({
                "employee_skill_id": f"ES{es_id:04d}",
                "employee_id": emp["employee_id"],
                "skill_id": skill_id,
                "proficiency_level": level,
                "proficiency_score": round(prof_score),
                "years_of_experience": years_exp,
                "last_assessed_date": rand_date(PERF_START, PERF_END).isoformat(),
                "assessment_method": random.choice(assessment_methods),
                "evidence_source": random.choice(evidence_sources),
            })
    return records


# ============================================================
# KPI RECORDS GENERATOR (1200+)
# ============================================================
def generate_kpi_records(employees, role_kpis, tasks, goals, quality_recs, attendance, feedback):
    records = []
    rec_id = 0

    # Build lookup structures
    role_kpi_map = defaultdict(list)  # role_id -> [role_kpi records]
    for rk in role_kpis:
        role_kpi_map[rk["role_id"]].append(rk)

    # Index data by employee and month
    def month_key(d_str):
        return d_str[:7] if d_str else None

    emp_tasks_by_month = defaultdict(list)
    for t in tasks:
        mk = month_key(t["assigned_date"])
        if mk:
            emp_tasks_by_month[(t["employee_id"], mk)].append(t)

    emp_goals_by_month = defaultdict(list)
    for g in goals:
        # Goals span periods, attribute to due_date month
        mk = month_key(g["due_date"])
        if mk:
            emp_goals_by_month[(g["employee_id"], mk)].append(g)

    emp_quality_by_month = defaultdict(list)
    for q in quality_recs:
        emp_quality_by_month[(q["employee_id"], q["period"])].append(q)

    emp_att_by_month = defaultdict(list)
    for a in attendance:
        mk = month_key(a["date"])
        if mk:
            emp_att_by_month[(a["employee_id"], mk)].append(a)

    emp_fb_by_month = defaultdict(list)
    for f in feedback:
        emp_fb_by_month[(f["employee_id"], f["period"])].append(f)

    for emp in employees:
        role_id = emp["_role_id"]
        kpis_for_role = role_kpi_map.get(role_id, [])

        for month_start, month_end in PERF_MONTHS:
            mk = month_start.strftime("%Y-%m")

            for rkpi in kpis_for_role:
                rec_id += 1
                kpi_id = rkpi["kpi_id"]
                target = float(rkpi["target_value"])
                source_ref = ""

                # Calculate actual values from source data
                if kpi_id == "KPI_TASK_COMPLETION":
                    month_tasks = emp_tasks_by_month.get((emp["employee_id"], mk), [])
                    total = len(month_tasks)
                    completed = sum(1 for t in month_tasks if t["status"] == "completed")
                    actual = round(completed / max(1, total) * 100, 1)
                    source_ref = f"TASKS_{mk}"

                elif kpi_id == "KPI_ONTIME_DELIVERY":
                    month_tasks = emp_tasks_by_month.get((emp["employee_id"], mk), [])
                    completed = [t for t in month_tasks if t["status"] == "completed"]
                    on_time = sum(1 for t in completed
                                 if t["completed_date"] and t["completed_date"] <= t["due_date"])
                    actual = round(on_time / max(1, len(completed)) * 100, 1) if completed else 0
                    source_ref = f"TASKS_{mk}"

                elif kpi_id == "KPI_QUALITY":
                    qrecs = emp_quality_by_month.get((emp["employee_id"], mk), [])
                    if qrecs:
                        actual = round(sum(float(q["quality_rating"]) for q in qrecs) / len(qrecs), 1)
                    else:
                        # Fallback: derive from task quality scores
                        month_tasks = emp_tasks_by_month.get((emp["employee_id"], mk), [])
                        quality_scores = [float(t["quality_score"]) for t in month_tasks
                                         if t.get("quality_score")]
                        actual = round(sum(quality_scores) / max(1, len(quality_scores)), 1) if quality_scores else target * 0.8
                    source_ref = f"QUALITY_{mk}"

                elif kpi_id == "KPI_GOAL_ACHIEVEMENT":
                    gls = emp_goals_by_month.get((emp["employee_id"], mk), [])
                    if gls:
                        weighted_sum = sum(float(g["achievement_percentage"]) * float(g["weight"]) for g in gls)
                        weight_sum = sum(float(g["weight"]) for g in gls)
                        actual = round(weighted_sum / max(0.01, weight_sum), 1)
                    else:
                        # Use archetype to generate
                        arc = EMP_ARCHETYPES[emp["_archetype"]]
                        actual = round(arc_val(arc, "goal_achievement", noise=5), 1)
                    source_ref = f"GOALS_{mk}"

                elif kpi_id == "KPI_ATTENDANCE":
                    att_recs = emp_att_by_month.get((emp["employee_id"], mk), [])
                    if att_recs:
                        scheduled = sum(1 for a in att_recs if a["status"] != "holiday")
                        present = sum(1 for a in att_recs
                                     if a["status"] in ("present", "remote", "half_day"))
                        actual = round(present / max(1, scheduled) * 100, 1)
                    else:
                        actual = 90
                    source_ref = f"ATTENDANCE_{mk}"

                elif kpi_id == "KPI_CUSTOMER_SAT":
                    fb_recs = emp_fb_by_month.get((emp["employee_id"], mk), [])
                    if fb_recs:
                        actual = round(sum(float(f["overall_rating"]) for f in fb_recs) / len(fb_recs), 1)
                    else:
                        arc = EMP_ARCHETYPES[emp["_archetype"]]
                        actual = round(random.uniform(*arc["feedback"]), 1)
                    source_ref = f"FEEDBACK_{mk}"

                elif kpi_id == "KPI_REVENUE":
                    arc = EMP_ARCHETYPES[emp["_archetype"]]
                    actual = round(arc_val(arc, "goal_achievement", noise=10), 1)
                    source_ref = f"SALES_{mk}"

                elif kpi_id == "KPI_SALES_CONVERSION":
                    arc = EMP_ARCHETYPES[emp["_archetype"]]
                    base = arc_val(arc, "task_completion", noise=8)
                    actual = round(base * 0.3, 1)  # conversion rates are lower
                    source_ref = f"SALES_{mk}"

                elif kpi_id == "KPI_TECHNICAL_SKILL":
                    fb_recs = emp_fb_by_month.get((emp["employee_id"], mk), [])
                    if fb_recs:
                        tech_avg = sum(float(f["technical_skill_rating"]) for f in fb_recs) / len(fb_recs)
                        actual = round(tech_avg / 5 * 100, 1)  # normalize to 0-100
                    else:
                        arc = EMP_ARCHETYPES[emp["_archetype"]]
                        actual = round(arc_val(arc, "skill_proficiency", noise=8), 1)
                    source_ref = f"SKILLS_{mk}"

                elif kpi_id == "KPI_COLLABORATION":
                    fb_recs = emp_fb_by_month.get((emp["employee_id"], mk), [])
                    if fb_recs:
                        actual = round(sum(float(f["teamwork_rating"]) for f in fb_recs) / len(fb_recs), 1)
                    else:
                        arc = EMP_ARCHETYPES[emp["_archetype"]]
                        actual = round(random.uniform(*arc["feedback"]), 1)
                    source_ref = f"FEEDBACK_{mk}"

                elif kpi_id == "KPI_LEARNING":
                    arc = EMP_ARCHETYPES[emp["_archetype"]]
                    actual = round(arc_val(arc, "learning", noise=8), 1)
                    source_ref = f"TRAINING_{mk}"

                elif kpi_id == "KPI_PROJECT_CONTRIBUTION":
                    arc = EMP_ARCHETYPES[emp["_archetype"]]
                    actual = round(arc_val(arc, "task_completion", noise=10), 1)
                    source_ref = f"PROJECTS_{mk}"

                else:
                    actual = round(target * random.uniform(0.7, 1.1), 1)

                # Normalize score
                if rkpi["measurement_type"] == "rating":
                    max_val = float(rkpi["maximum_value"])
                    normalized = round(actual / max_val * 100, 1) if max_val else actual
                elif rkpi["measurement_type"] == "percentage":
                    normalized = round(clamp(actual), 1)
                else:
                    normalized = round(clamp(actual / max(1, target) * 100), 1)

                records.append({
                    "record_id": f"REC{rec_id:05d}",
                    "employee_id": emp["employee_id"],
                    "role_kpi_id": rkpi["role_kpi_id"],
                    "period_start": month_start.isoformat(),
                    "period_end": month_end.isoformat(),
                    "actual_value": actual,
                    "target_value": target,
                    "normalized_score": normalized,
                    "data_source": kpi_id.lower().replace("kpi_", "") + "_system",
                    "source_record_id": source_ref,
                    "created_at": month_end.isoformat() + "T23:59:00",
                })
    return records


# ============================================================
# PERFORMANCE HISTORY GENERATOR
# ============================================================
def generate_performance_history(employees, kpi_records, role_kpis):
    records = []
    perf_id = 0

    # Build role_kpi weight lookup
    rkpi_weights = {rk["role_kpi_id"]: float(rk["weight"]) for rk in role_kpis}

    # Group KPI records by employee and month
    emp_month_kpis = defaultdict(list)
    for rec in kpi_records:
        mk = rec["period_start"][:7]
        emp_month_kpis[(rec["employee_id"], mk)].append(rec)

    for emp in employees:
        previous_score = None
        for month_start, month_end in PERF_MONTHS:
            mk = month_start.strftime("%Y-%m")
            month_kpis = emp_month_kpis.get((emp["employee_id"], mk), [])
            if not month_kpis:
                continue

            perf_id += 1
            # Calculate weighted KPI score
            kpi_weighted = sum(float(r["normalized_score"]) * rkpi_weights.get(r["role_kpi_id"], 0)
                              for r in month_kpis)

            # Feedback score (avg of feedback ratings for this month)
            fb_score = 0
            fb_kpis = [r for r in month_kpis if "feedback" in r.get("data_source", "")
                       or "customer" in r.get("data_source", "")]
            if fb_kpis:
                fb_score = sum(float(r["normalized_score"]) for r in fb_kpis) / len(fb_kpis)

            # Goal score
            goal_kpis = [r for r in month_kpis if "goal" in r.get("data_source", "")]
            goal_score = sum(float(r["normalized_score"]) for r in goal_kpis) / max(1, len(goal_kpis)) if goal_kpis else 0

            # Skill score
            skill_kpis = [r for r in month_kpis if "skill" in r.get("data_source", "")
                         or "technical" in r.get("data_source", "")]
            skill_score = sum(float(r["normalized_score"]) for r in skill_kpis) / max(1, len(skill_kpis)) if skill_kpis else 0

            overall = round(clamp(kpi_weighted), 1)
            score_change = round(overall - previous_score, 1) if previous_score is not None else 0
            trend_pct = round(score_change / max(1, abs(previous_score)) * 100, 1) if previous_score else 0

            records.append({
                "performance_id": f"PERF{perf_id:04d}",
                "employee_id": emp["employee_id"],
                "period_start": month_start.isoformat(),
                "period_end": month_end.isoformat(),
                "kpi_score": round(kpi_weighted, 1),
                "feedback_score": round(fb_score, 1),
                "goal_score": round(goal_score, 1),
                "skill_score": round(skill_score, 1),
                "overall_score": overall,
                "previous_score": round(previous_score, 1) if previous_score is not None else "",
                "score_change": score_change,
                "trend_percentage": trend_pct,
            })
            previous_score = overall
    return records


# ============================================================
# O*NET CSV GENERATOR
# ============================================================
def generate_onet_csvs():
    # Occupations
    occ_records = [{"occupation_code": o[0], "occupation_title": o[1], "description": o[2]}
                   for o in ONET_OCCUPATIONS_DATA]

    # Skills
    skill_records = [{"element_id": s[0], "element_name": s[1], "category": "Skills",
                      "description": s[2]} for s in ONET_SKILL_ELEMENTS]

    # Occupation-Skills
    occ_skill_records = []
    for occ_code, ratings in ONET_OCC_SKILL_RATINGS.items():
        for elem_id, (importance, level) in ratings.items():
            elem_name = next((s[1] for s in ONET_SKILL_ELEMENTS if s[0] == elem_id), elem_id)
            occ_skill_records.append({
                "occupation_code": occ_code, "element_id": elem_id,
                "element_name": elem_name, "scale_id": "IM",
                "data_value": importance, "recommend_suppress": "N",
            })
            occ_skill_records.append({
                "occupation_code": occ_code, "element_id": elem_id,
                "element_name": elem_name, "scale_id": "LV",
                "data_value": level, "recommend_suppress": "N",
            })

    # Knowledge
    knowledge_records = [{"element_id": k[0], "element_name": k[1], "category": "Knowledge",
                          "description": k[2]} for k in ONET_KNOWLEDGE_ELEMENTS]

    # Abilities
    ability_records = [{"element_id": a[0], "element_name": a[1], "category": "Abilities",
                        "description": a[2]} for a in ONET_ABILITY_ELEMENTS]

    # Tasks
    task_templates = {
        "15-1252.00": [
            "Analyze user requirements to derive software design and performance requirements.",
            "Design and develop software systems using scientific analysis and mathematical models.",
            "Modify existing software to correct errors, adapt to new hardware, or improve performance.",
            "Develop and direct software system testing and validation procedures.",
            "Consult with engineering staff to evaluate software-hardware interfaces.",
        ],
        "15-1254.00": [
            "Design, build, or maintain websites using authoring or scripting languages.",
            "Write, design, or edit web page content, or direct others producing content.",
            "Identify problems uncovered by testing or customer feedback, and correct or refer for correction.",
            "Evaluate code to ensure it is valid, properly structured, and meets industry standards.",
        ],
        "15-2051.00": [
            "Apply data mining, machine learning, and statistical analysis techniques.",
            "Develop custom software solutions and data models.",
            "Build and validate predictive models using large datasets.",
            "Communicate complex analytical findings to stakeholders.",
        ],
        "11-3021.00": [
            "Direct daily operations of information technology department.",
            "Develop and manage IT budgets and strategic plans.",
            "Plan, coordinate, and implement network security measures.",
            "Manage and mentor IT staff and technical teams.",
        ],
    }
    task_records = []
    task_id = 0
    for occ_code, task_list in task_templates.items():
        for task_desc in task_list:
            task_id += 1
            task_records.append({
                "occupation_code": occ_code,
                "task_id": f"ONET_TASK_{task_id:03d}",
                "task_description": task_desc,
            })

    return occ_records, skill_records, occ_skill_records, knowledge_records, ability_records, task_records


# ============================================================
# JOB GENERATOR
# ============================================================
def generate_jobs(departments, roles):
    role_lookup = {r["role_id"]: r for r in roles}
    job_data = []
    for i in range(1, 31):
        role = role_lookup[random.choice(list(role_lookup.keys()))]
        dept_id = role["department_id"]
        seniority = role["seniority_level"]
        min_exp = role["minimum_experience_years"]
        max_exp = min_exp + random.randint(3, 8)

        salary_ranges = {
            "Junior": (400000, 800000), "Mid": (800000, 1800000), "Senior": (1500000, 3500000),
        }
        sal_lo, sal_hi = salary_ranges.get(seniority, (600000, 1500000))

        created = rand_date(date(2026, 3, 1), date(2026, 8, 1))
        closing = created + timedelta(days=random.randint(30, 90))
        status = "open" if closing > date(2026, 9, 15) else random.choice(["open", "closed", "filled"])

        job_data.append({
            "job_id": f"JOB{i:03d}",
            "job_title": f"{role['seniority_level']} {role['role_name']}",
            "department_id": dept_id,
            "role_id": role["role_id"],
            "job_description": f"Looking for a {seniority.lower()} {role['role_name']} to join our {dept_id} team.",
            "seniority_level": seniority,
            "employment_type": "full_time",
            "location": random.choice(LOCATIONS),
            "work_mode": random.choice(["onsite", "remote", "hybrid"]),
            "minimum_experience_years": min_exp,
            "maximum_experience_years": max_exp,
            "education_requirement": random.choice(["Bachelor's", "Master's", "Any"]),
            "salary_min": sal_lo,
            "salary_max": sal_hi,
            "status": status,
            "created_date": created.isoformat(),
            "closing_date": closing.isoformat(),
        })
    return job_data


# ============================================================
# JOB REQUIREMENTS GENERATOR
# ============================================================
def generate_job_requirements(jobs, skills_data):
    records = []
    jr_id = 0
    for job in jobs:
        role_id = job["role_id"]
        role_skills = ROLE_SKILLS.get(role_id, SKILL_IDS[:8])

        # Select 6-10 skills for the job
        n_skills = min(len(role_skills), random.randint(6, 10))
        chosen_skills = random.sample(role_skills, n_skills)

        # Distribute weights to sum to 1.0
        raw_weights = [random.uniform(0.08, 0.25) for _ in chosen_skills]
        weight_sum = sum(raw_weights)
        normalized_weights = [round(w / weight_sum, 2) for w in raw_weights]
        # Fix rounding to ensure sum is 1.0
        diff = round(1.0 - sum(normalized_weights), 2)
        normalized_weights[0] = round(normalized_weights[0] + diff, 2)

        n_mandatory = max(3, n_skills // 2)
        for idx, skill_id in enumerate(chosen_skills):
            jr_id += 1
            is_mandatory = idx < n_mandatory
            req_type = "required" if is_mandatory else "preferred"

            if is_mandatory:
                prof_level = random.choice(["Intermediate", "Advanced", "Expert"])
            else:
                prof_level = random.choice(["Beginner", "Basic", "Intermediate", "Advanced"])

            prof_score = PROFICIENCY_MAP[prof_level]
            min_years = random.randint(1, 4) if is_mandatory else random.randint(0, 2)

            records.append({
                "job_requirement_id": f"JR{jr_id:04d}",
                "job_id": job["job_id"],
                "skill_id": skill_id,
                "required_proficiency": prof_level,
                "required_proficiency_score": prof_score,
                "weight": normalized_weights[idx],
                "is_mandatory": str(is_mandatory).lower(),
                "requirement_type": req_type,
                "minimum_years": min_years,
                "description": f"Proficiency in {SKILL_MAP.get(skill_id, skill_id)}",
            })
    return records


# ============================================================
# CANDIDATE GENERATOR (300)
# ============================================================
def generate_candidates():
    records = []
    used_names = set()
    statuses_dist = (
        ["applied"] * 60 + ["screening"] * 40 + ["interview"] * 70 +
        ["shortlisted"] * 50 + ["rejected"] * 55 + ["hired"] * 25
    )
    sources = ["linkedin", "naukri", "referral", "company_website", "indeed", "campus", "recruiter"]

    for i in range(1, 301):
        gender = random.choice(["Male", "Female"])
        first = random.choice(MALE_FIRST if gender == "Male" else FEMALE_FIRST)
        last = random.choice(LAST_NAMES)
        while (first, last) in used_names:
            first = random.choice(MALE_FIRST if gender == "Male" else FEMALE_FIRST)
            last = random.choice(LAST_NAMES)
        used_names.add((first, last))

        archetype = assign_archetype(CAND_ARCHETYPES)
        total_exp = random.uniform(0.5, 18)
        if archetype in ("junior_talented", "good_interview_limited_exp"):
            total_exp = random.uniform(0.5, 3)
        elif archetype in ("experienced_skill_gaps", "strong_all_around"):
            total_exp = random.uniform(5, 18)

        ed_levels = ["Bachelor's", "Master's", "PhD", "Diploma"]
        ed_weights = [45, 35, 10, 10]
        ed_level = random.choices(ed_levels, weights=ed_weights, k=1)[0]

        ed_fields = ["Computer Science", "Information Technology", "Electronics",
                     "Business Administration", "Marketing", "Finance",
                     "Data Science", "Mathematics", "Statistics",
                     "Human Resource Management", "Commerce", "Psychology"]

        status = random.choice(statuses_dist)
        app_date = rand_date(date(2026, 3, 1), date(2026, 9, 15))

        current_roles = ["Software Engineer", "Senior Developer", "Data Analyst",
                         "Marketing Executive", "Sales Associate", "HR Coordinator",
                         "DevOps Engineer", "QA Analyst", "Product Analyst",
                         "Business Analyst", "Frontend Developer", "Backend Developer",
                         "Data Scientist", "System Administrator", "Financial Analyst"]

        records.append({
            "candidate_id": f"CAN{i:03d}",
            "candidate_code": f"C{i:03d}",
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}{i}@gmail.com",
            "phone": gen_phone(),
            "location": random.choice(LOCATIONS + ["Remote", "Coimbatore", "Indore", "Lucknow", "Nagpur"]),
            "total_experience_years": round(total_exp, 1),
            "highest_education": ed_level,
            "education_field": random.choice(ed_fields),
            "current_role": random.choice(current_roles),
            "resume_file": f"resumes/CAN{i:03d}_resume.pdf",
            "application_date": app_date.isoformat(),
            "source": random.choice(sources),
            "status": status,
            "_archetype": archetype,
        })
    return records


# ============================================================
# CANDIDATE SKILLS GENERATOR (1500+)
# ============================================================
def generate_candidate_skills(candidates, skills_data):
    records = []
    cs_id = 0
    evidence_templates = {
        "resume": [
            "Mentioned {skill} in resume with {years} years experience.",
            "Listed {skill} as key skill in resume.",
            "Resume highlights {skill} expertise in multiple projects.",
        ],
        "project": [
            "Built REST APIs using {skill} for an e-commerce platform.",
            "Developed data pipeline using {skill} processing 1M+ records daily.",
            "Created {skill}-based microservices serving 10K+ requests/sec.",
            "Implemented {skill} solution for real-time analytics dashboard.",
        ],
        "certification": [
            "Holds {skill} certification from recognized institution.",
            "Completed advanced {skill} certification course.",
        ],
        "interview": [
            "Demonstrated strong {skill} knowledge during technical interview.",
            "Answered {skill} related questions with practical examples.",
        ],
        "assessment": [
            "Scored {score}% in {skill} assessment test.",
            "Completed {skill} coding challenge with above-average performance.",
        ],
    }

    for cand in candidates:
        archetype = cand["_archetype"]
        arc = CAND_ARCHETYPES[archetype]
        n_skills = random.randint(4, 8)
        chosen = random.sample(SKILL_IDS, n_skills)

        for skill_id in chosen:
            cs_id += 1
            prof_base = arc_val(arc, "proficiency", noise=10)

            if prof_base >= 85:
                level = "Expert"
            elif prof_base >= 70:
                level = "Advanced"
            elif prof_base >= 50:
                level = "Intermediate"
            elif prof_base >= 30:
                level = "Basic"
            else:
                level = "Beginner"

            prof_score = PROFICIENCY_MAP[level] + random.randint(-5, 5)
            prof_score = clamp(prof_score, 10, 100)

            source = random.choice(["resume", "project", "certification", "interview", "assessment"])
            templates = evidence_templates[source]
            evidence = random.choice(templates).format(
                skill=SKILL_MAP.get(skill_id, "technology"),
                years=random.randint(1, 5),
                score=random.randint(60, 95)
            )

            confidence = round(random.uniform(0.5, 1.0) if source in ("certification", "assessment") else random.uniform(0.3, 0.85), 2)
            verified = random.choice(["verified", "unverified", "pending"])

            records.append({
                "candidate_skill_id": f"CS{cs_id:05d}",
                "candidate_id": cand["candidate_id"],
                "skill_id": skill_id,
                "proficiency_level": level,
                "proficiency_score": round(prof_score),
                "years_experience": round(random.uniform(0.5, min(float(cand["total_experience_years"]), 10)), 1),
                "evidence_text": evidence,
                "evidence_source": source,
                "confidence_score": confidence,
                "verification_status": verified,
            })
    return records


# ============================================================
# CANDIDATE EXPERIENCE GENERATOR (600+)
# ============================================================
def generate_candidate_experience(candidates):
    records = []
    exp_id = 0
    domains = ["Technology", "E-commerce", "Finance", "Healthcare", "Education",
               "Telecommunications", "Manufacturing", "Consulting", "Media", "Retail"]
    tech_sets = [
        "Python,Django,PostgreSQL", "Java,Spring Boot,MySQL", "React,Node.js,MongoDB",
        "Python,FastAPI,Redis", "Angular,TypeScript,.NET", "AWS,Docker,Kubernetes",
        "Python,TensorFlow,Spark", "Salesforce,JavaScript,SQL", "Go,gRPC,Kubernetes",
        "React Native,Firebase,Node.js", "Python,Pandas,Tableau",
    ]

    for cand in candidates:
        total_exp = float(cand["total_experience_years"])
        n_roles = max(1, min(4, int(total_exp / 2.5)))
        remaining_exp = total_exp

        for j in range(n_roles):
            exp_id += 1
            if j == n_roles - 1:
                duration = max(6, int(remaining_exp * 12))
            else:
                duration = random.randint(12, max(12, int(remaining_exp * 12 * 0.5)))
                remaining_exp -= duration / 12

            end_year = 2026 - int(sum(1 for k in range(j)) * duration / 12)
            end_date = date(min(2026, max(2020, end_year)), random.randint(1, 12), 1)
            start_date = end_date - timedelta(days=duration * 30)

            titles = ["Software Engineer", "Senior Software Engineer", "Data Analyst",
                      "Marketing Executive", "Sales Associate", "HR Executive",
                      "DevOps Engineer", "QA Engineer", "Product Analyst",
                      "Business Analyst", "Team Lead", "Junior Developer",
                      "Associate Consultant", "Analyst", "Systems Engineer"]

            records.append({
                "experience_id": f"EXP{exp_id:04d}",
                "candidate_id": cand["candidate_id"],
                "company": random.choice(COMPANIES),
                "job_title": random.choice(titles),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat() if j > 0 else "",
                "duration_months": duration,
                "description": f"Worked as part of the technology team delivering solutions.",
                "technologies": random.choice(tech_sets),
                "responsibilities": "Development, testing, code review, and deployment.",
                "domain": random.choice(domains),
            })
    return records


# ============================================================
# CANDIDATE EDUCATION GENERATOR
# ============================================================
def generate_candidate_education(candidates):
    records = []
    ed_id = 0
    institutions = UNIVERSITIES + [
        "IIM Ahmedabad", "IIM Bangalore", "IIM Calcutta", "XLRI Jamshedpur",
        "FMS Delhi", "SP Jain Mumbai", "Presidency University", "St. Xavier's College",
        "Loyola College Chennai", "Fergusson College Pune",
    ]
    for cand in candidates:
        # Primary degree
        ed_id += 1
        ed_level = cand["highest_education"]
        if ed_level == "PhD":
            degrees = [
                ("PhD", cand["education_field"], "PhD"),
                ("Master's", cand["education_field"], "Master's"),
                ("Bachelor's", cand["education_field"], "Bachelor's"),
            ]
        elif ed_level == "Master's":
            degrees = [
                ("Master's", cand["education_field"], "Master's"),
                ("Bachelor's", cand["education_field"], "Bachelor's"),
            ]
        elif ed_level == "Diploma":
            degrees = [("Diploma", cand["education_field"], "Diploma")]
        else:
            degrees = [("Bachelor's", cand["education_field"], "Bachelor's")]

        for deg, field, level in degrees:
            ed_id += 1
            end_year = 2026 - int(float(cand["total_experience_years"])) - random.randint(0, 2)
            start_year = end_year - (4 if deg == "Bachelor's" else 2 if deg in ("Master's", "Diploma") else 3)
            grade_options = ["8.5 CGPA", "9.0 CGPA", "7.8 CGPA", "8.2 CGPA", "7.5 CGPA",
                            "First Class", "Distinction", "Second Class", "85%", "78%", "92%"]
            records.append({
                "education_id": f"ED{ed_id:04d}",
                "candidate_id": cand["candidate_id"],
                "degree": deg,
                "field": field,
                "institution": random.choice(institutions),
                "start_year": max(2005, start_year),
                "end_year": max(2009, end_year),
                "grade": random.choice(grade_options),
                "education_level": level,
            })
    return records


# ============================================================
# CANDIDATE CERTIFICATIONS GENERATOR
# ============================================================
def generate_candidate_certifications(candidates, skills_data):
    records = []
    cert_id = 0
    cert_pool = [
        ("AWS Solutions Architect Associate", "Amazon Web Services", "SKILL_036"),
        ("AWS Developer Associate", "Amazon Web Services", "SKILL_036"),
        ("Microsoft Azure Fundamentals", "Microsoft", "SKILL_037"),
        ("Google Cloud Professional Data Engineer", "Google", "SKILL_038"),
        ("Certified Kubernetes Administrator", "CNCF", "SKILL_040"),
        ("Docker Certified Associate", "Docker Inc", "SKILL_039"),
        ("PMP Certification", "PMI", "SKILL_067"),
        ("Certified Scrum Master", "Scrum Alliance", "SKILL_064"),
        ("CISSP", "ISC2", "SKILL_058"),
        ("CompTIA Security+", "CompTIA", "SKILL_058"),
        ("TensorFlow Developer Certificate", "Google", "SKILL_051"),
        ("Salesforce Administrator", "Salesforce", "SKILL_086"),
        ("Google Analytics Certification", "Google", "SKILL_136"),
        ("HubSpot Inbound Marketing", "HubSpot", "SKILL_087"),
        ("SHRM-CP", "SHRM", "SKILL_094"),
        ("Six Sigma Green Belt", "ASQ", "SKILL_102"),
        ("Oracle Database Administrator", "Oracle", "SKILL_033"),
        ("Tableau Desktop Specialist", "Tableau", "SKILL_056"),
        ("MongoDB Developer", "MongoDB", "SKILL_030"),
        ("React Developer Certification", "Meta", "SKILL_016"),
    ]

    for cand in candidates:
        n_certs = random.choices([0, 1, 2, 3], weights=[30, 35, 25, 10], k=1)[0]
        if n_certs == 0:
            continue

        chosen = random.sample(cert_pool, min(n_certs, len(cert_pool)))
        for cert_name, org, skill_id in chosen:
            cert_id += 1
            issue_date = rand_date(date(2022, 1, 1), date(2026, 6, 30))
            expiry = issue_date + timedelta(days=random.choice([365, 730, 1095, 0]))
            records.append({
                "certification_id": f"CERT{cert_id:04d}",
                "candidate_id": cand["candidate_id"],
                "certification_name": cert_name,
                "issuing_organization": org,
                "issue_date": issue_date.isoformat(),
                "expiry_date": expiry.isoformat() if expiry != issue_date else "",
                "verification_status": random.choice(["verified", "unverified", "pending"]),
                "related_skill_id": skill_id,
            })
    return records


# ============================================================
# CANDIDATE PROJECTS GENERATOR (600+)
# ============================================================
def generate_candidate_projects(candidates):
    records = []
    cp_id = 0
    project_templates = [
        ("E-commerce Platform", "Built a full-stack e-commerce platform with payment integration", "Backend Developer", "Python,Django,PostgreSQL,Redis", "E-commerce"),
        ("Real-time Chat Application", "Developed a WebSocket-based chat application with group messaging", "Full Stack Developer", "Node.js,React,MongoDB,Socket.io", "Communication"),
        ("ML Recommendation Engine", "Built a collaborative filtering recommendation system", "ML Engineer", "Python,TensorFlow,AWS,PostgreSQL", "Technology"),
        ("CRM Dashboard", "Created an analytics dashboard for sales team performance tracking", "Frontend Developer", "React,TypeScript,D3.js,REST API", "Business"),
        ("CI/CD Pipeline Automation", "Automated build-test-deploy pipelines for microservices", "DevOps Engineer", "Jenkins,Docker,Kubernetes,Terraform", "Infrastructure"),
        ("Inventory Management System", "Designed and built an inventory tracking system", "Software Engineer", "Java,Spring Boot,MySQL,React", "Manufacturing"),
        ("Social Media Analytics", "Built a data pipeline for social media sentiment analysis", "Data Engineer", "Python,Kafka,Spark,Elasticsearch", "Media"),
        ("Mobile Banking App", "Developed a secure mobile banking application", "Mobile Developer", "React Native,Node.js,PostgreSQL", "Finance"),
        ("Healthcare Portal", "Patient management and appointment scheduling system", "Full Stack Developer", "Django,React,PostgreSQL,Docker", "Healthcare"),
        ("API Gateway Service", "Built a centralized API gateway with rate limiting and auth", "Backend Developer", "Go,Redis,Docker,Kubernetes", "Technology"),
        ("HR Onboarding System", "Automated employee onboarding workflow system", "Software Engineer", "Python,FastAPI,React,PostgreSQL", "HR"),
        ("Sales Forecasting Model", "ML-based sales prediction model with 92% accuracy", "Data Scientist", "Python,Scikit-learn,Pandas,Tableau", "Business"),
        ("Content Management System", "Custom CMS for managing digital content and publishing", "Full Stack Developer", "Django,React,AWS S3,Elasticsearch", "Media"),
        ("Network Monitoring Tool", "Real-time network monitoring and alerting system", "DevOps Engineer", "Python,Prometheus,Grafana,Docker", "Infrastructure"),
        ("Customer Support Bot", "AI-powered customer support chatbot with NLP", "ML Engineer", "Python,NLP,FastAPI,React", "Customer Service"),
    ]
    complexities = ["low", "medium", "high", "very_high"]
    outcomes = ["successful", "completed", "partially_completed", "ongoing"]
    evidence_sources = ["github", "portfolio", "resume", "demo", "documentation"]

    for cand in candidates:
        archetype = cand["_archetype"]
        arc = CAND_ARCHETYPES[archetype]
        n_projects = random.randint(1, 4)
        chosen = random.sample(project_templates, min(n_projects, len(project_templates)))

        for name, desc, role, tech, domain in chosen:
            cp_id += 1
            duration = random.randint(2, 12)
            complexity = random.choices(complexities, weights=[20, 40, 30, 10], k=1)[0]

            records.append({
                "candidate_project_id": f"CP{cp_id:04d}",
                "candidate_id": cand["candidate_id"],
                "project_name": name,
                "description": desc,
                "role": role,
                "technologies": tech,
                "domain": domain,
                "duration_months": duration,
                "complexity": complexity,
                "outcome": random.choices(outcomes, weights=[50, 30, 15, 5], k=1)[0],
                "evidence_source": random.choice(evidence_sources),
            })
    return records


# ============================================================
# INTERVIEW GENERATOR (150+ interviews, 600+ questions, 600+ answers)
# ============================================================
def generate_interviews(candidates, jobs, employees):
    interviews = []
    questions = []
    answers = []
    int_id = 0
    q_id = 0
    a_id = 0

    # Only candidates who reached interview stage or beyond
    interviewable = [c for c in candidates
                     if c["status"] in ("interview", "shortlisted", "hired", "rejected")]
    random.shuffle(interviewable)
    interviewable = interviewable[:180]  # Ensure 150+ interviews

    # Interviewers: employees in manager or senior roles
    interviewers = [e for e in employees
                    if e["_role_id"] in ("ROLE004", "ROLE007", "ROLE009", "ROLE012", "ROLE014")]
    if not interviewers:
        interviewers = employees[:10]

    question_templates = {
        "technical": [
            "Explain the concept of {topic} and its applications.",
            "How would you design a scalable {topic} solution?",
            "What are the trade-offs between {topic} approaches?",
            "Describe your experience with {topic} in production systems.",
            "Walk through how you would implement {topic}.",
        ],
        "behavioral": [
            "Describe a challenging project you worked on and how you handled it.",
            "How do you handle disagreements with team members?",
            "Tell me about a time you failed and what you learned.",
            "How do you prioritize tasks when dealing with multiple deadlines?",
        ],
        "problem_solving": [
            "Design a system that handles {topic} at scale.",
            "How would you optimize a slow {topic} query?",
            "What approach would you take to debug a {topic} issue?",
        ],
    }
    topics = ["microservices", "database", "caching", "API design", "authentication",
              "data pipeline", "machine learning", "CI/CD", "cloud architecture",
              "load balancing", "message queue", "search indexing"]

    for cand in interviewable:
        archetype = cand["_archetype"]
        arc = CAND_ARCHETYPES[archetype]
        job = random.choice(jobs)
        n_rounds = random.randint(1, 3)

        for round_num in range(1, n_rounds + 1):
            int_id += 1
            interviewer = random.choice(interviewers)
            int_date = rand_date(date(2026, 4, 1), date(2026, 9, 1))
            int_status = random.choice(["completed", "completed", "completed", "scheduled", "cancelled"])

            interviews.append({
                "interview_id": f"INT{int_id:04d}",
                "candidate_id": cand["candidate_id"],
                "job_id": job["job_id"],
                "interview_round": round_num,
                "interviewer_id": interviewer["employee_id"],
                "interview_date": int_date.isoformat(),
                "status": int_status,
            })

            if int_status != "completed":
                continue

            # 3-5 questions per interview
            n_questions = random.randint(3, 5)
            role_skills = ROLE_SKILLS.get(job["role_id"], SKILL_IDS[:8])

            for _ in range(n_questions):
                q_id += 1
                q_type = random.choices(["technical", "behavioral", "problem_solving"],
                                       weights=[50, 25, 25], k=1)[0]
                skill_id = random.choice(role_skills)
                topic = random.choice(topics)
                template = random.choice(question_templates[q_type])
                question_text = template.format(topic=topic)
                difficulty = random.choice(["easy", "medium", "hard", "expert"])

                questions.append({
                    "question_id": f"Q{q_id:04d}",
                    "interview_id": f"INT{int_id:04d}",
                    "skill_id": skill_id,
                    "question": question_text,
                    "difficulty": difficulty,
                    "question_type": q_type,
                })

                # Generate answer
                a_id += 1
                interview_base = arc_val(arc, "interview", noise=10)

                # Scale ratings 0-10
                def int_rating():
                    base = interview_base / 10  # 0-10 scale
                    return round(clamp(base + random.uniform(-1, 1), 1, 10), 1)

                tech_correct = int_rating()
                conceptual = int_rating()
                ps = int_rating()
                practical = int_rating()
                comm = int_rating()

                # For archetypes with specific weaknesses
                if archetype == "strong_tech_weak_soft":
                    comm = round(clamp(comm * 0.6, 1, 10), 1)
                elif archetype == "good_resume_weak_interview":
                    tech_correct = round(clamp(tech_correct * 0.7, 1, 10), 1)
                    ps = round(clamp(ps * 0.7, 1, 10), 1)

                answers.append({
                    "answer_id": f"A{a_id:04d}",
                    "question_id": f"Q{q_id:04d}",
                    "candidate_id": cand["candidate_id"],
                    "answer_text": f"Candidate provided a detailed response about {topic}.",
                    "technical_correctness": tech_correct,
                    "conceptual_understanding": conceptual,
                    "problem_solving": ps,
                    "practical_reasoning": practical,
                    "communication": comm,
                    "evidence": f"Demonstrated understanding of {SKILL_MAP.get(skill_id, 'technology')}",
                    "ai_confidence": round(random.uniform(0.6, 0.95), 2),
                })

    return interviews, questions, answers


# ============================================================
# CANDIDATE-JOB SCORES GENERATOR
# ============================================================
def generate_candidate_job_scores(candidates, jobs, cand_skills, cand_exp,
                                   cand_projects, interviews, int_questions, int_answers,
                                   job_requirements, cand_education):
    records = []
    match_id = 0

    # Build lookups
    cand_skills_map = defaultdict(list)
    for cs in cand_skills:
        cand_skills_map[cs["candidate_id"]].append(cs)

    cand_exp_map = defaultdict(list)
    for ce in cand_exp:
        cand_exp_map[ce["candidate_id"]].append(ce)

    cand_proj_map = defaultdict(list)
    for cp in cand_projects:
        cand_proj_map[cp["candidate_id"]].append(cp)

    cand_edu_map = defaultdict(list)
    for ce in cand_education:
        cand_edu_map[ce["candidate_id"]].append(ce)

    job_req_map = defaultdict(list)
    for jr in job_requirements:
        job_req_map[jr["job_id"]].append(jr)

    # Interview results by candidate+job
    int_by_cand_job = defaultdict(list)
    for iv in interviews:
        if iv["status"] == "completed":
            int_by_cand_job[(iv["candidate_id"], iv["job_id"])].append(iv)

    ans_by_interview = defaultdict(list)
    for ans in int_answers:
        # Find question to get interview_id
        q_match = next((q for q in int_questions if q["question_id"] == ans["question_id"]), None)
        if q_match:
            ans_by_interview[q_match["interview_id"]].append(ans)

    # Assign each candidate to 1-2 jobs for scoring
    for cand in candidates:
        archetype = cand["_archetype"]
        arc = CAND_ARCHETYPES[archetype]
        n_jobs = random.randint(1, 2)
        target_jobs = random.sample(jobs, min(n_jobs, len(jobs)))

        for job in target_jobs:
            match_id += 1
            reqs = job_req_map.get(job["job_id"], [])

            # Required skill match score
            c_skills = {cs["skill_id"]: cs for cs in cand_skills_map.get(cand["candidate_id"], [])}
            mandatory_reqs = [r for r in reqs if r["is_mandatory"] == "true"]
            met_mandatory = sum(1 for r in mandatory_reqs if r["skill_id"] in c_skills)
            failed_mandatory = len(mandatory_reqs) - met_mandatory

            if reqs:
                skill_match_scores = []
                for r in reqs:
                    if r["skill_id"] in c_skills:
                        cs = c_skills[r["skill_id"]]
                        match_pct = min(100, float(cs["proficiency_score"]) / max(1, float(r["required_proficiency_score"])) * 100)
                        skill_match_scores.append(match_pct * float(r["weight"]))
                    else:
                        skill_match_scores.append(0)
                req_skill_score = round(sum(skill_match_scores) / max(0.01, sum(float(r["weight"]) for r in reqs)) if reqs else 0, 1)
            else:
                req_skill_score = arc_val(arc, "skill_match", noise=5)

            # Skill proficiency
            if c_skills:
                avg_prof = sum(float(cs["proficiency_score"]) for cs in c_skills.values()) / len(c_skills)
                skill_prof_score = round(clamp(avg_prof), 1)
            else:
                skill_prof_score = round(arc_val(arc, "proficiency", noise=5), 1)

            # Experience score
            cand_exps = cand_exp_map.get(cand["candidate_id"], [])
            total_months = sum(int(ce.get("duration_months", 12)) for ce in cand_exps)
            min_exp_years = float(job.get("minimum_experience_years", 2))
            exp_ratio = total_months / 12 / max(1, min_exp_years)
            experience_score = round(clamp(min(100, exp_ratio * 80 + random.uniform(-5, 5))), 1)

            # Project relevance
            projs = cand_proj_map.get(cand["candidate_id"], [])
            if projs:
                relevance_scores = []
                for p in projs:
                    p_techs = set(p.get("technologies", "").split(","))
                    job_techs = set()
                    for r in reqs:
                        job_techs.add(SKILL_MAP.get(r["skill_id"], ""))
                    overlap = len(p_techs & job_techs)
                    relevance_scores.append(min(100, overlap * 25 + random.uniform(20, 50)))
                project_score = round(sum(relevance_scores) / len(relevance_scores), 1)
            else:
                project_score = round(arc_val(arc, "projects", noise=8), 1)

            # Interview score
            cand_ints = int_by_cand_job.get((cand["candidate_id"], job["job_id"]), [])
            if cand_ints:
                all_answers = []
                for iv in cand_ints:
                    all_answers.extend(ans_by_interview.get(iv["interview_id"], []))
                if all_answers:
                    int_avg = sum(
                        (float(a["technical_correctness"]) + float(a["conceptual_understanding"]) +
                         float(a["problem_solving"]) + float(a["practical_reasoning"]) +
                         float(a["communication"])) / 5
                        for a in all_answers
                    ) / len(all_answers)
                    interview_score = round(int_avg * 10, 1)  # Scale 0-10 to 0-100
                else:
                    interview_score = round(arc_val(arc, "interview", noise=8), 1)
            else:
                interview_score = round(arc_val(arc, "interview", noise=8), 1)

            # Problem solving (from interview answers)
            if cand_ints and all_answers:
                ps_avg = sum(float(a["problem_solving"]) for a in all_answers) / len(all_answers)
                ps_score = round(ps_avg * 10, 1)
            else:
                ps_score = round(arc_val(arc, "interview", noise=10), 1)

            # Education score
            edus = cand_edu_map.get(cand["candidate_id"], [])
            ed_req = job.get("education_requirement", "Any")
            if ed_req == "Any" or not edus:
                ed_score = round(arc_val(arc, "education", noise=5), 1)
            else:
                ed_levels = {"Diploma": 1, "Bachelor's": 2, "Master's": 3, "PhD": 4}
                max_ed = max(ed_levels.get(e["education_level"], 1) for e in edus)
                req_ed = ed_levels.get(ed_req, 2)
                if max_ed >= req_ed:
                    ed_score = round(clamp(70 + random.uniform(0, 25)), 1)
                else:
                    ed_score = round(clamp(30 + random.uniform(0, 30)), 1)

            # Overall match score (configurable weights)
            overall = round(clamp(
                req_skill_score * 0.30 +
                skill_prof_score * 0.15 +
                experience_score * 0.15 +
                project_score * 0.10 +
                interview_score * 0.15 +
                ps_score * 0.10 +
                ed_score * 0.05
            ), 1)

            records.append({
                "match_id": f"MATCH{match_id:04d}",
                "candidate_id": cand["candidate_id"],
                "job_id": job["job_id"],
                "required_skill_score": round(clamp(req_skill_score), 1),
                "skill_proficiency_score": skill_prof_score,
                "experience_score": experience_score,
                "project_relevance_score": round(clamp(project_score), 1),
                "interview_score": round(clamp(interview_score), 1),
                "problem_solving_score": round(clamp(ps_score), 1),
                "education_score": round(clamp(ed_score), 1),
                "overall_match_score": overall,
                "mandatory_requirements_met": met_mandatory,
                "mandatory_requirements_failed": failed_mandatory,
                "calculation_version": "1.0",
                "calculated_at": "2026-09-15T12:00:00",
            })
    return records


# ============================================================
# CANDIDATE EVIDENCE GENERATOR
# ============================================================
def generate_candidate_evidence(candidates, jobs, cand_skills, cand_exp,
                                 cand_projects, cand_certs):
    records = []
    ev_id = 0
    types = ["resume", "project", "experience", "certification", "interview", "assessment"]

    # Create evidence from skills
    for cs in cand_skills:
        ev_id += 1
        records.append({
            "evidence_id": f"EV{ev_id:05d}",
            "candidate_id": cs["candidate_id"],
            "job_id": "",
            "skill_id": cs["skill_id"],
            "evidence_type": cs["evidence_source"],
            "source_document": cs["evidence_source"],
            "source_text": cs["evidence_text"],
            "evidence_strength": random.choice(["strong", "moderate", "weak"]),
            "confidence_score": cs["confidence_score"],
            "created_at": "2026-09-15T10:00:00",
        })

    # Sample from certifications
    for cert in cand_certs[:200]:
        ev_id += 1
        records.append({
            "evidence_id": f"EV{ev_id:05d}",
            "candidate_id": cert["candidate_id"],
            "job_id": "",
            "skill_id": cert["related_skill_id"],
            "evidence_type": "certification",
            "source_document": "certification",
            "source_text": f"Holds {cert['certification_name']} from {cert['issuing_organization']}",
            "evidence_strength": "strong",
            "confidence_score": 0.9,
            "created_at": "2026-09-15T10:00:00",
        })

    return records


# ============================================================
# SKILL TRAINING CATALOG GENERATOR
# ============================================================
def generate_training_catalog(skills_data):
    records = []
    tr_id = 0
    providers = ["Coursera", "Udemy", "LinkedIn Learning", "Pluralsight", "edX",
                 "Internal Academy", "AWS Training", "Google Cloud Training",
                 "Microsoft Learn", "DataCamp", "Simplilearn", "upGrad"]
    difficulties = ["beginner", "intermediate", "advanced", "expert"]

    training_templates = [
        "{skill} Fundamentals", "Advanced {skill}", "{skill} Masterclass",
        "{skill} for Professionals", "Practical {skill} Workshop",
        "{skill} Certification Prep", "{skill} Best Practices",
    ]

    for skill_id, skill_name, category, desc in skills_data[:80]:  # Top 80 skills
        n_trainings = random.randint(1, 3)
        chosen_templates = random.sample(training_templates, min(n_trainings, len(training_templates)))
        for template in chosen_templates:
            tr_id += 1
            records.append({
                "training_id": f"TC{tr_id:04d}",
                "skill_id": skill_id,
                "training_name": template.format(skill=skill_name),
                "description": f"Comprehensive training on {skill_name} ({desc})",
                "difficulty": random.choice(difficulties),
                "duration_hours": random.choice([4, 8, 16, 24, 32, 40, 60]),
                "provider": random.choice(providers),
            })
    return records


# ============================================================
# MAIN FUNCTION
# ============================================================
def main():
    print("=" * 60)
    print("Workforce Management Platform — Dataset Generator")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ONET_DIR, exist_ok=True)

    # ---- Phase 1: Foundation ----
    print("\n[Phase 1] Generating foundation data...")
    departments = generate_departments()
    roles = generate_roles()
    kpis = generate_kpis()
    role_kpis = generate_role_kpis(roles, kpis)
    skills = [{"skill_id": s[0], "skill_name": s[1], "category": s[2],
               "description": s[3]} for s in SKILLS_DATA]

    # ---- Phase 2: Employees ----
    print("\n[Phase 2] Generating employee data...")
    employees = generate_employees(departments, roles)
    projects = generate_projects(departments)
    employee_projects = generate_employee_projects(employees, projects)

    # ---- Phase 3: Performance Data ----
    print("\n[Phase 3] Generating performance data...")
    tasks = generate_tasks(employees, projects, employee_projects)
    quality_records = generate_quality_records(employees, tasks, projects)
    goals = generate_goals(employees)
    attendance = generate_attendance(employees)
    feedback = generate_feedback(employees)
    training = generate_training(employees, SKILLS_DATA)
    employee_skills = generate_employee_skills(employees, SKILLS_DATA)

    # ---- Phase 4: KPI & Performance History ----
    print("\n[Phase 4] Calculating KPI records and performance history...")
    kpi_records = generate_kpi_records(employees, role_kpis, tasks, goals,
                                        quality_records, attendance, feedback)
    perf_history = generate_performance_history(employees, kpi_records, role_kpis)

    # ---- Phase 5: O*NET ----
    print("\n[Phase 5] Generating O*NET data...")
    onet_occ, onet_skills, onet_occ_skills, onet_knowledge, onet_abilities, onet_tasks = generate_onet_csvs()

    # ---- Phase 6: Hiring Intelligence ----
    print("\n[Phase 6] Generating hiring intelligence data...")
    jobs = generate_jobs(departments, roles)
    job_requirements = generate_job_requirements(jobs, SKILLS_DATA)
    candidates = generate_candidates()
    cand_skills = generate_candidate_skills(candidates, SKILLS_DATA)
    cand_experience = generate_candidate_experience(candidates)
    cand_education = generate_candidate_education(candidates)
    cand_certifications = generate_candidate_certifications(candidates, SKILLS_DATA)
    cand_projects = generate_candidate_projects(candidates)
    interviews_data, int_questions, int_answers = generate_interviews(candidates, jobs, employees)
    cand_job_scores = generate_candidate_job_scores(
        candidates, jobs, cand_skills, cand_experience, cand_projects,
        interviews_data, int_questions, int_answers, job_requirements, cand_education)
    cand_evidence = generate_candidate_evidence(
        candidates, jobs, cand_skills, cand_experience, cand_projects, cand_certifications)

    # ---- Phase 7: Training Catalog ----
    print("\n[Phase 7] Generating training catalog...")
    training_catalog = generate_training_catalog(SKILLS_DATA)

    # ============================================================
    # WRITE ALL CSVs
    # ============================================================
    print("\n" + "=" * 60)
    print("Writing CSV files...")
    print("=" * 60)

    # Clean internal fields from employees
    emp_clean = []
    for e in employees:
        ec = {k: v for k, v in e.items() if not k.startswith("_")}
        emp_clean.append(ec)

    # Clean internal fields from candidates
    cand_clean = []
    for c in candidates:
        cc = {k: v for k, v in c.items() if not k.startswith("_")}
        cand_clean.append(cc)

    write_csv("departments.csv", departments,
              ["department_id", "department_name", "department_description", "department_head_id"])

    write_csv("roles.csv", roles,
              ["role_id", "role_name", "department_id", "role_description",
               "seniority_level", "minimum_experience_years"])

    write_csv("kpis.csv", kpis,
              ["kpi_id", "kpi_name", "description", "measurement_type",
               "default_direction", "calculation_method"])

    write_csv("role_kpis.csv", role_kpis,
              ["role_kpi_id", "role_id", "kpi_id", "weight", "target_value",
               "minimum_value", "maximum_value", "measurement_unit", "measurement_type",
               "direction", "is_mandatory", "active"])

    write_csv("employees.csv", emp_clean,
              ["employee_id", "employee_code", "first_name", "last_name", "email",
               "phone", "gender", "date_of_birth", "date_of_joining", "employment_status",
               "employment_type", "department_id", "role_id", "manager_id", "location",
               "work_mode", "current_salary", "experience_before_joining_years",
               "education_level", "education_field", "university", "current_level",
               "created_at", "updated_at"])

    write_csv("projects.csv", projects,
              ["project_id", "project_name", "department_id", "description",
               "project_type", "start_date", "end_date", "status",
               "business_priority", "technology_stack"])

    write_csv("employee_projects.csv", employee_projects,
              ["employee_project_id", "employee_id", "project_id", "role_in_project",
               "responsibility", "allocation_percentage", "start_date", "end_date",
               "contribution_score"])

    write_csv("employee_tasks.csv", tasks,
              ["task_id", "employee_id", "project_id", "assigned_date", "due_date",
               "completed_date", "status", "priority", "estimated_hours", "actual_hours",
               "quality_score", "rework_required", "rework_count", "complexity", "task_type"])

    write_csv("employee_quality_records.csv", quality_records,
              ["quality_record_id", "employee_id", "task_id", "project_id", "period",
               "total_items", "defects", "critical_defects", "minor_defects",
               "rework_count", "quality_rating", "reviewer_id"])

    write_csv("employee_goals.csv", goals,
              ["goal_id", "employee_id", "goal_title", "goal_description",
               "goal_category", "start_date", "due_date", "target_value",
               "actual_value", "achievement_percentage", "weight", "status", "manager_id"])

    write_csv("employee_attendance.csv", attendance,
              ["attendance_id", "employee_id", "date", "status", "scheduled_hours",
               "worked_hours", "leave_type", "late_minutes", "overtime_hours"])

    write_csv("employee_feedback.csv", feedback,
              ["feedback_id", "employee_id", "reviewer_id", "reviewer_role", "period",
               "technical_skill_rating", "communication_rating", "teamwork_rating",
               "problem_solving_rating", "leadership_rating", "overall_rating",
               "comment", "created_at"])

    write_csv("employee_training.csv", training,
              ["training_id", "employee_id", "training_name", "skill_id",
               "training_category", "start_date", "completion_date",
               "completion_percentage", "assessment_score", "status", "hours_spent"])

    write_csv("employee_skills.csv", employee_skills,
              ["employee_skill_id", "employee_id", "skill_id", "proficiency_level",
               "proficiency_score", "years_of_experience", "last_assessed_date",
               "assessment_method", "evidence_source"])

    write_csv("employee_kpi_records.csv", kpi_records,
              ["record_id", "employee_id", "role_kpi_id", "period_start", "period_end",
               "actual_value", "target_value", "normalized_score", "data_source",
               "source_record_id", "created_at"])

    write_csv("employee_performance_history.csv", perf_history,
              ["performance_id", "employee_id", "period_start", "period_end",
               "kpi_score", "feedback_score", "goal_score", "skill_score",
               "overall_score", "previous_score", "score_change", "trend_percentage"])

    # O*NET CSVs
    write_csv(os.path.join(ONET_DIR, "occupations.csv"), onet_occ,
              ["occupation_code", "occupation_title", "description"])
    write_csv(os.path.join(ONET_DIR, "skills.csv"), onet_skills,
              ["element_id", "element_name", "category", "description"])
    write_csv(os.path.join(ONET_DIR, "occupation_skills.csv"), onet_occ_skills,
              ["occupation_code", "element_id", "element_name", "scale_id",
               "data_value", "recommend_suppress"])
    write_csv(os.path.join(ONET_DIR, "knowledge.csv"), onet_knowledge,
              ["element_id", "element_name", "category", "description"])
    write_csv(os.path.join(ONET_DIR, "abilities.csv"), onet_abilities,
              ["element_id", "element_name", "category", "description"])
    write_csv(os.path.join(ONET_DIR, "tasks.csv"), onet_tasks,
              ["occupation_code", "task_id", "task_description"])

    # Hiring Intelligence CSVs
    write_csv("jobs.csv", jobs,
              ["job_id", "job_title", "department_id", "role_id", "job_description",
               "seniority_level", "employment_type", "location", "work_mode",
               "minimum_experience_years", "maximum_experience_years",
               "education_requirement", "salary_min", "salary_max", "status",
               "created_date", "closing_date"])

    write_csv("job_requirements.csv", job_requirements,
              ["job_requirement_id", "job_id", "skill_id", "required_proficiency",
               "required_proficiency_score", "weight", "is_mandatory",
               "requirement_type", "minimum_years", "description"])

    write_csv("candidates.csv", cand_clean,
              ["candidate_id", "candidate_code", "first_name", "last_name", "email",
               "phone", "location", "total_experience_years", "highest_education",
               "education_field", "current_role", "resume_file", "application_date",
               "source", "status"])

    write_csv("candidate_skills.csv", cand_skills,
              ["candidate_skill_id", "candidate_id", "skill_id", "proficiency_level",
               "proficiency_score", "years_experience", "evidence_text",
               "evidence_source", "confidence_score", "verification_status"])

    write_csv("candidate_experience.csv", cand_experience,
              ["experience_id", "candidate_id", "company", "job_title", "start_date",
               "end_date", "duration_months", "description", "technologies",
               "responsibilities", "domain"])

    write_csv("candidate_education.csv", cand_education,
              ["education_id", "candidate_id", "degree", "field", "institution",
               "start_year", "end_year", "grade", "education_level"])

    write_csv("candidate_certifications.csv", cand_certifications,
              ["certification_id", "candidate_id", "certification_name",
               "issuing_organization", "issue_date", "expiry_date",
               "verification_status", "related_skill_id"])

    write_csv("candidate_projects.csv", cand_projects,
              ["candidate_project_id", "candidate_id", "project_name", "description",
               "role", "technologies", "domain", "duration_months", "complexity",
               "outcome", "evidence_source"])

    write_csv("interviews.csv", interviews_data,
              ["interview_id", "candidate_id", "job_id", "interview_round",
               "interviewer_id", "interview_date", "status"])

    write_csv("interview_questions.csv", int_questions,
              ["question_id", "interview_id", "skill_id", "question",
               "difficulty", "question_type"])

    write_csv("interview_answers.csv", int_answers,
              ["answer_id", "question_id", "candidate_id", "answer_text",
               "technical_correctness", "conceptual_understanding", "problem_solving",
               "practical_reasoning", "communication", "evidence", "ai_confidence"])

    write_csv("candidate_job_scores.csv", cand_job_scores,
              ["match_id", "candidate_id", "job_id", "required_skill_score",
               "skill_proficiency_score", "experience_score", "project_relevance_score",
               "interview_score", "problem_solving_score", "education_score",
               "overall_match_score", "mandatory_requirements_met",
               "mandatory_requirements_failed", "calculation_version", "calculated_at"])

    write_csv("candidate_evidence.csv", cand_evidence,
              ["evidence_id", "candidate_id", "job_id", "skill_id", "evidence_type",
               "source_document", "source_text", "evidence_strength",
               "confidence_score", "created_at"])

    write_csv("skill_training_catalog.csv", training_catalog,
              ["training_id", "skill_id", "training_name", "description",
               "difficulty", "duration_hours", "provider"])

    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE — Summary")
    print("=" * 60)
    summary = {
        "Departments": len(departments),
        "Roles": len(roles),
        "KPIs": len(kpis),
        "Role KPIs": len(role_kpis),
        "Skills": len(skills),
        "Employees": len(emp_clean),
        "Projects": len(projects),
        "Employee Projects": len(employee_projects),
        "Employee Tasks": len(tasks),
        "Quality Records": len(quality_records),
        "Goals": len(goals),
        "Attendance Records": len(attendance),
        "Feedback Records": len(feedback),
        "Training Records": len(training),
        "Employee Skills": len(employee_skills),
        "KPI Records": len(kpi_records),
        "Performance History": len(perf_history),
        "O*NET Occupations": len(onet_occ),
        "O*NET Skills": len(onet_skills),
        "O*NET Occupation-Skills": len(onet_occ_skills),
        "O*NET Knowledge": len(onet_knowledge),
        "O*NET Abilities": len(onet_abilities),
        "O*NET Tasks": len(onet_tasks),
        "Jobs": len(jobs),
        "Job Requirements": len(job_requirements),
        "Candidates": len(cand_clean),
        "Candidate Skills": len(cand_skills),
        "Candidate Experience": len(cand_experience),
        "Candidate Education": len(cand_education),
        "Candidate Certifications": len(cand_certifications),
        "Candidate Projects": len(cand_projects),
        "Interviews": len(interviews_data),
        "Interview Questions": len(int_questions),
        "Interview Answers": len(int_answers),
        "Candidate-Job Scores": len(cand_job_scores),
        "Candidate Evidence": len(cand_evidence),
        "Training Catalog": len(training_catalog),
    }
    for name, count in summary.items():
        print(f"  {name:30s}: {count:>7,}")
    total = sum(summary.values())
    print(f"  {'TOTAL RECORDS':30s}: {total:>7,}")
    print(f"\nAll files written to: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
