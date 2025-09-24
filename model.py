# """
# model.py – SkillBridge Resume Analyzer (Efficient & Diverse)

# Usage:
#     from model import analyze_resume, analyze_resume_file
#     user_skills, job_skills, missing_skills = analyze_resume(resume_text, job_text, target_role=role)
#     user_skills, job_skills, missing_skills = analyze_resume_file("resume.pdf", job_text, target_role=role)
# """

# import re
# import string
# import numpy as np
# import tensorflow_hub as hub
# import os

# try:
#     import PyPDF2
# except ImportError:
#     PyPDF2 = None

# # -----------------------------------------------------------------------------
# # Load Universal Sentence Encoder ONCE
# # -----------------------------------------------------------------------------
# print("Loading Universal Sentence Encoder (USE model)...")
# _EMBED = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
# print("USE model loaded.")

# # -----------------------------------------------------------------------------
# # Canonical Skill Synonyms (safe - no 2-letter triggers like 'ts')
# # -----------------------------------------------------------------------------
# SKILL_SYNONYMS = {
#     "python": ["python"],
#     "java": ["java"],
#     "javascript": ["javascript", "jscript"],
#     "typescript": ["typescript"],
#     "spring boot": ["spring boot", "springboot", "spring-boot"],
#     "react": ["react", "reactjs", "react.js"],
#     "react native": ["react native", "reactnative"],
#     "angular": ["angular", "angularjs", "angular.js"],
#     "vue.js": ["vue", "vue.js", "vuejs"],
#     "node.js": ["node.js", "nodejs", "node"],
#     "express.js": ["express", "express.js", "expressjs"],
#     "flask": ["flask"],
#     "django": ["django"],
#     "rest api": ["rest api", "restful api", "rest"],
#     "graphql": ["graphql"],
#     "docker": ["docker"],
#     "kubernetes": ["kubernetes", "k8s"],
#     "terraform": ["terraform", "iac"],
#     "mysql": ["mysql"],
#     "postgresql": ["postgresql", "postgres", "psql"],
#     "mongodb": ["mongodb", "mongo"],
#     "aws": ["aws", "amazon web services"],
#     "azure": ["azure", "microsoft azure"],
#     "gcp": ["gcp", "google cloud"],
#     "git": ["git", "github", "gitlab"],
#     "linux": ["linux", "unix"],
#     "machine learning": ["machine learning", "ml"],
#     "deep learning": ["deep learning", "dl"],
#     "tensorflow": ["tensorflow"],
#     "pytorch": ["pytorch", "torch"],
#     "pandas": ["pandas"],
#     "numpy": ["numpy"],
#     "scikit-learn": ["scikit learn", "scikit-learn", "sklearn"],
#     "flutter": ["flutter"],
#     "dart": ["dart"],
#     "firebase": ["firebase"],
#     "kotlin": ["kotlin"],
#     "swift": ["swift", "swiftui"],
#     "figma": ["figma"],
#     "adobe xd": ["adobe xd", "xd"],
#     "solidity": ["solidity"],
#     "ethereum": ["ethereum", "eth"],
#     "smart contracts": ["smart contract", "smart contracts"],
#     "web3.js": ["web3", "web3.js"],
#     "cryptography": ["cryptography"],
# }

