"""Predefined career roadmaps (static structured data, no model involved).

CAREER_ROADMAPS: career -> ordered learning stages. Each stage lists `core` skills (needed for the job) and `bonus`
skills (nice to have). Every skill name is a canonical name from data/skills_catalog.py, so it can be compared with the
skills stored in My Profile and the CV Analyzer.
SKILL_HOURS: typical study hours for a complete beginner. RESOURCES: curated learning links (official docs and
well-known free platforms; entries without a URL are practice suggestions).
"""

LEVELS = ["Beginner", "Intermediate", "Advanced"]
LEVEL_FACTOR = {"Beginner": 1.0, "Intermediate": 0.75, "Advanced": 0.55}  # share of the base hours still needed
LEVEL_HELP = {"Beginner": "New to most of these topics: full study time and beginner-friendly resources first.",
              "Intermediate": "Some experience: about 75% of the beginner study time.",
              "Advanced": "Strong background: about 55% of the study time, documentation and practice first."}
KIND_PREFERENCE = {"Beginner": ["Course", "Interactive", "Video", "Docs", "Book", "Practice"],
                   "Intermediate": ["Course", "Docs", "Interactive", "Practice", "Book", "Video"],
                   "Advanced": ["Docs", "Practice", "Book", "Course", "Interactive", "Video"]}
STUDY_DAYS_PER_WEEK = 5

# prerequisite inference: knowing the key skill means these basics are already known
IMPLIES = {
    "Django": ["Python"], "Flask": ["Python"], "FastAPI": ["Python"], "Pandas": ["Python"], "NumPy": ["Python"],
    "Scikit-learn": ["Python"], "TensorFlow": ["Python"], "PyTorch": ["Python"], "Keras": ["Python"],
    "React": ["JavaScript", "HTML"], "Vue.js": ["JavaScript", "HTML"], "Angular": ["JavaScript", "TypeScript", "HTML"],
    "TypeScript": ["JavaScript"], "Node.js": ["JavaScript"], "Express.js": ["Node.js", "JavaScript"],
    "Bootstrap": ["CSS", "HTML"], "Tailwind CSS": ["CSS", "HTML"], "CSS": ["HTML"],
    "PostgreSQL": ["SQL"], "MySQL": ["SQL"], "SQLite": ["SQL"], "Oracle": ["SQL"],
    "GitHub": ["Git"], "Spring Boot": ["Java"], "Kubernetes": ["Docker"], "Penetration Testing": ["Cybersecurity"],
    "Network Security": ["Networking"], "Deep Learning": ["Machine Learning"]
}


def _stage(name, goal, core, bonus, project):
    return {"name": name, "goal": goal, "core": core, "bonus": bonus, "project": project}


