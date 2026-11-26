"""Skill dictionary used for CV skill extraction: canonical name -> (category, aliases)."""

PL, WEB, DS, DB, TOOLS, SOFT = ("Programming Languages", "Web Development", "Data Science",
                                "Databases", "Tools & Technologies", "Soft Skills")
CATEGORIES = [PL, WEB, DS, DB, TOOLS, SOFT]

_RAW = {
    PL: {"Python": [], "Java": [], "C++": [], "C#": [], "C": ["c programming", "c language"],
         "JavaScript": ["ecmascript"], "TypeScript": [], "PHP": [], "Go": ["golang"], "Kotlin": [],
         "Swift": [], "Ruby": [], "Rust": [], "Dart": [], "MATLAB": []},
    WEB: {"HTML": ["html5"], "CSS": ["css3"], "React": ["react.js", "reactjs"], "Angular": ["angularjs"],
          "Vue.js": ["vue", "vuejs"], "Node.js": ["nodejs", "node js"], "Django": [], "Flask": [],
          "FastAPI": [], "Express.js": ["expressjs", "express js"], "Spring Boot": ["spring"],
          "Laravel": [], "Bootstrap": [], "Tailwind CSS": ["tailwind"], "REST APIs": ["rest api", "restful", "rest apis", "restful apis"],
          "GraphQL": [], "Streamlit": []},
    DS: {"Machine Learning": ["ml"], "Deep Learning": [], "Data Analysis": ["data analytics", "data analyst"],
         "Pandas": [], "NumPy": [], "Scikit-learn": ["sklearn", "scikit learn"], "TensorFlow": [],
         "PyTorch": [], "Keras": [], "Data Visualization": ["data visualisation"], "NLP": ["natural language processing"],
         "Computer Vision": [], "Statistics": ["statistical analysis"], "Power BI": ["powerbi"], "Tableau": [],
         "Matplotlib": [], "Plotly": [], "Data Cleaning": ["data preprocessing"]},
    DB: {"SQL": [], "MySQL": [], "PostgreSQL": ["postgres"], "MongoDB": [], "SQLite": [], "Redis": [],
         "Oracle": ["oracle database"], "Firebase": [],
         "Database Management": ["dbms", "database design", "database administration"]},
    TOOLS: {"Git": [], "GitHub": [], "Docker": [], "Kubernetes": ["k8s"], "Linux": [], "AWS": ["amazon web services"],
            "Azure": [], "Google Cloud": ["gcp"], "CI/CD": ["ci cd", "continuous integration"], "Jira": [],
            "Postman": [], "Agile": [], "Scrum": [], "Microsoft Excel": ["ms excel", "advanced excel"],
            "Figma": [], "Unit Testing": ["pytest", "unittest", "junit"], "Cybersecurity": ["cyber security", "information security"],
            "Network Security": [], "Penetration Testing": ["pentesting", "ethical hacking"], "Wireshark": [],
            "OWASP": [], "SIEM": [], "Networking": ["computer networks"], "Microservices": []},
    SOFT: {"Communication": ["communication skills"], "Problem Solving": ["problem-solving", "analytical thinking"],
           "Teamwork": ["team player", "collaboration", "team work"], "Leadership": [], "Time Management": [],
           "Critical Thinking": [], "Adaptability": [], "Creativity": []},
}

SKILL_CATEGORY = {name: cat for cat, skills in _RAW.items() for name in skills}
ALIASES = {name: [name.lower()] + [a.lower() for a in aliases]
           for skills in _RAW.values() for name, aliases in skills.items()}