# # -----------------------------------------------------------------------------
# # Role-Based Target Skills
# # -----------------------------------------------------------------------------
# ROLE_SKILLS = {
#     "Java Backend Developer": [
#         "Java", "Spring Boot", "REST API", "Hibernate", "JPA",
#         "MySQL", "PostgreSQL", "Docker", "Maven"
#     ],
#     "Node.js Backend Developer": [
#         "JavaScript", "Node.js", "Express.js", "REST API", "MongoDB",
#         "JWT Authentication", "Docker", "Redis"
#     ],
#     "Full Stack Developer (Java)": [
#         "HTML", "CSS", "JavaScript", "React", "Java",
#         "Spring Boot", "REST API", "MySQL", "Docker"
#     ],
#     "Full Stack Developer (JS)": [
#         "HTML", "CSS", "JavaScript", "React", "Node.js",
#         "Express.js", "MongoDB", "Docker"
#     ],
#     "Frontend Developer": [
#         "HTML", "CSS", "JavaScript", "React", "Vue.js",
#         "Tailwind CSS", "Responsive Design"
#     ],
#     "Mobile Developer": [
#         "Flutter", "Dart", "React Native", "Kotlin", "Swift",
#         "Firebase", "UI/UX"
#     ],
#     "Data Scientist": [
#         "Python", "Pandas", "NumPy", "Scikit-learn",
#         "Matplotlib", "TensorFlow", "SQL"
#     ],
#     "AI Engineer": [
#         "Python", "TensorFlow", "PyTorch", "Deep Learning",
#         "NLP", "ML Models", "MLOps"
#     ],
#     "Blockchain Developer": [
#         "Solidity", "Ethereum", "Smart Contracts",
#         "Web3.js", "Cryptography"
#     ],
#     "Cloud Engineer": [
#         "AWS", "Azure", "GCP", "Docker", "Kubernetes",
#         "Terraform", "CI/CD"
#     ],
#     "DevOps Engineer": [
#         "Docker", "Kubernetes", "CI/CD", "Linux",
#         "AWS", "Monitoring", "GitHub Actions"
#     ],
#     "UI/UX Designer": [
#         "Figma", "Adobe XD", "Sketch", "Wireframing",
#         "Prototyping", "User Research", "Information Architecture",
#         "Usability Testing", "Accessibility", "Design Systems",
#         "HTML", "CSS", "Basic JavaScript"
#     ],
#     "Web Developer": [
#     "HTML", "CSS", "JavaScript", "Responsive Design", "Basic SEO",
#     "Version Control (Git)", "Basic Backend (PHP/Node.js/Python)"
# ],
# "Backend Developer": [
#     "REST API", "Databases (SQL & NoSQL)", "Authentication",
#     "Docker", "Server-side Framework (Spring/Express/Django)"
# ],
# "Database Administrator": [
#     "SQL", "MySQL", "PostgreSQL", "Database Backup", 
#     "Performance Tuning", "Stored Procedures", "Security"
# ],
# "Machine Learning Engineer": [
#     "Python", "Scikit-learn", "TensorFlow", "PyTorch",
#     "Model Optimization", "Data Preprocessing", "ML Pipelines"
# ],
# "System Administrator": [
#     "Linux", "Shell Scripting", "Networking Basics",
#     "System Monitoring", "Backup & Recovery", "Firewall Config"
# ],
# "Embedded Systems Engineer": [
#     "C/C++", "Microcontrollers (Arduino, STM32)", 
#     "RTOS", "IoT Protocols", "Low-level Hardware Debugging"
# ],
# "AR/VR Developer": [
#     "Unity", "C#", "Unreal Engine", "3D Modeling",
#     "ARKit/ARCore", "OpenXR", "Interaction Design"
# ],
# "Cybersecurity Specialist": [
#     "Network Security", "Penetration Testing", "SIEM",
#     "Firewalls", "Cryptography", "Incident Response"
# ],
# "Network Engineer": [
#     "Routing & Switching", "TCP/IP", "LAN/WAN",
#     "Cisco Devices", "Firewall Management", "Network Monitoring"
# ]

# }


# # -----------------------------------------------------------------------------
# # Skills Library
# # -----------------------------------------------------------------------------
# SKILLS_LIBRARY = sorted({skill for role in ROLE_SKILLS.values() for skill in role})
# SKILLS_LIBRARY += [s.title() for s in SKILL_SYNONYMS.keys()]
# SKILLS_LIBRARY = sorted(set(SKILLS_LIBRARY))

# # -----------------------------------------------------------------------------
# # Helpers
# # -----------------------------------------------------------------------------
# _PUNC_TABLE = str.maketrans('', '', string.punctuation)
# def _clean(text: str) -> str:
#     return (text or "").lower().translate(_PUNC_TABLE)

# def extract_keywords(text: str):
#     if not text or not text.strip():
#         return []
#     low = _clean(text)
#     found = set()
#     for skill in SKILLS_LIBRARY:
#         pattern = r"\b" + re.escape(skill.lower()) + r"\b"
#         if re.search(pattern, low):
#             found.add(skill)
#     for canon, syns in SKILL_SYNONYMS.items():
#         for s in syns:
#             pattern = r"\b" + re.escape(s.lower()) + r"\b"
#             if re.search(pattern, low):
#                 found.add(canon.title())
#                 break
#     return sorted(found)

