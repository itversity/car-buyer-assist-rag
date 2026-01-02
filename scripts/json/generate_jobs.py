#!/usr/bin/env python3
"""
Generate 1000 tech-focused job records in JSONL format for vector similarity search demo.
"""

import json
import random
from typing import List, Dict

# Job categories and titles
JOB_TITLES = {
    "Software Engineering": [
        "Junior Frontend Developer", "Mid-Level Frontend Developer", "Senior Frontend Developer",
        "Junior Backend Developer", "Mid-Level Backend Developer", "Senior Backend Developer",
        "Full-Stack Developer", "Senior Full-Stack Developer", "Lead Software Engineer",
        "Python Developer", "Senior Python Developer", "Java Developer", "Senior Java Developer",
        "JavaScript Developer", "Senior JavaScript Developer", "React Developer", "Senior React Developer",
        "Node.js Developer", "Go Developer", "Rust Developer", "C++ Developer", "Senior C++ Developer"
    ],
    "Data Science & Analytics": [
        "Junior Data Scientist", "Data Scientist", "Senior Data Scientist", "Lead Data Scientist",
        "Data Analyst", "Senior Data Analyst", "Business Intelligence Analyst", "Analytics Engineer",
        "Data Engineer", "Senior Data Engineer", "Big Data Engineer", "ETL Developer"
    ],
    "DevOps & Cloud Engineering": [
        "DevOps Engineer", "Senior DevOps Engineer", "Cloud Engineer", "Senior Cloud Engineer",
        "Site Reliability Engineer", "Senior SRE", "Infrastructure Engineer", "Kubernetes Engineer",
        "AWS Solutions Architect", "Azure Cloud Engineer", "GCP Engineer"
    ],
    "Machine Learning & AI": [
        "Machine Learning Engineer", "Senior ML Engineer", "MLOps Engineer", "AI Engineer",
        "Deep Learning Engineer", "Computer Vision Engineer", "NLP Engineer", "Research Scientist"
    ],
    "Mobile Development": [
        "iOS Developer", "Senior iOS Developer", "Android Developer", "Senior Android Developer",
        "React Native Developer", "Flutter Developer", "Mobile App Developer"
    ],
    "QA/Testing": [
        "QA Engineer", "Senior QA Engineer", "Test Automation Engineer", "SDET",
        "Quality Assurance Analyst", "Performance Test Engineer"
    ],
    "Product Management": [
        "Product Manager", "Senior Product Manager", "Technical Product Manager", "Product Owner"
    ],
    "Cybersecurity": [
        "Security Engineer", "Senior Security Engineer", "Cybersecurity Analyst", "Penetration Tester",
        "Security Architect", "Information Security Specialist"
    ],
    "Database Administration": [
        "Database Administrator", "Senior DBA", "Database Engineer", "Data Architect"
    ],
    "System Administration": [
        "Systems Administrator", "Senior Systems Administrator", "Linux Administrator", "Network Administrator"
    ]
}

# Locations
LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Boston, MA",
    "Chicago, IL", "Denver, CO", "Los Angeles, CA", "Remote", "Remote", "Remote",  # More remote options
    "Hybrid - San Francisco, CA", "Hybrid - New York, NY", "Hybrid - Seattle, WA",
    "Hybrid - Austin, TX", "Hybrid - Boston, MA", "Portland, OR", "Atlanta, GA",
    "Miami, FL", "Washington, DC", "Remote", "Remote"  # Even more remote
]

# Technologies and skills for descriptions
TECH_STACKS = {
    "Frontend": ["React", "Vue.js", "Angular", "TypeScript", "JavaScript", "HTML5", "CSS3", "Next.js", "Svelte"],
    "Backend": ["Python", "Java", "Node.js", "Go", "Rust", "C++", "Django", "Flask", "FastAPI", "Spring Boot", "Express"],
    "Data": ["Python", "SQL", "Pandas", "NumPy", "Spark", "Hadoop", "Kafka", "Airflow", "TensorFlow", "PyTorch"],
    "DevOps": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Jenkins", "GitLab CI", "Ansible"],
    "Mobile": ["Swift", "Kotlin", "React Native", "Flutter", "iOS", "Android"],
    "ML/AI": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "MLflow", "Kubeflow", "OpenCV", "NLTK"]
}

COMPANY_TYPES = [
    "fast-growing startup", "established tech company", "Fortune 500 company", "innovative fintech",
    "leading SaaS provider", "cutting-edge AI company", "well-funded startup", "enterprise software company",
    "healthcare technology company", "e-commerce platform", "cloud services provider", "cybersecurity firm"
]

WORK_ENVIRONMENTS = [
    "remote-first", "fully remote", "distributed team", "hybrid work model", "flexible remote options",
    "onsite with remote flexibility", "collaborative office environment"
]

BENEFITS_HINTS = [
    "competitive salary and equity", "comprehensive health benefits", "unlimited PTO", "flexible work hours",
    "learning and development budget", "401k matching", "stock options", "work-life balance",
    "professional development opportunities", "great company culture", "cutting-edge technology stack"
]


