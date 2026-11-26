"""Predefined role requirements (static dataset; replace with live data later).
required = weight 2, preferred = weight 1, related = useful extras, keywords = phrases worth mentioning."""

JOB_ROLES = {
    "Backend Developer": {
        "required": ["Python", "SQL", "REST APIs", "Git", "Database Management"],
        "preferred": ["Django", "Flask", "FastAPI", "Docker", "PostgreSQL", "Node.js", "Java", "Linux", "AWS", "Unit Testing"],
        "related": ["MongoDB", "MySQL", "Redis", "Microservices", "CI/CD", "GitHub", "Problem Solving"],
        "keywords": ["api design", "authentication", "scalability", "microservices", "caching", "unit testing", "deployment"]},
    "Frontend Developer": {
        "required": ["HTML", "CSS", "JavaScript", "React", "Git"],
        "preferred": ["TypeScript", "Angular", "Vue.js", "Bootstrap", "Tailwind CSS", "REST APIs", "Figma", "Unit Testing"],
        "related": ["GitHub", "Node.js", "GraphQL", "Communication", "Creativity"],
        "keywords": ["responsive design", "accessibility", "ui components", "state management", "performance optimization", "cross-browser"]},
    "Full Stack Developer": {
        "required": ["HTML", "CSS", "JavaScript", "SQL", "Git", "REST APIs"],
        "preferred": ["React", "Node.js", "Python", "Django", "MongoDB", "Docker", "TypeScript", "PostgreSQL"],
        "related": ["GitHub", "Express.js", "Flask", "Linux", "AWS", "Agile", "Teamwork"],
        "keywords": ["full stack", "api integration", "responsive design", "authentication", "deployment", "database design"]},
    "Data Analyst": {
        "required": ["SQL", "Data Analysis", "Python", "Data Visualization", "Microsoft Excel"],
        "preferred": ["Pandas", "NumPy", "Power BI", "Tableau", "Statistics", "Matplotlib", "Data Cleaning"],
        "related": ["Plotly", "MySQL", "PostgreSQL", "Communication", "Problem Solving", "Critical Thinking"],
        "keywords": ["dashboards", "reporting", "kpi", "data cleaning", "insights", "exploratory data analysis"]},
    "Machine Learning Engineer": {
        "required": ["Python", "Machine Learning", "Scikit-learn", "Pandas", "NumPy", "Statistics"],
        "preferred": ["Deep Learning", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "SQL", "Docker", "Git"],
        "related": ["Keras", "Matplotlib", "Data Cleaning", "AWS", "Linux", "Problem Solving"],
        "keywords": ["model training", "feature engineering", "model evaluation", "deployment", "neural networks", "mlops"]},
    "Software Engineer": {
        "required": ["Python", "Git", "Problem Solving", "SQL"],
        "preferred": ["Java", "C++", "JavaScript", "REST APIs", "Docker", "Unit Testing", "Agile", "Linux", "CI/CD"],
        "related": ["GitHub", "Teamwork", "Communication", "Database Management", "Microservices"],
        "keywords": ["data structures", "algorithms", "software design", "code review", "testing", "version control"]},
    "Cybersecurity Analyst": {
        "required": ["Cybersecurity", "Networking", "Network Security", "Linux", "Problem Solving"],
        "preferred": ["Penetration Testing", "Wireshark", "OWASP", "SIEM", "Python", "SQL", "Critical Thinking"],
        "related": ["Git", "Docker", "Communication", "Teamwork", "Cloud"],
        "keywords": ["vulnerability assessment", "incident response", "threat analysis", "firewall", "encryption", "risk assessment"]},
}
ROLE_NAMES = list(JOB_ROLES)