# def cosine_similarity(vec1, vec2):
#     dot = float(np.dot(vec1, vec2))
#     denom = float(np.linalg.norm(vec1) * np.linalg.norm(vec2))
#     return dot / denom if denom else 0.0

# # -----------------------------------------------------------------------------
# # Main Analyzer
# # -----------------------------------------------------------------------------
# def analyze_resume(resume_text: str, job_text: str = "", target_role: str = None, threshold: float = 0.65):
#     job_text = job_text or ""

#     # Extract job skills
#     job_skills = (
#         extract_keywords(job_text)
#         if job_text.strip()
#         else ROLE_SKILLS.get(target_role, [])
#     )
#     if not job_skills:
#         job_skills = [
#             "Python", "JavaScript", "HTML", "CSS", "React", "Node.js", "Django", "Flask",
#             "SQL", "MongoDB", "PostgreSQL", "AWS", "Docker", "Kubernetes", "Git",
#             "Linux", "REST API", "CI/CD", "Data Structures", "Machine Learning"
#         ]

#     user_skills = extract_keywords(resume_text)

#     if not user_skills:
#         return [], sorted(set(job_skills)), sorted(set(job_skills))

#     # 🔽 Normalize user skills (case-insensitive unique list)
#     user_skills = list({skill.lower(): skill.title() for skill in user_skills}.values())

#     # Vectorize
#     user_vecs = _EMBED(user_skills).numpy()
#     missing = []

#     for skill in job_skills:
#         skill_vec = _EMBED([skill]).numpy()[0]
#         max_sim = max((cosine_similarity(skill_vec, uv) for uv in user_vecs), default=0)
#         if max_sim < threshold:
#             missing.append(skill)

#     return sorted(set(user_skills)), sorted(set(job_skills)), sorted(set(missing))

# # -----------------------------------------------------------------------------
# # File-Based Analyzer
# # -----------------------------------------------------------------------------
# def analyze_resume_file(file_path: str, job_text: str = "", target_role: str = None, threshold: float = 0.7):
#     if not os.path.isfile(file_path):
#         raise FileNotFoundError(f"File not found: {file_path}")
    
#     text = ""
#     if file_path.lower().endswith(".txt"):
#         with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
#             text = f.read()
#     elif file_path.lower().endswith(".pdf"):
#         if PyPDF2 is None:
#             raise ImportError("PyPDF2 is not installed. Run: pip install PyPDF2")
#         with open(file_path, "rb") as f:
#             reader = PyPDF2.PdfReader(f)
#             for page in reader.pages:
#                 text += page.extract_text() or ""
#     else:
#         raise ValueError("Unsupported file format. Only .txt and .pdf are supported.")
    
#     return analyze_resume(text, job_text, target_role, threshold)

# # -----------------------------------------------------------------------------
# def generate_ai_suggestion(user_skills, missing_skills, role):
#     role = role.lower()

#     suggestions = []

#     if role == "ui/ux designer":
#         suggestions.append("🔹 Focus on mastering design tools like Figma, Adobe XD, and Sketch.")
#         suggestions.append("🔹 Strengthen your knowledge in user-centered design principles and wireframing.")
#         suggestions.append("🔹 Learn about accessibility standards and how to run usability testing.")
#         if "html" not in user_skills:
#             suggestions.append("🔹 Having a basic grasp of HTML/CSS can help you communicate better with developers.")
#         if "portfolio" not in user_skills:
#             suggestions.append("🔹 Build a professional portfolio showcasing your design thinking and projects.")

#     elif role == "frontend developer":
#         suggestions.append("🔹 Strengthen your JavaScript skills and explore frameworks like React or Vue.")
#         suggestions.append("🔹 Make sure you know responsive design, Flexbox, Grid, and cross-browser compatibility.")
#         if "api" not in user_skills:
#             suggestions.append("🔹 Learn how to interact with RESTful APIs and handle asynchronous data.")
    
#     elif role == "backend developer":
#         suggestions.append("🔹 Deepen your knowledge of backend languages like Python, Java, or Node.js.")
#         suggestions.append("🔹 Understand database management (SQL, MongoDB) and authentication systems.")
#         if "flask" not in user_skills and "django" not in user_skills:
#             suggestions.append("🔹 Learn backend frameworks like Flask or Django.")