CAREER_ROADMAPS = {
    "Backend Developer": {
        "summary": "Build the server-side logic, databases and APIs that power web and mobile apps.",
        "stages": [
            _stage("Programming & Tools", "Write clean Python and manage your code with Git.", ["Python", "Git", "Linux"], ["GitHub"],
                   "A command-line expense tracker published on GitHub."),
            _stage("Databases", "Model, store and query data reliably.", ["SQL", "Database Management"], ["PostgreSQL", "MongoDB"],
                   "Design a library database and answer questions with joins."),
            _stage("Web APIs & Frameworks", "Build and secure REST APIs with a web framework.", ["REST APIs", "Flask", "Django"],
                   ["FastAPI", "Node.js"], "A task-manager API with user login."),
            _stage("Quality & Deployment", "Test, containerise and ship your services.", ["Unit Testing", "Docker"],
                   ["CI/CD", "AWS", "Redis", "Microservices"], "Containerise your API, add tests and a CI pipeline."),
        ]},
    "Frontend Developer": {
        "summary": "Create fast, accessible and beautiful user interfaces for the web.",
        "stages": [
            _stage("Web Foundations", "Structure, style and add behaviour to web pages.", ["HTML", "CSS", "JavaScript", "Git"], ["GitHub"],
                   "A responsive personal portfolio website."),
            _stage("Modern Frameworks", "Build component-based apps.", ["React"], ["TypeScript", "Vue.js", "Angular"],
                   "A weather app that calls a public API."),
            _stage("Styling & Design", "Speed up styling and work from designs.", ["Bootstrap", "Figma"], ["Tailwind CSS"],
                   "Rebuild a landing page from a Figma design."),
            _stage("Data & Quality", "Connect to back ends and test your UI.", ["REST APIs", "Unit Testing"], ["GraphQL"],
                   "A dashboard that loads data from an API, with tests."),
        ]},
    "Full Stack Developer": {
        "summary": "Build complete web applications, from the database to the user interface.",
        "stages": [
            _stage("Web Foundations", "Master the building blocks of the web.", ["HTML", "CSS", "JavaScript", "Git"], ["GitHub"],
                   "A multi-page responsive website."),
            _stage("Front End", "Build interactive interfaces.", ["React"], ["TypeScript", "Bootstrap"],
                   "A single-page app with routing and forms."),
            _stage("Back End & Data", "Create APIs and store data.", ["Node.js", "Express.js", "SQL", "REST APIs"],
                   ["Python", "Django", "MongoDB", "PostgreSQL"], "A blog platform with login, posts and comments."),
            _stage("Ship It", "Test and deploy your full-stack app.", ["Docker", "Unit Testing"], ["CI/CD", "AWS", "Linux"],
                   "Deploy your blog platform with a CI pipeline."),
        ]},
    "Data Analyst": {
        "summary": "Turn raw data into insights, dashboards and decisions.",
        "stages": [
            _stage("Data Foundations", "Understand data and basic analysis.", ["Microsoft Excel", "Statistics", "Data Analysis"],
                   ["Critical Thinking"], "Analyse a public dataset in Excel and summarise 5 insights."),
            _stage("SQL for Analysts", "Query databases to get the data you need.", ["SQL"], ["MySQL", "PostgreSQL"],
                   "Answer 15 business questions on a sample sales database."),
            _stage("Python for Data", "Clean and explore data with Python.", ["Python", "Pandas", "NumPy", "Data Cleaning"], [],
                   "Clean a messy dataset and publish the notebook."),
            _stage("Visualization & Reporting", "Communicate results with charts and dashboards.",
                   ["Data Visualization", "Power BI", "Matplotlib"], ["Tableau", "Plotly", "Communication"],
                   "A 3-page Power BI dashboard with a short written summary."),
        ]},
    "Machine Learning Engineer": {
        "summary": "Train, evaluate and deploy machine-learning models that solve real problems.",
        "stages": [
            _stage("Python & Math", "Build the programming and statistics base.", ["Python", "Statistics", "NumPy", "Git"], [],
                   "Implement basic statistics functions from scratch."),
            _stage("Data Handling", "Prepare and explore data.", ["Pandas", "Data Cleaning", "Matplotlib"], ["SQL"],
                   "Exploratory analysis of a Kaggle dataset."),
            _stage("Machine Learning", "Learn core algorithms and evaluation.", ["Machine Learning", "Scikit-learn"], [],
                   "A model that predicts house prices, with proper evaluation."),
            _stage("Deep Learning", "Work with neural networks.", ["Deep Learning", "TensorFlow"],
                   ["PyTorch", "Keras", "NLP", "Computer Vision"], "An image or text classifier trained on a public dataset."),
            _stage("Deployment", "Serve your model to users.", ["Docker"], ["FastAPI", "AWS"],
                   "Expose your model through an API in a container."),
        ]},
    "Software Engineer": {
        "summary": "Design, build and maintain reliable software with solid engineering practices.",
        "stages": [
            _stage("Core Programming", "Strong problem solving in a main language.", ["Python", "Git", "Problem Solving"], ["Java", "C++"],
                   "Solve 30 practice problems and publish your solutions."),
            _stage("Systems & Data", "Understand the platform your code runs on.", ["SQL", "Linux", "Database Management"], ["Networking"],
                   "A small inventory system backed by a database."),
            _stage("Building Software", "Create and test real features.", ["REST APIs", "Unit Testing", "Agile"], ["JavaScript"],
                   "A REST service with automated tests, built in sprints."),
            _stage("Professional Practice", "Work the way engineering teams do.", ["CI/CD", "Docker"], ["Microservices", "Jira", "GitHub"],
                   "Add CI and a pull-request workflow to your project."),
        ]},
    "Cybersecurity Analyst": {
        "summary": "Detect, investigate and prevent security threats to systems and networks.",
        "stages": [
            _stage("IT Foundations", "Know how systems and networks work.", ["Networking", "Linux", "Problem Solving"], ["Python"],
                   "Build a home lab network with virtual machines."),
            _stage("Security Fundamentals", "Learn the core security concepts.", ["Cybersecurity", "Network Security"], ["Critical Thinking"],
                   "Write a risk assessment for a small office network."),
            _stage("Defensive Tools", "Monitor traffic and investigate alerts.", ["Wireshark", "SIEM"], ["SQL"],
                   "Analyse a packet capture and report suspicious traffic."),
            _stage("Web & Offensive Security", "Find and understand vulnerabilities.", ["OWASP", "Penetration Testing"], [],
                   "Complete a beginner web-hacking path and write a report."),
        ]},
    "DevOps Engineer": {
        "summary": "Automate building, testing, deploying and running software in the cloud.",
        "stages": [
            _stage("Foundations", "Comfortable in the terminal with code and networks.", ["Linux", "Git", "Python"], ["GitHub", "Networking"],
                   "Automate a daily backup with a shell or Python script."),
            _stage("Containers", "Package applications to run anywhere.", ["Docker"], ["Kubernetes"],
                   "Containerise a web app with a database using Docker Compose."),
            _stage("Cloud & Automation", "Deploy automatically to the cloud.", ["AWS", "CI/CD"], ["Azure", "Google Cloud"],
                   "A pipeline that tests and deploys an app on every push."),
            _stage("Reliability & Security", "Keep systems healthy and secure.", ["Microservices"], ["Cybersecurity", "Redis"],
                   "Split a small app into two services with health checks."),
        ]},
    "Mobile App Developer": {
        "summary": "Build apps for Android and iOS devices that people use every day.",
        "stages": [
            _stage("Programming Foundations", "Learn object-oriented programming and Git.", ["Java", "Git", "Problem Solving"], ["GitHub"],
                   "A console app using classes and collections."),
            _stage("Mobile Development", "Build native or cross-platform apps.", ["Kotlin"], ["Dart"],
                   "A to-do app with a clean, responsive screen layout."),
            _stage("Backend Services", "Connect apps to data and APIs.", ["REST APIs", "Firebase"], ["SQLite"],
                   "A chat or notes app with sign-in and cloud storage."),
            _stage("Design & Quality", "Polish, test and ship.", ["Figma", "Unit Testing"], ["Agile", "CI/CD"],
                   "Prepare your app for release with tests and a design review."),
        ]},
}

