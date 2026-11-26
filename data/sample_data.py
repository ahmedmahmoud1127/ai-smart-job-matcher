"""Sample data for the dashboard. Replace with API / database calls later."""

USER = {"first_name": "Ahmed", "full_name": "Ahmed Mahmoud", "initial": "A"}

STATS = [
    {"key": "jobs", "label": "Total Jobs", "value": "1,250+", "sub": "Available Jobs", "delta": "12%",
     "icon": "briefcase", "tone": "blue", "trend": [4, 5, 5, 7, 6, 8, 9, 9, 11]},
    {"key": "matched", "label": "Matched Jobs", "value": "247", "sub": "Matched Opportunities", "delta": "8%",
     "icon": "target", "tone": "mint", "trend": [3, 4, 4, 6, 5, 7, 7, 8, 9]},
    {"key": "compat", "label": "Your Compatibility", "value": "78%", "sub": "Average Match Rate", "delta": "3%",
     "icon": "star", "tone": "cream", "trend": [6, 6, 7, 7, 8, 8, 8, 9, 9]},
    {"key": "skills", "label": "Skills Acquired", "value": "12", "sub": "Skills Learned", "delta": "2",
     "icon": "cap", "tone": "lav", "trend": [2, 3, 3, 4, 4, 5, 6, 6, 8]},
]

READINESS = {
    "score": 78,
    "message_title": "Great Progress!",
    "message": "You're well prepared for many opportunities.",
    "tip": "Learn Django to improve your chances in backend roles.",
    "available": ["Python", "SQL", "HTML", "CSS", "JavaScript", "Machine Learning", "Git", "Pandas",
                  "Problem Solving", "Data Analysis", "Teamwork", "English"],
    "missing": ["Django", "REST APIs", "Docker", "System Design", "Testing"],
    "advanced": ["Python", "SQL", "Machine Learning", "Data Analysis"],
}

JOBS = [
    {"id": 1, "title": "Backend Developer", "company": "Meta", "type": "Remote", "match": 94,
     "location": "Menlo Park, CA (Remote)", "salary": "$95k – $130k", "level": "Junior – Mid",
     "summary": "Build and maintain scalable services that power products used by billions of people.",
     "required": ["Python", "SQL", "REST APIs", "Django", "Git"]},
    {"id": 2, "title": "Data Scientist", "company": "Google", "type": "Remote", "match": 91,
     "location": "Mountain View, CA (Remote)", "salary": "$100k – $140k", "level": "Junior – Mid",
     "summary": "Turn large datasets into insight with statistical modeling and machine learning.",
     "required": ["Python", "SQL", "Machine Learning", "Pandas", "Data Analysis"]},
    {"id": 3, "title": "Software Engineer", "company": "Microsoft", "type": "Hybrid", "match": 87,
     "location": "Redmond, WA (Hybrid)", "salary": "$90k – $125k", "level": "Entry – Mid",
     "summary": "Design, code and ship features across cloud and developer-productivity products.",
     "required": ["Python", "JavaScript", "Git", "System Design", "Testing"]},
]

ROADMAP = [
    {"title": "Python Fundamentals", "progress": 100},
    {"title": "Django Framework", "progress": 45},
    {"title": "REST APIs", "progress": 0},
    {"title": "Git & GitHub", "progress": 0},
]

SKILLS = [
    {"name": "Python", "color": "#3B7DD8"}, {"name": "SQL", "color": "#2E9DB5"},
    {"name": "HTML", "color": "#E5703A"}, {"name": "CSS", "color": "#4A6FE0"},
    {"name": "JavaScript", "color": "#D9A21B"}, {"name": "Machine Learning", "color": "#7B6BD6"},
    {"name": "Git", "color": "#D2553E"}, {"name": "Pandas", "color": "#5B5FC7"},
    {"name": "Problem Solving", "color": "#3FA37A"}, {"name": "Data Analysis", "color": "#2E9DB5"},
    {"name": "Teamwork", "color": "#C77DA8"}, {"name": "English", "color": "#6C7A96"},
]
VISIBLE_SKILLS = 6

NOTIFICATIONS = [
    "3 new jobs match your profile",
    "Django Framework: 45% complete – keep going!",
    "Your CV was viewed by 2 recruiters",
]