#     elif role == "data analyst":
#         suggestions.append("🔹 Improve your skills in Python, SQL, and data visualization tools (Tableau, Power BI).")
#         suggestions.append("🔹 Learn to clean and analyze data using pandas, NumPy, and Excel.")
#         if "statistics" not in user_skills:
#             suggestions.append("🔹 Build your understanding of basic statistics and probability.")
    
#     elif role == "machine learning engineer":
#         suggestions.append("🔹 Learn ML libraries such as scikit-learn, TensorFlow, or PyTorch.")
#         suggestions.append("🔹 Study linear algebra, probability, and optimization fundamentals.")
#         if "projects" not in user_skills:
#             suggestions.append("🔹 Work on real-world ML projects and participate in Kaggle competitions.")

#     else:
#         suggestions.append(f"🔹 Explore relevant tools, courses, and projects related to '{role.title()}'.")

#     if missing_skills:
#         suggestions.append("🔹 You are missing key skills such as: " + ", ".join(missing_skills[:5]) + ".")

#     return "\n".join(suggestions)


# def generate_feedback(resume_text, user_skills, job_skills, missing_skills):
#     feedback = []

#     if not resume_text.strip():
#         feedback.append("📝 Your resume seems empty or too short. Add more content on skills and achievements.")

#     if missing_skills:
#         feedback.append(f"🚫 Missing job-critical skills like: {', '.join(missing_skills[:4])}. Add relevant projects or certifications.")

#     if len(user_skills) < 4:
#         feedback.append("🧩 Your resume lacks technical depth. Include tools, languages, frameworks, and libraries used.")

#     overlap = set(user_skills).intersection(set(job_skills))
#     if len(overlap) < 3:
#         feedback.append("⚠️ Limited overlap with job description. Tailor your resume with more matching skills.")

#     if not any(x in resume_text.lower() for x in ["achieved", "reduced", "improved", "saved", "led", "built", "developed"]):
#         feedback.append("📈 Include measurable results like 'Improved speed by 25%' or 'Built dashboard used by 5 teams'.")

#     if any(fluff in resume_text.lower() for fluff in ["team player", "hardworking", "go-getter"]):
#         feedback.append("❌ Avoid vague buzzwords like 'team player' or 'go-getter'. Focus on impact-driven statements.")

#     if not any(x in resume_text.lower() for x in ["summary", "objective"]):
#         feedback.append("📝 Include a clear summary or objective aligned with your target job title.")

#     feedback.append("👥 Highlight leadership, collaboration, or mentorship experience where possible.")

#     return feedback

# def match_best_role(user_skills):
#     best_role = None
#     max_matches = 0
#     for role, skills in ROLE_SKILLS.items():
#         matches = len(set(map(str.lower, user_skills)) & set(map(str.lower, skills)))
#         if matches > max_matches:
#             max_matches = matches
#             best_role = role
#     return best_role


# # -----------------------------------------------------------------------------
# # Self-Test
# # -----------------------------------------------------------------------------
# if __name__ == "__main__":
#     resume = """Programming Language: Python
#     Framework: React"""
#     u, j, m = analyze_resume(resume, target_role="Web Developer")
#     print("User Skills:", u)
#     print("Job Skills :", j)
#     print("Missing    :", m)

"""
model.py – SkillBridge Resume Analyzer (Efficient & Lazy Loading)

Usage:
    from model import analyze_resume, analyze_resume_file
    user_skills, job_skills, missing_skills = analyze_resume(resume_text, job_text, target_role=role)
    user_skills, job_skills, missing_skills = analyze_resume_file("resume.pdf", job_text, target_role=role)
"""

import re
import string
import numpy as np
import tensorflow_hub as hub
import os

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# ---------------------------------------------------------------------
# Lazy Loading for Universal Sentence Encoder
# ---------------------------------------------------------------------
_EMBED = None

def get_model():
    """Load the Universal Sentence Encoder on first use (from local path)."""
    global _EMBED
    if _EMBED is None:
        # 👇 Update this path if you moved the extracted model folder
        MODEL_PATH = r"C:\Users\AU Computers\Downloads\archive"
        
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Local USE model not found at {MODEL_PATH}")
        
        print("Loading Universal Sentence Encoder (USE model) from local path...")
        _EMBED = hub.load(MODEL_PATH)
        print("USE model loaded successfully (local).")
    return _EMBED


