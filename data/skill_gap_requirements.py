"""Predefined career skill requirements for Skill Gap Analysis (plain structured data - no model involved).

CAREER_REQUIREMENTS: career -> {category, stage_names, requirements}. The career names are the same as in
data/roadmaps.py so the plan can be handed to the Learning Roadmap page.
A requirement says: which user skills satisfy it (`skills`, lower case), the level needed, how complex it is
(1-5, drives the study-hours estimate), how important it is for the job (weight 1-3), and in which of the
3 learning stages it belongs.
"""

LEVEL_RANK = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
COMPLEXITY_HOURS = {1: 6, 2: 14, 3: 26, 4: 42, 5: 60}   # beginner study hours by complexity
IMPORTANCE = {3: "High", 2: "Medium", 1: "Nice to have"}
FOCUS_MODES = {"Balanced": "Importance first, easy prerequisites before hard topics.",
               "Quick wins": "Short, easy skills first so you see progress sooner.",
               "Highest impact": "The most important skills for the job first."}
STAGE_COLORS = {1: "blue", 2: "purple", 3: "pink"}


def _r(name, cat, weight, cx, stage, purpose, skills=None, needs="Intermediate", requires=()):
    return {"name": name, "category": cat, "weight": weight, "complexity": cx, "stage": stage, "purpose": purpose,
            "skills": [s.lower() for s in (skills or [name])], "needs": needs, "requires": list(requires)}


_SQL = ["sql", "mysql", "postgresql", "sqlite", "sql server", "oracle"]
_API = ["rest apis", "apis", "api", "rest", "restful apis", "rest api"]
_OOP = ["oop", "object oriented programming", "object-oriented programming", "oop principles"]
_DSA = ["data structures", "algorithms", "data structures & algorithms", "dsa", "data structures and algorithms"]
_CLOUD = ["cloud computing", "cloud", "aws", "azure", "google cloud", "gcp"]
_GIT = ["git", "github", "git & github"]
_FRAMEWORKS = ["django", "flask", "fastapi", "express.js", "node.js", "spring boot", "asp.net core", "laravel"]