SKILL_HOURS = {
    "Python": 40, "Git": 8, "GitHub": 4, "Linux": 15, "SQL": 20, "Database Management": 12, "PostgreSQL": 10, "MongoDB": 10,
    "MySQL": 8, "REST APIs": 12, "Flask": 15, "Django": 25, "FastAPI": 12, "Node.js": 20, "Express.js": 10, "Unit Testing": 10,
    "Docker": 12, "CI/CD": 8, "AWS": 20, "Redis": 6, "Microservices": 12, "HTML": 15, "CSS": 20, "JavaScript": 40, "React": 30,
    "Vue.js": 20, "Angular": 30, "TypeScript": 15, "Bootstrap": 8, "Tailwind CSS": 8, "Figma": 10, "GraphQL": 10,
    "Microsoft Excel": 15, "Statistics": 25, "Data Analysis": 20, "Critical Thinking": 6, "Data Cleaning": 10, "Pandas": 15,
    "NumPy": 10, "Matplotlib": 8, "Data Visualization": 10, "Power BI": 15, "Tableau": 15, "Plotly": 6, "Communication": 5,
    "Machine Learning": 30, "Scikit-learn": 15, "Deep Learning": 30, "TensorFlow": 20, "PyTorch": 20, "Keras": 8, "NLP": 20,
    "Computer Vision": 20, "Java": 40, "C++": 40, "Problem Solving": 15, "Agile": 6, "Jira": 4, "Networking": 20,
    "Cybersecurity": 20, "Network Security": 15, "Wireshark": 8, "SIEM": 12, "OWASP": 10, "Penetration Testing": 25,
    "Kubernetes": 20, "Azure": 20, "Google Cloud": 20, "Kotlin": 30, "Dart": 25, "Firebase": 8, "SQLite": 6,
}
DEFAULT_SKILL_HOURS = 12