# ---------------------------------------------------------------------
# Canonical Skill Synonyms
# ---------------------------------------------------------------------
SKILL_SYNONYMS = {
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "jscript"],
    "typescript": ["typescript"],
    "spring boot": ["spring boot", "springboot", "spring-boot"],
    "react": ["react", "reactjs", "react.js"],
    "react native": ["react native", "reactnative"],
    "angular": ["angular", "angularjs", "angular.js"],
    "vue.js": ["vue", "vue.js", "vuejs"],
    "node.js": ["node.js", "nodejs", "node"],
    "express.js": ["express", "express.js", "expressjs"],
    "flask": ["flask"],
    "django": ["django"],
    "rest api": ["rest api", "restful api", "rest"],
    "graphql": ["graphql"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "terraform": ["terraform", "iac"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mongodb": ["mongodb", "mongo"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud"],
    "git": ["git", "github", "gitlab"],
    "linux": ["linux", "unix"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch", "torch"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit learn", "scikit-learn", "sklearn"],
    "flutter": ["flutter"],
    "dart": ["dart"],
    "firebase": ["firebase"],
    "kotlin": ["kotlin"],
    "swift": ["swift", "swiftui"],
    "figma": ["figma"],
    "adobe xd": ["adobe xd", "xd"],
    "solidity": ["solidity"],
    "ethereum": ["ethereum", "eth"],
    "smart contracts": ["smart contract", "smart contracts"],
    "web3.js": ["web3", "web3.js"],
    "cryptography": ["cryptography"],
}

# ---------------------------------------------------------------------
# Role-Based Target Skills
# ---------------------------------------------------------------------
ROLE_SKILLS = {
    "Java Backend Developer": [
        "Java", "Spring Boot", "REST API", "Hibernate", "JPA",
        "MySQL", "PostgreSQL", "Docker", "Maven"
    ],
    "Node.js Backend Developer": [
        "JavaScript", "Node.js", "Express.js", "REST API", "MongoDB",
        "JWT Authentication", "Docker", "Redis"
    ],
    "Full Stack Developer (Java)": [
        "HTML", "CSS", "JavaScript", "React", "Java",
        "Spring Boot", "REST API", "MySQL", "Docker"
    ],
    "Full Stack Developer (JS)": [
        "HTML", "CSS", "JavaScript", "React", "Node.js",
        "Express.js", "MongoDB", "Docker"
    ],
    "Frontend Developer": [
        "HTML", "CSS", "JavaScript", "React", "Vue.js",
        "Tailwind CSS", "Responsive Design"
    ],
    "Mobile Developer": [
        "Flutter", "Dart", "React Native", "Kotlin", "Swift",
        "Firebase", "UI/UX"
    ],
    "Data Scientist": [
        "Python", "Pandas", "NumPy", "Scikit-learn",
        "Matplotlib", "TensorFlow", "SQL"
    ],
    "AI Engineer": [
        "Python", "TensorFlow", "PyTorch", "Deep Learning",
        "NLP", "ML Models", "MLOps"
    ],
    "Blockchain Developer": [
        "Solidity", "Ethereum", "Smart Contracts",
        "Web3.js", "Cryptography"
    ],
    "Cloud Engineer": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes",
        "Terraform", "CI/CD"
    ],
    "DevOps Engineer": [
        "Docker", "Kubernetes", "CI/CD", "Linux",
        "AWS", "Monitoring", "GitHub Actions"
    ],
    "UI/UX Designer": [
        "Figma", "Adobe XD", "Sketch", "Wireframing",
        "Prototyping", "User Research", "Information Architecture",
        "Usability Testing", "Accessibility", "Design Systems",
        "HTML", "CSS", "Basic JavaScript"
    ],
    "Web Developer": [
        "HTML", "CSS", "JavaScript", "Responsive Design", "Basic SEO",
        "Version Control (Git)", "Basic Backend (PHP/Node.js/Python)"
    ],
    "Backend Developer": [
        "REST API", "Databases (SQL & NoSQL)", "Authentication",
        "Docker", "Server-side Framework (Spring/Express/Django)"
    ],
    "Database Administrator": [
        "SQL", "MySQL", "PostgreSQL", "Database Backup",
        "Performance Tuning", "Stored Procedures", "Security"
    ],
    "Machine Learning Engineer": [
        "Python", "Scikit-learn", "TensorFlow", "PyTorch",
        "Model Optimization", "Data Preprocessing", "ML Pipelines"
    ],
    "System Administrator": [
        "Linux", "Shell Scripting", "Networking Basics",
        "System Monitoring", "Backup & Recovery", "Firewall Config"
    ],
    "Embedded Systems Engineer": [
        "C/C++", "Microcontrollers (Arduino, STM32)",
        "RTOS", "IoT Protocols", "Low-level Hardware Debugging"
    ],
    "AR/VR Developer": [
        "Unity", "C#", "Unreal Engine", "3D Modeling",
        "ARKit/ARCore", "OpenXR", "Interaction Design"
    ],
    "Cybersecurity Specialist": [
        "Network Security", "Penetration Testing", "SIEM",
        "Firewalls", "Cryptography", "Incident Response"
    ],
    "Network Engineer": [
        "Routing & Switching", "TCP/IP", "LAN/WAN",
        "Cisco Devices", "Firewall Management", "Network Monitoring"
    ]
}