def generate_description(title: str, location: str) -> str:
    """Generate a rich, natural language job description."""
    # Determine job category from title
    category = None
    for cat, titles in JOB_TITLES.items():
        if title in titles:
            category = cat
            break
    
    if not category:
        category = "Software Engineering"
    
    # Select appropriate tech stack
    if "Frontend" in title or "React" in title or "JavaScript" in title:
        techs = random.sample(TECH_STACKS["Frontend"], min(3, len(TECH_STACKS["Frontend"])))
    elif "Backend" in title or "Python" in title or "Java" in title or "Node" in title:
        techs = random.sample(TECH_STACKS["Backend"], min(3, len(TECH_STACKS["Backend"])))
    elif "Data" in title or "Analyst" in title or "ML" in title or "Machine Learning" in title:
        techs = random.sample(TECH_STACKS["Data"], min(3, len(TECH_STACKS["Data"])))
    elif "DevOps" in title or "Cloud" in title or "SRE" in title:
        techs = random.sample(TECH_STACKS["DevOps"], min(3, len(TECH_STACKS["DevOps"])))
    elif "Mobile" in title or "iOS" in title or "Android" in title:
        techs = random.sample(TECH_STACKS["Mobile"], min(3, len(TECH_STACKS["Mobile"])))
    else:
        techs = random.sample(TECH_STACKS["Backend"], min(2, len(TECH_STACKS["Backend"])))
    
    company_type = random.choice(COMPANY_TYPES)
    work_env = random.choice(WORK_ENVIRONMENTS)
    benefit = random.choice(BENEFITS_HINTS)
    
    # Determine experience level from title
    if "Junior" in title or "Entry" in title:
        exp_level = "entry-level"
        responsibility = "You'll work on exciting projects and learn from experienced engineers"
    elif "Senior" in title or "Lead" in title:
        exp_level = "senior"
        responsibility = "You'll lead technical initiatives and mentor junior developers"
    else:
        exp_level = "mid-level"
        responsibility = "You'll design and implement robust solutions for complex problems"
    
    # Build description with varied phrasing
    description_parts = []
    
    # Opening sentence
    openings = [
        f"Join our {company_type} as a {title.lower()}.",
        f"We're seeking a talented {title.lower()} to join our {company_type}.",
        f"Exciting opportunity for a {title.lower()} at a {company_type}.",
        f"Looking for a skilled {title.lower()} to join our growing team at a {company_type}."
    ]
    description_parts.append(random.choice(openings))
    
    # Technical responsibilities
    tech_desc = f" {responsibility} using {', '.join(techs[:-1])} and {techs[-1]}."
    description_parts.append(tech_desc)
    
    # Work environment
    if "Remote" in location:
        if work_env in ["remote-first", "fully remote"]:
            env_desc = f" This is a {work_env} position, perfect for those who value flexibility."
        elif work_env == "distributed team":
            env_desc = f" We operate as a {work_env}, perfect for those who value flexibility."
        else:
            env_desc = f" We offer {work_env}, perfect for those who value flexibility."
    elif "Hybrid" in location:
        if work_env == "hybrid work model":
            env_desc = f" We offer a {work_env}, allowing you to balance office collaboration with remote work."
        else:
            env_desc = f" We offer a {work_env} approach, allowing you to balance office collaboration with remote work."
    else:
        if work_env in ["remote-first", "fully remote", "distributed team"]:
            env_desc = f" Our {work_env} approach fosters collaboration and innovation."
        elif work_env == "flexible remote options":
            env_desc = f" We offer {work_env} that foster collaboration and innovation."
        else:
            env_desc = f" Our {work_env} fosters collaboration and innovation."
    
    description_parts.append(env_desc)
    
    # Benefits/culture
    closing = f" We offer {benefit} and are committed to your professional growth."
    description_parts.append(closing)
    
    return "".join(description_parts)


def generate_salary(title: str, location: str) -> str:
    """Generate appropriate salary range based on title and location."""
    # Base salary ranges by level
    if "Junior" in title or "Entry" in title:
        base_min, base_max = 60000, 90000
    elif "Senior" in title or "Lead" in title:
        base_min, base_max = 120000, 200000
    else:
        base_min, base_max = 90000, 140000
    
    # Adjust for location
    if "San Francisco" in location or "New York" in location:
        multiplier = 1.3
    elif "Seattle" in location or "Boston" in location or "Los Angeles" in location:
        multiplier = 1.2
    elif "Remote" in location:
        multiplier = 1.0  # Remote can vary, but often competitive
    else:
        multiplier = 1.1
    
    min_salary = int(base_min * multiplier)
    max_salary = int(base_max * multiplier)
    
    # Add some variation
    min_salary += random.randint(-5000, 10000)
    max_salary += random.randint(0, 15000)
    
    return f"${min_salary:,} - ${max_salary:,}"


def generate_job_record() -> Dict:
    """Generate a single job record."""
    # Select random category and title
    category = random.choice(list(JOB_TITLES.keys()))
    title = random.choice(JOB_TITLES[category])
    location = random.choice(LOCATIONS)
    
    return {
        "title": title,
        "description": generate_description(title, location),
        "location": location,
        "salary": generate_salary(title, location)
    }


def main():
    """Generate 1000 job records and save to JSONL file."""
    output_file = "jobs_1000.jsonl"
    
    print(f"Generating 1000 job records...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i in range(1000):
            job = generate_job_record()
            f.write(json.dumps(job, ensure_ascii=False) + '\n')
            
            if (i + 1) % 100 == 0:
                print(f"Generated {i + 1} records...")
    
    print(f"Successfully generated 1000 job records in {output_file}")
    
    # Print a few sample records
    print("\nSample records:")
    with open(output_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 3:
                job = json.loads(line)
                print(f"\n{i+1}. {job['title']}")
                print(f"   Location: {job['location']}")
                print(f"   Salary: {job['salary']}")
                print(f"   Description: {job['description'][:100]}...")


if __name__ == "__main__":
    main()