CAREER_REQUIREMENTS = {
    "Backend Developer": {
        "category": "Software Development", "stage_names": ["Core Skills", "Backend Development", "Advanced Topics"],
        "requirements": [
            _r("Python", "Programming", 3, 2, 1, "writing backend logic"),
            _r("Advanced Python", "Programming", 2, 3, 1, "writing clean, efficient code", ["python"], "Advanced", ["Python"]),
            _r("Data Structures & Algorithms", "CS Fundamentals", 3, 4, 1, "solving problems efficiently", _DSA),
            _r("OOP Principles", "CS Fundamentals", 3, 3, 1, "structuring large codebases", _OOP),
            _r("Git & GitHub", "Tools", 3, 2, 1, "working in a team", _GIT),
            _r("Linux Basics", "DevOps & Cloud", 2, 2, 1, "working on servers", ["linux"]),
            _r("Advanced Problem Solving", "CS Fundamentals", 2, 3, 1, "tackling complex tasks", ["problem solving", "advanced problem solving", "competitive programming"], "Advanced"),
            _r("SQL", "Databases", 3, 2, 2, "querying relational data", _SQL),
            _r("Advanced SQL", "Databases", 2, 3, 2, "writing joins, windows and optimised queries", _SQL, "Advanced", ["SQL"]),
            _r("Database Optimization", "Databases", 2, 4, 2, "keeping queries fast at scale", ["database optimization", "query optimization", "indexing"]),
            _r("Django Framework", "Web & APIs", 3, 3, 2, "building backend web applications", ["django"], "Intermediate", ["Python"]),
            _r("REST APIs", "Web & APIs", 3, 3, 2, "connecting apps and services", _API, "Intermediate", ["Python"]),
            _r("Authentication & Security", "Web & APIs", 2, 3, 2, "protecting users and data", ["authentication", "jwt", "oauth", "web security", "owasp", "security basics"]),
            _r("Unit Testing", "Tools", 2, 2, 2, "shipping reliable code", ["unit testing", "pytest", "unittest", "testing"]),
            _r("System Design", "CS Fundamentals", 3, 5, 3, "designing scalable systems", ["system design", "software architecture"]),
            _r("Design Patterns", "CS Fundamentals", 2, 4, 3, "writing maintainable architecture", ["design patterns"], "Intermediate", ["OOP Principles"]),
            _r("Docker", "DevOps & Cloud", 3, 3, 3, "deployment", ["docker", "containers"]),
            _r("Cloud Computing", "DevOps & Cloud", 2, 4, 3, "hosting and scaling applications", _CLOUD),
            _r("CI/CD", "DevOps & Cloud", 1, 3, 3, "automating tests and releases", ["ci/cd", "ci cd", "github actions", "jenkins"]),
            _r("Caching & Message Queues", "Web & APIs", 1, 4, 3, "handling high traffic", ["redis", "caching", "rabbitmq", "kafka", "message queues"]),
        ]},
    "Frontend Developer": {
        "category": "Software Development", "stage_names": ["Core Skills", "Frontend Development", "Advanced Topics"],
        "requirements": [
            _r("HTML", "Web & APIs", 3, 1, 1, "structuring web pages"),
            _r("CSS", "Web & APIs", 3, 2, 1, "styling and layout"),
            _r("JavaScript", "Programming", 3, 3, 1, "adding behaviour to pages"),
            _r("Git & GitHub", "Tools", 2, 2, 1, "working in a team", _GIT),
            _r("Responsive Design", "Design", 2, 2, 1, "supporting every screen size", ["responsive design", "media queries", "flexbox", "css grid", "bootstrap", "tailwind css"]),
            _r("Web Accessibility", "Design", 1, 2, 1, "making sites usable for everyone", ["accessibility", "a11y", "wcag"]),
            _r("React", "Web & APIs", 3, 4, 2, "building component-based interfaces", ["react"], "Intermediate", ["JavaScript"]),
            _r("TypeScript", "Programming", 2, 3, 2, "catching bugs early", ["typescript"], "Intermediate", ["JavaScript"]),
            _r("State Management", "Web & APIs", 2, 3, 2, "managing complex app data", ["state management", "redux", "zustand", "context api"]),
            _r("REST APIs", "Web & APIs", 2, 3, 2, "loading data from servers", _API),
            _r("CSS Frameworks", "Design", 2, 2, 2, "speeding up styling", ["bootstrap", "tailwind css", "tailwind"]),
            _r("Figma", "Design", 1, 2, 2, "working from design files", ["figma"]),
            _r("Unit Testing", "Tools", 2, 3, 3, "shipping reliable interfaces", ["unit testing", "jest", "testing"]),
            _r("Performance Optimization", "Web & APIs", 2, 4, 3, "building fast pages", ["performance optimization", "web performance", "lighthouse"]),
            _r("Build Tools", "Tools", 1, 2, 3, "bundling and tooling", ["webpack", "vite", "npm", "build tools"]),
            _r("CI/CD", "DevOps & Cloud", 1, 3, 3, "automating releases", ["ci/cd", "ci cd", "github actions"]),
        ]},
    "Full Stack Developer": {
        "category": "Software Development", "stage_names": ["Core Skills", "Full Stack Development", "Advanced Topics"],
        "requirements": [
            _r("HTML", "Web & APIs", 3, 1, 1, "structuring web pages"),
            _r("CSS", "Web & APIs", 3, 2, 1, "styling and layout"),
            _r("JavaScript", "Programming", 3, 3, 1, "front-end and Node.js development"),
            _r("Backend Language", "Programming", 3, 3, 1, "writing server-side logic", ["python", "node.js", "java", "c#", "php"]),
            _r("Git & GitHub", "Tools", 3, 2, 1, "working in a team", _GIT),
            _r("SQL", "Databases", 3, 2, 1, "querying relational data", _SQL),
            _r("React", "Web & APIs", 3, 4, 2, "building interfaces", ["react", "vue.js", "angular"], "Intermediate", ["JavaScript"]),
            _r("REST APIs", "Web & APIs", 3, 3, 2, "connecting front end and back end", _API),
            _r("Backend Framework", "Web & APIs", 3, 3, 2, "building server applications", _FRAMEWORKS),
            _r("Database Design", "Databases", 2, 3, 2, "modelling data", ["database design", "database management", "postgresql", "mongodb", "mysql"]),
            _r("Authentication & Security", "Web & APIs", 2, 3, 2, "protecting users and data", ["authentication", "jwt", "oauth", "web security", "owasp"]),
            _r("Docker", "DevOps & Cloud", 2, 3, 3, "deployment", ["docker", "containers"]),
            _r("Cloud Computing", "DevOps & Cloud", 2, 4, 3, "hosting applications", _CLOUD),
            _r("Unit Testing", "Tools", 2, 2, 3, "shipping reliable code", ["unit testing", "pytest", "jest", "testing"]),
            _r("System Design", "CS Fundamentals", 1, 5, 3, "designing scalable products", ["system design", "software architecture"]),
            _r("CI/CD", "DevOps & Cloud", 1, 3, 3, "automating releases", ["ci/cd", "ci cd", "github actions"]),
        ]},
    "Data Analyst": {
        "category": "Data & Analytics", "stage_names": ["Core Skills", "Data Analysis", "Advanced Topics"],
        "requirements": [
            _r("SQL", "Databases", 3, 2, 1, "extracting data", _SQL),
            _r("Advanced SQL", "Databases", 2, 3, 1, "complex joins and window functions", _SQL, "Advanced", ["SQL"]),
            _r("Microsoft Excel", "Tools", 3, 2, 1, "quick analysis and reporting", ["microsoft excel", "excel", "ms excel"]),
            _r("Python", "Programming", 3, 2, 1, "automating analysis"),
            _r("Statistics", "Data & AI", 3, 3, 1, "drawing valid conclusions", ["statistics", "statistical analysis"]),
            _r("Data Analysis", "Data & AI", 3, 3, 2, "finding insights in data", ["data analysis", "data analytics", "exploratory data analysis"]),
            _r("Pandas", "Data & AI", 3, 3, 2, "wrangling tabular data", ["pandas"], "Intermediate", ["Python"]),
            _r("Data Visualization", "Data & AI", 3, 3, 2, "communicating results", ["data visualization", "matplotlib", "plotly", "seaborn"]),
            _r("Power BI or Tableau", "Tools", 2, 3, 2, "building dashboards", ["power bi", "tableau"]),
            _r("Data Cleaning", "Data & AI", 2, 2, 2, "preparing reliable data", ["data cleaning", "data preprocessing"]),
            _r("NumPy", "Data & AI", 1, 2, 2, "numerical computing", ["numpy"], "Intermediate", ["Python"]),
            _r("A/B Testing & Hypothesis Tests", "Data & AI", 2, 4, 3, "measuring the effect of changes", ["a/b testing", "hypothesis testing", "advanced statistics"]),
            _r("Data Storytelling", "Soft Skills", 2, 2, 3, "presenting insights to stakeholders", ["communication", "data storytelling", "presentation skills"]),
            _r("Machine Learning Basics", "Data & AI", 1, 4, 3, "predictive analysis", ["machine learning", "scikit-learn"]),
            _r("Data Warehousing", "Databases", 1, 4, 3, "working with large analytical databases", ["data warehousing", "bigquery", "snowflake", "etl"]),
        ]},
    "Machine Learning Engineer": {
        "category": "Data & AI", "stage_names": ["Core Skills", "Machine Learning", "Advanced Topics"],
        "requirements": [
            _r("Python", "Programming", 3, 2, 1, "implementing models"),
            _r("Statistics & Probability", "Data & AI", 3, 3, 1, "understanding model behaviour", ["statistics", "probability", "statistical analysis"]),
            _r("Linear Algebra & Calculus", "CS Fundamentals", 2, 4, 1, "understanding how models learn", ["linear algebra", "calculus", "math", "mathematics"]),
            _r("NumPy", "Data & AI", 3, 2, 1, "numerical computing", ["numpy"], "Intermediate", ["Python"]),
            _r("Pandas", "Data & AI", 3, 3, 1, "preparing datasets", ["pandas"], "Intermediate", ["Python"]),
            _r("Git & GitHub", "Tools", 2, 2, 1, "tracking experiments and code", _GIT),
            _r("Machine Learning", "Data & AI", 3, 4, 2, "training predictive models", ["machine learning"]),
            _r("Scikit-learn", "Data & AI", 3, 3, 2, "classic ML algorithms", ["scikit-learn", "sklearn"], "Intermediate", ["Python"]),
            _r("Feature Engineering", "Data & AI", 2, 3, 2, "improving model inputs", ["feature engineering", "data cleaning", "data preprocessing"]),
            _r("SQL", "Databases", 2, 2, 2, "accessing training data", _SQL),
            _r("Data Visualization", "Data & AI", 1, 2, 2, "explaining results", ["data visualization", "matplotlib", "plotly"]),
            _r("Deep Learning", "Data & AI", 3, 5, 3, "neural networks", ["deep learning", "neural networks"], "Intermediate", ["Machine Learning"]),
            _r("TensorFlow or PyTorch", "Data & AI", 3, 4, 3, "building deep learning models", ["tensorflow", "pytorch", "keras"]),
            _r("Model Deployment", "DevOps & Cloud", 2, 4, 3, "serving models to users", ["model deployment", "mlops", "fastapi", "flask", "docker"]),
            _r("NLP or Computer Vision", "Data & AI", 1, 4, 3, "specialising in a domain", ["nlp", "computer vision"]),
        ]},
    "Software Engineer": {
        "category": "Software Development", "stage_names": ["Core Skills", "Software Engineering", "Advanced Topics"],
        "requirements": [
            _r("Programming Language", "Programming", 3, 3, 1, "implementing software", ["python", "java", "c++", "c#", "javascript"]),
            _r("Data Structures & Algorithms", "CS Fundamentals", 3, 4, 1, "solving problems efficiently", _DSA),
            _r("OOP Principles", "CS Fundamentals", 3, 3, 1, "structuring code", _OOP),
            _r("Git & GitHub", "Tools", 3, 2, 1, "collaborating on code", _GIT),
            _r("Problem Solving", "CS Fundamentals", 2, 3, 1, "debugging and design", ["problem solving", "advanced problem solving", "algorithms"]),
            _r("SQL", "Databases", 3, 2, 2, "storing and querying data", _SQL),
            _r("Software Testing", "Tools", 2, 3, 2, "keeping software reliable", ["unit testing", "pytest", "junit", "testing", "software testing"]),
            _r("Operating Systems Basics", "CS Fundamentals", 1, 3, 2, "understanding how programs run", ["operating systems", "linux", "os"]),
            _r("REST APIs", "Web & APIs", 2, 3, 2, "integrating services", _API),
            _r("Agile & Scrum", "Tools", 1, 1, 2, "working in a team process", ["agile", "scrum"]),
            _r("Design Patterns", "CS Fundamentals", 2, 4, 3, "writing maintainable code", ["design patterns"], "Intermediate", ["OOP Principles"]),
            _r("System Design", "CS Fundamentals", 3, 5, 3, "designing scalable systems", ["system design", "software architecture"]),
            _r("Docker", "DevOps & Cloud", 2, 3, 3, "deployment", ["docker", "containers"]),
            _r("CI/CD", "DevOps & Cloud", 2, 3, 3, "automating builds", ["ci/cd", "ci cd", "github actions", "jenkins"]),
            _r("Cloud Computing", "DevOps & Cloud", 1, 4, 3, "running software in the cloud", _CLOUD),
        ]},
    "Cybersecurity Analyst": {
        "category": "Cybersecurity", "stage_names": ["Core Skills", "Security Operations", "Advanced Topics"],
        "requirements": [
            _r("Networking", "Security", 3, 3, 1, "understanding how data travels", ["networking", "computer networks", "tcp/ip"]),
            _r("Linux", "DevOps & Cloud", 3, 2, 1, "working on servers", ["linux"]),
            _r("Cybersecurity Fundamentals", "Security", 3, 2, 1, "knowing threats and defences", ["cybersecurity", "information security", "cyber security"]),
            _r("Python Scripting", "Programming", 2, 2, 1, "automating security tasks", ["python", "bash", "shell scripting"]),
            _r("Problem Solving", "CS Fundamentals", 2, 3, 1, "investigating incidents", ["problem solving", "critical thinking"]),
            _r("Network Security", "Security", 3, 3, 2, "protecting networks", ["network security", "firewalls"], "Intermediate", ["Networking"]),
            _r("Wireshark", "Security", 2, 2, 2, "analysing traffic", ["wireshark"]),
            _r("SIEM", "Security", 2, 3, 2, "monitoring alerts", ["siem", "splunk"]),
            _r("Vulnerability Assessment", "Security", 2, 3, 2, "finding weaknesses", ["vulnerability assessment", "owasp", "nessus"]),
            _r("Cryptography Basics", "Security", 1, 3, 2, "protecting data", ["cryptography", "encryption"]),
            _r("Penetration Testing", "Security", 3, 4, 3, "testing defences", ["penetration testing", "pentesting", "ethical hacking"], "Intermediate", ["Cybersecurity Fundamentals"]),
            _r("Incident Response", "Security", 2, 3, 3, "handling attacks", ["incident response"]),
            _r("Cloud Security", "Security", 1, 4, 3, "securing cloud workloads", ["cloud security", "aws", "azure"]),
            _r("Security Frameworks", "Security", 1, 3, 3, "following standards", ["nist", "iso 27001", "owasp", "security frameworks"]),
        ]},
    "DevOps Engineer": {
        "category": "Cloud & DevOps", "stage_names": ["Core Skills", "DevOps Practices", "Advanced Topics"],
        "requirements": [
            _r("Linux", "DevOps & Cloud", 3, 2, 1, "administering servers", ["linux"]),
            _r("Git & GitHub", "Tools", 3, 2, 1, "version control", _GIT),
            _r("Networking", "DevOps & Cloud", 2, 3, 1, "understanding connectivity", ["networking", "computer networks", "tcp/ip"]),
            _r("Scripting", "Programming", 2, 2, 1, "automating tasks", ["python", "bash", "shell scripting", "powershell"]),
            _r("Docker", "DevOps & Cloud", 3, 3, 2, "packaging applications", ["docker", "containers"]),
            _r("CI/CD", "DevOps & Cloud", 3, 3, 2, "automating delivery", ["ci/cd", "ci cd", "github actions", "jenkins"], "Intermediate", ["Git & GitHub"]),
            _r("Cloud Computing", "DevOps & Cloud", 3, 4, 2, "running infrastructure", _CLOUD),
            _r("Infrastructure as Code", "DevOps & Cloud", 2, 4, 2, "managing infrastructure with code", ["terraform", "ansible", "infrastructure as code", "cloudformation"]),
            _r("Monitoring & Logging", "DevOps & Cloud", 2, 3, 2, "keeping services healthy", ["monitoring", "prometheus", "grafana", "logging"]),
            _r("Kubernetes", "DevOps & Cloud", 3, 5, 3, "orchestrating containers", ["kubernetes", "k8s"], "Intermediate", ["Docker"]),
            _r("Microservices", "Web & APIs", 2, 4, 3, "building distributed systems", ["microservices"]),
            _r("DevSecOps", "Security", 1, 3, 3, "securing pipelines", ["devsecops", "security"]),
            _r("Site Reliability Practices", "DevOps & Cloud", 1, 4, 3, "keeping systems reliable", ["sre", "site reliability", "incident response"]),
        ]},
    "Mobile App Developer": {
        "category": "Software Development", "stage_names": ["Core Skills", "Mobile Development", "Advanced Topics"],
        "requirements": [
            _r("Mobile Programming Language", "Programming", 3, 3, 1, "writing app logic", ["kotlin", "swift", "dart", "java"]),
            _r("OOP Principles", "CS Fundamentals", 3, 3, 1, "structuring app code", _OOP),
            _r("Git & GitHub", "Tools", 2, 2, 1, "version control", _GIT),
            _r("UI Basics", "Design", 2, 2, 1, "laying out screens", ["ui design", "ui", "html", "css"]),
            _r("Mobile Framework", "Mobile", 3, 4, 2, "building apps", ["flutter", "react native", "android", "ios", "swiftui", "jetpack compose"]),
            _r("REST APIs", "Web & APIs", 3, 3, 2, "loading app data", _API),
            _r("Local Storage & SQLite", "Databases", 2, 2, 2, "working offline", ["sqlite", "firebase", "room", "local storage"]),
            _r("State Management", "Mobile", 2, 3, 2, "keeping UI in sync with data", ["state management", "provider", "bloc", "redux", "viewmodel"]),
            _r("UI/UX Design", "Design", 1, 2, 2, "creating good experiences", ["figma", "ui/ux design", "ux"]),
            _r("Unit Testing", "Tools", 2, 3, 3, "shipping reliable apps", ["unit testing", "testing", "junit"]),
            _r("Performance Optimization", "Mobile", 2, 4, 3, "smooth, battery-friendly apps", ["performance optimization", "profiling"]),
            _r("Push Notifications & Firebase", "Mobile", 1, 3, 3, "engaging users", ["firebase", "push notifications"]),
            _r("App Store Publishing", "Mobile", 1, 2, 3, "releasing your app", ["app store publishing", "google play", "app store"]),
            _r("CI/CD", "DevOps & Cloud", 1, 3, 3, "automating builds", ["ci/cd", "ci cd", "github actions"]),
        ]},
}
CAREERS = list(CAREER_REQUIREMENTS)