# ---------------------------------------------------------------------
# Skills Library
# ---------------------------------------------------------------------
SKILLS_LIBRARY = sorted({skill for role in ROLE_SKILLS.values() for skill in role})
SKILLS_LIBRARY += [s.title() for s in SKILL_SYNONYMS.keys()]
SKILLS_LIBRARY = sorted(set(SKILLS_LIBRARY))

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
_PUNC_TABLE = str.maketrans('', '', string.punctuation)

def _clean(text: str) -> str:
    return (text or "").lower().translate(_PUNC_TABLE)

def extract_keywords(text: str):
    if not text or not text.strip():
        return []
    low = _clean(text)
    found = set()
    for skill in SKILLS_LIBRARY:
        if re.search(r"\b" + re.escape(skill.lower()) + r"\b", low):
            found.add(skill)
    for canon, syns in SKILL_SYNONYMS.items():
        for s in syns:
            if re.search(r"\b" + re.escape(s.lower()) + r"\b", low):
                found.add(canon.title())
                break
    return sorted(found)

def cosine_similarity(vec1, vec2):
    dot = float(np.dot(vec1, vec2))
    denom = float(np.linalg.norm(vec1) * np.linalg.norm(vec2))
    return dot / denom if denom else 0.0

# ---------------------------------------------------------------------
# Main Analyzer
# ---------------------------------------------------------------------
def analyze_resume(resume_text: str, job_text: str = "", target_role: str = None, threshold: float = 0.65):
    model = get_model()

    job_text = job_text or ""
    job_skills = (
        extract_keywords(job_text)
        if job_text.strip()
        else ROLE_SKILLS.get(target_role, [])
    )
    if not job_skills:
        job_skills = [
            "Python", "JavaScript", "HTML", "CSS", "React", "Node.js", "Django", "Flask",
            "SQL", "MongoDB", "PostgreSQL", "AWS", "Docker", "Kubernetes", "Git",
            "Linux", "REST API", "CI/CD", "Data Structures", "Machine Learning"
        ]

    user_skills = extract_keywords(resume_text)
    if not user_skills:
        return [], sorted(set(job_skills)), sorted(set(job_skills))

    # normalize
    user_skills = list({s.lower(): s.title() for s in user_skills}.values())

    user_vecs = model(user_skills).numpy()
    missing = []
    for skill in job_skills:
        skill_vec = model([skill]).numpy()[0]
        max_sim = max((cosine_similarity(skill_vec, uv) for uv in user_vecs), default=0)
        if max_sim < threshold:
            missing.append(skill)

    return sorted(set(user_skills)), sorted(set(job_skills)), sorted(set(missing))

# ---------------------------------------------------------------------
# File-Based Analyzer
# ---------------------------------------------------------------------
def analyze_resume_file(file_path: str, job_text: str = "", target_role: str = None, threshold: float = 0.7):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    text = ""
    if file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    elif file_path.lower().endswith(".pdf"):
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is not installed. Run: pip install PyPDF2")
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    else:
        raise ValueError("Unsupported file format. Only .txt and .pdf are supported.")

    return analyze_resume(text, job_text, target_role, threshold)