def _r(title, provider, url="", kind="Course", free=True):
    return {"title": title, "provider": provider, "url": url, "kind": kind, "free": free}


RESOURCES = {
    "Python": [_r("The Python Tutorial", "Python.org", "https://docs.python.org/3/tutorial/", "Docs"),
               _r("Automate the Boring Stuff with Python", "Al Sweigart", "https://automatetheboringstuff.com/", "Book"),
               _r("CS50's Introduction to Programming with Python", "Harvard CS50", "https://cs50.harvard.edu/python/")],
    "Git": [_r("Pro Git", "git-scm.com", "https://git-scm.com/book/en/v2", "Book"),
            _r("Learn Git Branching", "learngitbranching.js.org", "https://learngitbranching.js.org/", "Interactive")],
    "GitHub": [_r("GitHub Skills", "GitHub", "https://skills.github.com/", "Interactive")],
    "Linux": [_r("Linux Journey", "linuxjourney.com", "https://linuxjourney.com/", "Interactive"),
              _r("Bandit wargame", "OverTheWire", "https://overthewire.org/wargames/bandit/", "Practice")],
    "SQL": [_r("SQLBolt", "sqlbolt.com", "https://sqlbolt.com/", "Interactive"),
            _r("SQL Tutorial", "Mode", "https://mode.com/sql-tutorial/", "Course")],
    "Database Management": [_r("Intro to SQL & databases", "Khan Academy", "https://www.khanacademy.org/computing/computer-programming/sql"),
                            _r("PostgreSQL Tutorial", "postgresqltutorial.com", "https://www.postgresqltutorial.com/", "Docs")],
    "PostgreSQL": [_r("Official PostgreSQL tutorial", "PostgreSQL docs", "https://www.postgresql.org/docs/current/tutorial.html", "Docs"),
                   _r("PostgreSQL Tutorial for beginners", "postgresqltutorial.com", "https://www.postgresqltutorial.com/")],
    "MongoDB": [_r("MongoDB University", "MongoDB", "https://learn.mongodb.com/")],
    "MySQL": [_r("MySQL Tutorial", "mysqltutorial.org", "https://www.mysqltutorial.org/")],
    "SQLite": [_r("SQLite Tutorial", "sqlitetutorial.net", "https://www.sqlitetutorial.net/")],
    "REST APIs": [_r("RESTful API tutorial", "restfulapi.net", "https://restfulapi.net/", "Docs"),
                  _r("HTTP overview", "MDN", "https://developer.mozilla.org/en-US/docs/Web/HTTP", "Docs")],
    "Flask": [_r("Flask Tutorial", "Flask docs", "https://flask.palletsprojects.com/en/stable/tutorial/", "Docs"),
              _r("The Flask Mega-Tutorial", "Miguel Grinberg", "https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world")],
    "Django": [_r("Writing your first Django app", "Django docs", "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "Docs"),
               _r("Django Girls Tutorial", "Django Girls", "https://tutorial.djangogirls.org/")],
    "FastAPI": [_r("FastAPI Tutorial", "FastAPI docs", "https://fastapi.tiangolo.com/tutorial/", "Docs")],
    "Node.js": [_r("Learn Node.js", "Node.js", "https://nodejs.org/en/learn", "Docs"),
                _r("Full Stack JavaScript path", "The Odin Project", "https://www.theodinproject.com/paths/full-stack-javascript")],
    "Express.js": [_r("Express/Node introduction", "MDN", "https://developer.mozilla.org/en-US/docs/Learn/Server-side/Express_Nodejs"),
                   _r("Express starter guide", "Express docs", "https://expressjs.com/en/starter/installing.html", "Docs")],
    "Unit Testing": [_r("Getting started with pytest", "pytest docs", "https://docs.pytest.org/en/stable/getting-started.html", "Docs"),
                     _r("Getting started with Jest", "Jest docs", "https://jestjs.io/docs/getting-started", "Docs")],
    "Docker": [_r("Get started with Docker", "Docker docs", "https://docs.docker.com/get-started/", "Docs"),
               _r("Play with Docker", "Docker", "https://labs.play-with-docker.com/", "Interactive")],
    "CI/CD": [_r("GitHub Actions quickstart", "GitHub docs", "https://docs.github.com/en/actions/quickstart", "Docs")],
    "AWS": [_r("AWS Skill Builder", "AWS", "https://skillbuilder.aws/"), _r("AWS Training", "AWS", "https://aws.amazon.com/training/")],
    "Redis": [_r("Redis get started", "Redis docs", "https://redis.io/docs/latest/develop/get-started/", "Docs"),
              _r("Redis University", "Redis", "https://university.redis.io/")],
    "Microservices": [_r("Microservices patterns", "microservices.io", "https://microservices.io/", "Docs")],
    "HTML": [_r("Learn HTML", "MDN", "https://developer.mozilla.org/en-US/docs/Learn/HTML", "Docs"),
             _r("Responsive Web Design", "freeCodeCamp", "https://www.freecodecamp.org/learn/2022/responsive-web-design/")],
    "CSS": [_r("Learn CSS", "MDN", "https://developer.mozilla.org/en-US/docs/Learn/CSS", "Docs"),
            _r("Flexbox Froggy", "flexboxfroggy.com", "https://flexboxfroggy.com/", "Interactive"),
            _r("CSS Grid Garden", "cssgridgarden.com", "https://cssgridgarden.com/", "Interactive")],
    "JavaScript": [_r("The Modern JavaScript Tutorial", "javascript.info", "https://javascript.info/"),
                   _r("Eloquent JavaScript", "Marijn Haverbeke", "https://eloquentjavascript.net/", "Book"),
                   _r("JavaScript guide", "MDN", "https://developer.mozilla.org/en-US/docs/Learn/JavaScript", "Docs")],
    "React": [_r("Learn React", "react.dev", "https://react.dev/learn", "Docs")],
    "Vue.js": [_r("Vue.js Tutorial", "vuejs.org", "https://vuejs.org/tutorial/", "Interactive")],
    "Angular": [_r("Angular Tutorials", "angular.dev", "https://angular.dev/tutorials", "Docs")],
    "TypeScript": [_r("TypeScript Handbook", "typescriptlang.org", "https://www.typescriptlang.org/docs/handbook/intro.html", "Docs"),
                   _r("TypeScript Exercises", "typescript-exercises.github.io", "https://typescript-exercises.github.io/", "Practice")],
    "Bootstrap": [_r("Bootstrap documentation", "getbootstrap.com", "https://getbootstrap.com/docs/5.3/getting-started/introduction/", "Docs")],
    "Tailwind CSS": [_r("Tailwind CSS docs", "tailwindcss.com", "https://tailwindcss.com/docs", "Docs")],
    "Figma": [_r("Figma Help Center", "Figma", "https://help.figma.com/hc/en-us", "Docs"),
              _r("Redesign a page you use daily and share it as a prototype", "Self-practice", "", "Practice")],
    "GraphQL": [_r("Introduction to GraphQL", "graphql.org", "https://graphql.org/learn/", "Docs")],
    "Microsoft Excel": [_r("Excel help & learning", "Microsoft", "https://support.microsoft.com/en-us/excel", "Docs"),
                        _r("Excel Easy", "excel-easy.com", "https://www.excel-easy.com/", "Interactive")],
    "Statistics": [_r("Statistics and probability", "Khan Academy", "https://www.khanacademy.org/math/statistics-probability"),
                   _r("StatQuest", "Josh Starmer", "https://statquest.org/", "Video")],
    "Data Analysis": [_r("Kaggle Learn", "Kaggle", "https://www.kaggle.com/learn", "Interactive"),
                      _r("Google Data Analytics Certificate", "Coursera", "https://www.coursera.org/professional-certificates/google-data-analytics", "Course", False)],
    "Critical Thinking": [_r("Question every chart you read: what is the claim, the evidence and what is missing?", "Self-practice", "", "Practice")],
    "Data Cleaning": [_r("Data Cleaning", "Kaggle Learn", "https://www.kaggle.com/learn/data-cleaning", "Interactive")],
    "Pandas": [_r("Pandas", "Kaggle Learn", "https://www.kaggle.com/learn/pandas", "Interactive"),
               _r("10 minutes to pandas", "pandas docs", "https://pandas.pydata.org/docs/user_guide/10min.html", "Docs")],
    "NumPy": [_r("NumPy: the absolute basics for beginners", "NumPy docs", "https://numpy.org/doc/stable/user/absolute_beginners.html", "Docs")],
    "Matplotlib": [_r("Matplotlib tutorials", "Matplotlib docs", "https://matplotlib.org/stable/tutorials/index.html", "Docs"),
                   _r("Data Visualization", "Kaggle Learn", "https://www.kaggle.com/learn/data-visualization", "Interactive")],
    "Data Visualization": [_r("From Data to Viz", "data-to-viz.com", "https://www.data-to-viz.com/", "Docs"),
                           _r("Data Visualization", "Kaggle Learn", "https://www.kaggle.com/learn/data-visualization", "Interactive")],
    "Power BI": [_r("Power BI training", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi")],
    "Tableau": [_r("Tableau free training videos", "Tableau", "https://www.tableau.com/learn/training", "Video"),
                _r("Tableau Public", "Tableau", "https://public.tableau.com/", "Practice")],
    "Plotly": [_r("Plotly Python graphing library", "plotly.com", "https://plotly.com/python/", "Docs")],
    "Communication": [_r("Present your project to a friend or a student club and ask for feedback", "Self-practice", "", "Practice")],
    "Machine Learning": [_r("Machine Learning Crash Course", "Google", "https://developers.google.com/machine-learning/crash-course"),
                         _r("Intro to Machine Learning", "Kaggle Learn", "https://www.kaggle.com/learn/intro-to-machine-learning", "Interactive"),
                         _r("Machine Learning Specialization", "Coursera", "https://www.coursera.org/specializations/machine-learning-introduction", "Course", False)],
    "Scikit-learn": [_r("scikit-learn user guide", "scikit-learn", "https://scikit-learn.org/stable/user_guide.html", "Docs"),
                     _r("Intermediate Machine Learning", "Kaggle Learn", "https://www.kaggle.com/learn/intermediate-machine-learning", "Interactive")],
    "Deep Learning": [_r("Intro to Deep Learning", "Kaggle Learn", "https://www.kaggle.com/learn/intro-to-deep-learning", "Interactive"),
                      _r("DeepLearning.AI courses", "DeepLearning.AI", "https://www.deeplearning.ai/")],
    "TensorFlow": [_r("TensorFlow tutorials", "TensorFlow", "https://www.tensorflow.org/tutorials", "Docs")],
    "PyTorch": [_r("PyTorch tutorials", "PyTorch", "https://pytorch.org/tutorials/", "Docs")],
    "Keras": [_r("Keras getting started", "keras.io", "https://keras.io/getting_started/", "Docs")],
    "NLP": [_r("Hugging Face NLP Course", "Hugging Face", "https://huggingface.co/learn/nlp-course")],
    "Computer Vision": [_r("Computer Vision", "Kaggle Learn", "https://www.kaggle.com/learn/computer-vision", "Interactive"),
                        _r("OpenCV tutorials", "OpenCV", "https://docs.opencv.org/4.x/d9/df8/tutorial_root.html", "Docs")],
    "Java": [_r("Learn Java", "dev.java", "https://dev.java/learn/", "Docs"),
             _r("Java Programming MOOC", "University of Helsinki", "https://java-programming.mooc.fi/")],
    "C++": [_r("Learn C++", "learncpp.com", "https://www.learncpp.com/")],
    "Problem Solving": [_r("Explore card sets", "LeetCode", "https://leetcode.com/explore/", "Practice"),
                        _r("Algorithms practice", "HackerRank", "https://www.hackerrank.com/domains/algorithms", "Practice")],
    "Agile": [_r("Agile Coach", "Atlassian", "https://www.atlassian.com/agile", "Docs")],
    "Jira": [_r("Atlassian University", "Atlassian", "https://university.atlassian.com/")],
    "Networking": [_r("Network+ course", "Professor Messer", "https://www.professormesser.com/network-plus/", "Video"),
                   _r("Networking Academy", "Cisco", "https://www.netacad.com/")],
    "Cybersecurity": [_r("Pre-Security path", "TryHackMe", "https://tryhackme.com/path/outline/presecurity", "Interactive"),
                      _r("Networking Academy", "Cisco", "https://www.netacad.com/")],
    "Network Security": [_r("Security+ course", "Professor Messer", "https://www.professormesser.com/security-plus/", "Video"),
                         _r("Cybrary", "cybrary.it", "https://www.cybrary.it/")],
    "Wireshark": [_r("Wireshark documentation", "wireshark.org", "https://www.wireshark.org/docs/", "Docs")],
    "SIEM": [_r("Free Splunk courses", "Splunk", "https://www.splunk.com/en_us/training/free-courses/overview.html"),
             _r("Wazuh getting started", "Wazuh docs", "https://documentation.wazuh.com/current/getting-started/", "Docs")],
    "OWASP": [_r("OWASP Top Ten", "OWASP", "https://owasp.org/www-project-top-ten/", "Docs"),
              _r("Web Security Academy", "PortSwigger", "https://portswigger.net/web-security", "Interactive")],
    "Penetration Testing": [_r("Hack The Box Academy", "Hack The Box", "https://academy.hackthebox.com/", "Interactive"),
                            _r("TryHackMe", "TryHackMe", "https://tryhackme.com/", "Interactive")],
    "Kubernetes": [_r("Kubernetes Basics", "kubernetes.io", "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "Docs")],
    "Azure": [_r("Azure training", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/azure/")],
    "Google Cloud": [_r("Google Cloud Skills Boost", "Google Cloud", "https://www.cloudskillsboost.google/")],
    "Kotlin": [_r("Kotlin getting started", "kotlinlang.org", "https://kotlinlang.org/docs/getting-started.html", "Docs"),
               _r("Android Basics with Compose", "Android Developers", "https://developer.android.com/courses/android-basics-compose/course")],
    "Dart": [_r("Dart overview", "dart.dev", "https://dart.dev/overview", "Docs"),
             _r("Flutter codelabs", "Flutter", "https://docs.flutter.dev/codelabs", "Interactive")],
    "Firebase": [_r("Firebase guides", "Firebase", "https://firebase.google.com/docs/guides", "Docs")],
}