# ---------------------------------------------------------------------
# AI Suggestions & Feedback
# ---------------------------------------------------------------------
def generate_ai_suggestion(user_skills, missing_skills, role):
    role = role.lower()
    suggestions = []

    if role == "ui/ux designer":
        suggestions.append("🔹 Focus on mastering design tools like Figma, Adobe XD, and Sketch.")
        suggestions.append("🔹 Strengthen your knowledge in user-centered design principles and wireframing.")
        suggestions.append("🔹 Learn about accessibility standards and usability testing.")
        if "html" not in user_skills:
            suggestions.append("🔹 A basic grasp of HTML/CSS can help you communicate with developers.")
        if "portfolio" not in user_skills:
            suggestions.append("🔹 Build a portfolio showcasing your design thinking and projects.")

    elif role == "frontend developer":
        suggestions.append("🔹 Strengthen your JavaScript skills and explore frameworks like React or Vue.")
        suggestions.append("🔹 Learn responsive design, Flexbox, Grid, and cross-browser compatibility.")
        if "api" not in user_skills:
            suggestions.append("🔹 Learn how to interact with RESTful APIs and handle async data.")

    elif role == "backend developer":
        suggestions.append("🔹 Deepen backend knowledge in Python, Java, or Node.js.")
        suggestions.append("🔹 Understand databases (SQL, MongoDB) and authentication systems.")
        if "flask" not in user_skills and "django" not in user_skills:
            suggestions.append("🔹 Learn backend frameworks like Flask or Django.")

    elif role == "data analyst":
        suggestions.append("🔹 Improve Python, SQL, and data visualization tools (Tableau, Power BI).")
        suggestions.append("🔹 Learn to clean and analyze data with pandas and NumPy.")
        if "statistics" not in user_skills:
            suggestions.append("🔹 Strengthen your understanding of statistics and probability.")

    elif role == "machine learning engineer":
        suggestions.append("🔹 Learn scikit-learn, TensorFlow, and PyTorch.")
        suggestions.append("🔹 Study linear algebra, probability, and optimization fundamentals.")
        if "projects" not in user_skills:
            suggestions.append("🔹 Work on real-world ML projects or Kaggle competitions.")

    else:
        suggestions.append(f"🔹 Explore relevant tools, courses, and projects related to '{role.title()}'.")

    if missing_skills:
        suggestions.append("🔹 You are missing key skills such as: " + ", ".join(missing_skills[:5]) + ".")

    return "\n".join(suggestions)

def generate_feedback(resume_text, user_skills, job_skills, missing_skills):
    feedback = []

    if not resume_text.strip():
        feedback.append("📝 Resume seems empty. Add more content on skills and achievements.")

    if missing_skills:
        feedback.append(f"🚫 Missing critical skills like: {', '.join(missing_skills[:4])}.")

    if len(user_skills) < 4:
        feedback.append("🧩 Resume lacks technical depth. Include tools, languages, frameworks, libraries.")

    overlap = set(user_skills).intersection(set(job_skills))
    if len(overlap) < 3:
        feedback.append("⚠️ Limited overlap with job description. Tailor your resume more closely.")

    if not any(x in resume_text.lower() for x in ["achieved", "reduced", "improved", "led", "built", "developed"]):
        feedback.append("📈 Add measurable results (e.g., 'Improved speed by 25%').")

    if any(fluff in resume_text.lower() for fluff in ["team player", "hardworking", "go-getter"]):
        feedback.append("❌ Avoid vague buzzwords like 'team player' or 'go-getter'.")

    if not any(x in resume_text.lower() for x in ["summary", "objective"]):
        feedback.append("📝 Add a summary/objective aligned with your target job title.")

    feedback.append("👥 Highlight leadership, collaboration, or mentorship experience.")

    return feedback

def match_best_role(user_skills):
    best_role = None
    max_matches = 0
    for role, skills in ROLE_SKILLS.items():
        matches = len(set(map(str.lower, user_skills)) & set(map(str.lower, skills)))
        if matches > max_matches:
            max_matches = matches
            best_role = role
    return best_role


# ---------------------------------------------------------------------
# Self-Test
# ---------------------------------------------------------------------
if __name__ == "__main__":
    resume = """Programming Language: Python
    Framework: React"""
    u, j, m = analyze_resume(resume, target_role="Web Developer")
    print("User Skills:", u)
    print("Job Skills :", j)
    print("Missing    :", m)
