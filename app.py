# from ai_resume_coach import ResumeCoach
# from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, flash, jsonify
# from werkzeug.utils import secure_filename
# import os
# from bson.objectid import ObjectId
# from flask_pymongo import PyMongo
# from datetime import datetime
# from model import analyze_resume, analyze_resume_file, generate_ai_suggestion, generate_feedback
# import random
# import pymongo
# from career_model import ask_career_bot

# app = Flask(__name__)
# app.secret_key = "skillbridge_secret_key"

# # MongoDB config
# app.config["MONGO_URI"] = "mongodb://localhost:27017/skillbridge"
# mongo = PyMongo(app)

# # Upload config
# UPLOAD_FOLDER = "static/uploads"
# ALLOWED_EXTENSIONS = {"txt", "pdf"}
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route("/")
# def landing():
#     return render_template("landingpage.html")

# @app.route("/resume", methods=["GET", "POST"])
# def resume():
#     user_skills = job_skills = missing_skills = []
#     ai_suggestion = ""
#     feedback_list = []
#     resume_text = ""
#     filename = None

#     if request.method == "POST":
#         job = request.form.get("job", "").strip()
#         role = request.form.get("role", "").strip()
#         file = request.files.get("resume_file", None)
#         resume_text = request.form.get("resume", "").strip()

#         if not file and not resume_text and not job:
#             return render_template("index.html", error="Please provide either a resume or job description.")

#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#             file.save(filepath)

#             if filepath.lower().endswith(".txt"):
#                 with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
#                     resume_text = f.read()
#             elif filepath.lower().endswith(".pdf"):
#                 import PyPDF2
#                 with open(filepath, "rb") as f:
#                     reader = PyPDF2.PdfReader(f)
#                     resume_text = "".join(page.extract_text() or "" for page in reader.pages)

#             user_skills, job_skills, missing_skills = analyze_resume_file(filepath, job, role)

#         elif resume_text:
#             user_skills, job_skills, missing_skills = analyze_resume(resume_text, job, role)

#         ai_suggestion = generate_ai_suggestion(user_skills, missing_skills, role)
#         feedback_list = generate_feedback(resume_text, user_skills, job_skills, missing_skills)

#     return render_template(
#         "index.html",
#         user_skills=user_skills,
#         job_skills=job_skills,
#         missing_skills=missing_skills,
#         ai_suggestion=ai_suggestion,
#         feedback=feedback_list,
#         filename=filename
#     )

# @app.route("/download/<filename>")
# def download_file(filename):
#     return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

# # @app.route("/register", methods=["GET", "POST"])
# # def register():
# #     if request.method == "POST":
# #         email = request.form.get("email")
# #         if mongo.db.users.find_one({"email": email}):
# #             return render_template("register.html", error="Email already registered.")
        
# #         user_data = {
# #             "fullname": request.form.get("fullname"),
# #             "email": email,
# #             "password": request.form.get("password"),
# #             "career_level": request.form.get("career_level"),
# #             "country": request.form.get("country"),
# #             "education_level": request.form.get("education_level"),
# #         }

# #         mongo.db.users.insert_one(user_data)
# #         return render_template("register.html", success="Registration successful!")

# #     return render_template("register.html")

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         email = request.form.get("email")
#         if mongo.db.users.find_one({"email": email}):
#             return render_template("register.html", error="Email already registered.")
        
#         user_data = {
#             "fullname": request.form.get("fullname"),
#             "email": email,
#             "password": request.form.get("password"),  # ⚠️ consider hashing later
#             "career_level": request.form.get("career_level"),
#             "country": request.form.get("country"),
#             "education_level": request.form.get("education_level"),
#         }

#         mongo.db.users.insert_one(user_data)
#         # ✅ Redirect to login page instead of showing register page again
#         return redirect(url_for("login"))

#     return render_template("register.html")

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")
#         user = mongo.db.users.find_one({"email": email})
#         if user and user["password"] == password:
#             session["user_email"] = user["email"]
#             session["fullname"] = user["fullname"]
#             return redirect(url_for("dashboard"))
#         else:
#             return render_template("login.html", error="Invalid email or password.")
#     return render_template("login.html")

# @app.route("/api/user")
# def get_user():
#     if "user_email" in session:
#         return {"fullname": session.get("fullname", "User")}
#     return {}, 401

# @app.route("/dashboard")
# def dashboard():
#     if "user_email" not in session:
#         return redirect(url_for("login"))
#     return render_template("dashboard.html", name=session["fullname"])

# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect(url_for("landing"))

# @app.route("/jobs")
# def view_jobs():
#     jobs = list(mongo.db.jobs.find())
#     return render_template("job_application.html", jobs=jobs)

# @app.route("/apply", methods=["POST"])
# def apply_job():
#     if "user_email" not in session:
#         flash("You need to log in to apply.", "warning")
#         return redirect(url_for("login"))

#     user = mongo.db.users.find_one({"email": session["user_email"]})
#     if not user:
#         flash("User not found.", "danger")
#         return redirect(url_for("login"))

#     job_id = request.form.get("job_id")
#     name = request.form.get("name")
#     email = request.form.get("email")
#     phone = request.form.get("phone")
#     message = request.form.get("message")
#     resume = request.files.get("resume")

#     resume_path = None
#     if resume and allowed_file(resume.filename):
#         filename = secure_filename(f"{name.replace(' ', '_')}_{resume.filename}")
#         resume_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#         resume.save(resume_path)

#     mongo.db.applications.insert_one({
#         "job_id": ObjectId(job_id),
#         "user_id": user["_id"],
#         "name": name,
#         "email": email,
#         "phone": phone,
#         "message": message,
#         "resume_path": resume_path,
#     })

#     flash("Your application has been submitted!", "success")
#     return redirect(url_for("my_applications"))

# @app.route("/my-applications")
# def my_applications():
#     if "user_email" not in session:
#         return redirect(url_for("login"))

#     user = mongo.db.users.find_one({"email": session["user_email"]})
#     if not user:
#         flash("User not found.", "danger")
#         return redirect(url_for("logout"))

#     applications = mongo.db.applications.find({"user_id": user["_id"]})
#     return render_template("my_applications.html", applications=applications)

# @app.route("/bookmark/<job_id>", methods=["POST"])
# def bookmark_job(job_id):
#     if "user_email" not in session:
#         return jsonify({"success": False, "message": "Login required"}), 401

#     user = mongo.db.users.find_one({"email": session["user_email"]})
#     if not user:
#         return jsonify({"success": False, "message": "User not found"}), 404

#     user_id = user["_id"]
#     job_obj_id = ObjectId(job_id)

#     if mongo.db.bookmarks.find_one({"user_id": user_id, "job_id": job_obj_id}):
#         return jsonify({"success": False, "message": "Already bookmarked"})

#     mongo.db.bookmarks.insert_one({"user_id": user_id, "job_id": job_obj_id})
#     return jsonify({"success": True, "message": "Job bookmarked!"})

# @app.route("/bookmarks")
# def bookmarks():
#     if "user_email" not in session:
#         flash("Please login to view bookmarks", "warning")
#         return redirect(url_for("login"))

#     user = mongo.db.users.find_one({"email": session["user_email"]})
#     if not user:
#         flash("User not found", "danger")
#         return redirect(url_for("login"))

#     bookmark_entries = list(mongo.db.bookmarks.find({"user_id": user["_id"]}))
#     job_ids = [entry["job_id"] for entry in bookmark_entries]
#     saved_jobs = list(mongo.db.jobs.find({"_id": {"$in": job_ids}}))

#     return render_template("bookmarks.html", saved_jobs=saved_jobs)

# @app.route("/remove-bookmark/<job_id>", methods=["POST"])
# def remove_bookmark(job_id):
#     if "user_email" not in session:
#         return jsonify({"success": False, "message": "Login required"}), 401

#     user = mongo.db.users.find_one({"email": session["user_email"]})
#     if not user:
#         return jsonify({"success": False, "message": "User not found"}), 404

#     mongo.db.bookmarks.delete_one({"user_id": user["_id"], "job_id": ObjectId(job_id)})
#     return redirect(url_for("bookmarks"))

# @app.route("/notifications")
# def notifications():
#     if "user_email" not in session:
#         return redirect(url_for("login"))

#     user_email = session["user_email"]
#     user = mongo.db.users.find_one({"email": user_email})
#     if not user:
#         flash("User not found.", "danger")
#         return redirect(url_for("logout"))

#     notifications = list(mongo.db.applications.find({
#         "user_id": user["_id"],
#         "notification": {"$exists": True}
#     }))

#     messages = list(mongo.db.messages.find({"email": user_email}))

#     return render_template(
#         "notifications.html",
#         messages=messages,
#         notifications=notifications
#     )

# @app.route("/admin/login", methods=["GET", "POST"])
# def admin_login():
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")

#         if username == "admin" and password == "admin123":
#             session["admin"] = True
#             session["role"] = "admin"
#             return redirect(url_for("admin_dashboard"))
#         else:
#             return render_template("admin_login.html", error="Invalid credentials.")

#     return render_template("admin_login.html")

# @app.route("/admin/dashboard")
# def admin_dashboard():
#     if not session.get("admin"):
#         return redirect(url_for("admin_login"))
#     return render_template("admin_dashboard.html")

# @app.route("/admin/logout")
# def admin_logout():
#     session.pop("admin", None)
#     session.pop("role", None)
#     return redirect(url_for("admin_login"))

# @app.route("/admin/users")
# def admin_users():
#     if not session.get("admin"):
#         return redirect(url_for("admin_login"))

#     users = list(mongo.db.users.find())
#     return render_template("admin_users.html", users=users)

# @app.route("/admin/jobs", methods=["GET", "POST"])
# def manage_jobs():
#     if not session.get("admin"):
#         return redirect(url_for("admin_login"))

#     if request.method == "POST":
#         job = {
#             "title": request.form.get("title"),
#             "company": request.form.get("company"),
#             "location": request.form.get("location"),
#             "type": request.form.get("type"),
#             "posted_date": request.form.get("posted_date"),
#             "description": request.form.get("description"),
#         }
#         mongo.db.jobs.insert_one(job)
#         return redirect(url_for("manage_jobs"))

#     jobs = list(mongo.db.jobs.find())
#     return render_template("admin_jobs.html", jobs=jobs)

# @app.route("/admin/applications")
# def admin_applications():
#     if session.get("role") != "admin":
#         flash("Admins only!", "danger")
#         return redirect(url_for("landing"))

#     apps = list(mongo.db.applications.find())
#     for app in apps:
#         job = mongo.db.jobs.find_one({"_id": ObjectId(app["job_id"])})
#         app["job_title"] = job.get("title", "Untitled Job") if job else "Deleted Job"

#     return render_template("admin_applications.html", applications=apps)

# @app.route('/admin/applications/<app_id>/accept', methods=['POST'])
# def accept_application(app_id):
#     application = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
#     job = mongo.db.jobs.find_one({'_id': application["job_id"]})
#     job_title = job.get("title", "This job") if job else "This job"

#     mongo.db.applications.update_one(
#         {'_id': ObjectId(app_id)},
#         {'$set': {
#             'status': 'Accepted',
#             'notification': f'Your application for "{job_title}" has been accepted!'
#         }}
#     )
#     flash('Application accepted and user notified.')
#     return redirect(url_for('admin_applications'))

# @app.route('/admin/applications/<app_id>/reject', methods=['POST'])
# def reject_application(app_id):
#     application = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
#     job = mongo.db.jobs.find_one({'_id': application["job_id"]})
#     job_title = job.get("title", "This job") if job else "This job"

#     mongo.db.applications.update_one(
#         {'_id': ObjectId(app_id)},
#         {'$set': {
#             'status': 'Rejected',
#             'notification': f'Sorry, your application for "{job_title}" was rejected.'
#         }}
#     )
#     flash('Application rejected and user notified.')
#     return redirect(url_for('admin_applications'))

# @app.route('/admin/applications/<app_id>/pending', methods=['POST'])
# def pending_application(app_id):
#     application = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
#     job = mongo.db.jobs.find_one({'_id': application["job_id"]})
#     job_title = job.get("title", "This job") if job else "This job"

#     mongo.db.applications.update_one(
#         {'_id': ObjectId(app_id)},
#         {'$set': {
#             'status': 'Pending',
#             'notification': f'Your application for "{job_title}" is under review.'
#         }}
#     )
#     flash('Application marked as pending and user notified.')
#     return redirect(url_for('admin_applications'))

# @app.route("/admin/send-message", methods=["POST"])
# def send_message():
#     if not session.get("admin"):
#         return redirect(url_for("admin_login"))

#     email = request.form.get("email")
#     message = request.form.get("message")

#     if not email or not message:
#         flash("Missing data")
#         return redirect(url_for("admin_users"))

#     mongo.db.messages.insert_one({
#         "email": email,
#         "message": message,
#         "date": datetime.utcnow()
#     })

#     flash(f"Message sent to {email}")
#     return redirect(url_for("admin_users"))

# # Interview Prep Feature
# def seed_interview_questions(force_reseed=False):
#     sample_questions = [
#         {"role": "Java Backend Developer", "type": "technical", "difficulty": "easy", "question": "What is the difference between List and Set in Java?"},
#         {"role": "Java Backend Developer", "type": "technical", "difficulty": "medium", "question": "How would you optimize a Spring Boot application for performance?"},
#         {"role": "Java Backend Developer", "type": "technical", "difficulty": "hard", "question": "Design a REST API for a banking system with transaction history."},
#         {"role": "Java Backend Developer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a time you debugged a complex Java issue."},
#         {"role": "Java Backend Developer", "type": "system_design", "difficulty": "hard", "question": "Design a scalable microservices architecture using Spring Boot."},
#         {"role": "Node.js Backend Developer", "type": "technical", "difficulty": "easy", "question": "What is the event loop in Node.js?"},
#         {"role": "Node.js Backend Developer", "type": "technical", "difficulty": "medium", "question": "How would you handle authentication in an Express.js app?"},
#         {"role": "Node.js Backend Developer", "type": "technical", "difficulty": "hard", "question": "Implement a rate limiter for an API using Node.js."},
#         {"role": "Node.js Backend Developer", "type": "behavioral", "difficulty": "medium", "question": "Describe a challenging Node.js project you worked on."},
#         {"role": "Node.js Backend Developer", "type": "system_design", "difficulty": "hard", "question": "Design a real-time chat system with Node.js and WebSockets."},
#         {"role": "Full Stack Developer (Java)", "type": "technical", "difficulty": "easy", "question": "What is the role of CSS in a web application?"},
#         {"role": "Full Stack Developer (Java)", "type": "technical", "difficulty": "medium", "question": "How do you integrate React with a Spring Boot backend?"},
#         {"role": "Full Stack Developer (Java)", "type": "technical", "difficulty": "hard", "question": "Build a full-stack e-commerce app with React and Java."},
#         {"role": "Full Stack Developer (Java)", "type": "behavioral", "difficulty": "medium", "question": "Share a time you collaborated on a full-stack project."},
#         {"role": "Full Stack Developer (Java)", "type": "system_design", "difficulty": "hard", "question": "Design a scalable full-stack solution for an online store."},
#         {"role": "Full Stack Developer (JS)", "type": "technical", "difficulty": "easy", "question": "What is a callback function in JavaScript?"},
#         {"role": "Full Stack Developer (JS)", "type": "technical", "difficulty": "medium", "question": "How do you secure a Node.js and React application?"},
#         {"role": "Full Stack Developer (JS)", "type": "technical", "difficulty": "hard", "question": "Design a RESTful API with MongoDB and Express."},
#         {"role": "Full Stack Developer (JS)", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a full-stack bug you fixed."},
#         {"role": "Full Stack Developer (JS)", "type": "system_design", "difficulty": "hard", "question": "Plan a scalable JS full-stack app for a social platform."},
#         {"role": "Frontend Developer", "type": "technical", "difficulty": "easy", "question": "What is the box model in CSS?"},
#         {"role": "Frontend Developer", "type": "technical", "difficulty": "medium", "question": "How do you optimize a React application?"},
#         {"role": "Frontend Developer", "type": "technical", "difficulty": "hard", "question": "Create a responsive design for a multi-device layout."},
#         {"role": "Frontend Developer", "type": "behavioral", "difficulty": "medium", "question": "Describe a time you improved a website’s usability."},
#         {"role": "Frontend Developer", "type": "system_design", "difficulty": "hard", "question": "Design a frontend for a high-traffic e-commerce site."},
#         {"role": "Mobile Developer", "type": "technical", "difficulty": "easy", "question": "What is the difference between Flutter and React Native?"},
#         {"role": "Mobile Developer", "type": "technical", "difficulty": "medium", "question": "How do you handle state management in Flutter?"},
#         {"role": "Mobile Developer", "type": "technical", "difficulty": "hard", "question": "Design a mobile app for real-time location tracking."},
#         {"role": "Mobile Developer", "type": "behavioral", "difficulty": "medium", "question": "Share a mobile app project you’re proud of."},
#         {"role": "Mobile Developer", "type": "system_design", "difficulty": "hard", "question": "Plan a cross-platform mobile app architecture."},
#         {"role": "Data Scientist", "type": "technical", "difficulty": "easy", "question": "What is a confusion matrix?"},
#         {"role": "Data Scientist", "type": "technical", "difficulty": "medium", "question": "Explain the process of feature engineering."},
#         {"role": "Data Scientist", "type": "technical", "difficulty": "hard", "question": "Build a predictive model using TensorFlow."},
#         {"role": "Data Scientist", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a data project that impacted a business."},
#         {"role": "Data Scientist", "type": "system_design", "difficulty": "hard", "question": "Design a data pipeline for a recommendation system."},
#         {"role": "AI Engineer", "type": "technical", "difficulty": "easy", "question": "What is a neural network?"},
#         {"role": "AI Engineer", "type": "technical", "difficulty": "medium", "question": "How do you prevent overfitting in a model?"},
#         {"role": "AI Engineer", "type": "technical", "difficulty": "hard", "question": "Implement an NLP model for sentiment analysis."},
#         {"role": "AI Engineer", "type": "behavioral", "difficulty": "medium", "question": "Describe an AI project you led."},
#         {"role": "AI Engineer", "type": "system_design", "difficulty": "hard", "question": "Design an AI-powered chatbot system."},
#         {"role": "Blockchain Developer", "type": "technical", "difficulty": "easy", "question": "What is a smart contract?"},
#         {"role": "Blockchain Developer", "type": "technical", "difficulty": "medium", "question": "How does Ethereum’s consensus mechanism work?"},
#         {"role": "Blockchain Developer", "type": "technical", "difficulty": "hard", "question": "Write a Solidity contract for a voting system."},
#         {"role": "Blockchain Developer", "type": "behavioral", "difficulty": "medium", "question": "Share a blockchain project you worked on."},
#         {"role": "Blockchain Developer", "type": "system_design", "difficulty": "hard", "question": "Design a decentralized finance (DeFi) platform."},
#         {"role": "Cloud Engineer", "type": "technical", "difficulty": "easy", "question": "What is the difference between IaaS and PaaS?"},
#         {"role": "Cloud Engineer", "type": "technical", "difficulty": "medium", "question": "How do you set up auto-scaling on AWS?"},
#         {"role": "Cloud Engineer", "type": "technical", "difficulty": "hard", "question": "Design a multi-cloud strategy for disaster recovery."},
#         {"role": "Cloud Engineer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a cloud migration you managed."},
#         {"role": "Cloud Engineer", "type": "system_design", "difficulty": "hard", "question": "Plan a cloud architecture for a global app."},
#         {"role": "DevOps Engineer", "type": "technical", "difficulty": "easy", "question": "What is CI/CD?"},
#         {"role": "DevOps Engineer", "type": "technical", "difficulty": "medium", "question": "How do you configure a Kubernetes pod?"},
#         {"role": "DevOps Engineer", "type": "technical", "difficulty": "hard", "question": "Design a CI/CD pipeline with GitHub Actions."},
#         {"role": "DevOps Engineer", "type": "behavioral", "difficulty": "medium", "question": "Describe a time you improved deployment speed."},
#         {"role": "DevOps Engineer", "type": "system_design", "difficulty": "hard", "question": "Plan a DevOps setup for a microservices app."},
#         {"role": "UI/UX Designer", "type": "technical", "difficulty": "easy", "question": "What is the difference between UI and UX?"},
#         {"role": "UI/UX Designer", "type": "technical", "difficulty": "medium", "question": "How do you conduct user research?"},
#         {"role": "UI/UX Designer", "type": "technical", "difficulty": "hard", "question": "Design a wireframe for a mobile banking app."},
#         {"role": "UI/UX Designer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a design project you led."},
#         {"role": "UI/UX Designer", "type": "system_design", "difficulty": "hard", "question": "Create a design system for a large-scale app."},
#         {"role": "Web Developer", "type": "technical", "difficulty": "easy", "question": "What does HTML5 offer over HTML4?"},
#         {"role": "Web Developer", "type": "technical", "difficulty": "medium", "question": "How do you optimize a website for SEO?"},
#         {"role": "Web Developer", "type": "technical", "difficulty": "hard", "question": "Build a responsive portfolio site with JavaScript."},
#         {"role": "Web Developer", "type": "behavioral", "difficulty": "medium", "question": "Share a web project you completed under pressure."},
#         {"role": "Web Developer", "type": "system_design", "difficulty": "hard", "question": "Design a scalable web app architecture."},
#         {"role": "Backend Developer", "type": "technical", "difficulty": "easy", "question": "What is REST API?"},
#         {"role": "Backend Developer", "type": "technical", "difficulty": "medium", "question": "How do you secure a backend API?"},
#         {"role": "Backend Developer", "type": "technical", "difficulty": "hard", "question": "Design a backend for a social media platform."},
#         {"role": "Backend Developer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a backend issue you resolved."},
#         {"role": "Backend Developer", "type": "system_design", "difficulty": "hard", "question": "Plan a distributed backend system."},
#         {"role": "Database Administrator", "type": "technical", "difficulty": "easy", "question": "What is a primary key?"},
#         {"role": "Database Administrator", "type": "technical", "difficulty": "medium", "question": "How do you optimize a slow SQL query?"},
#         {"role": "Database Administrator", "type": "technical", "difficulty": "hard", "question": "Design a database schema for an e-commerce site."},
#         {"role": "Database Administrator", "type": "behavioral", "difficulty": "medium", "question": "Describe a database recovery you performed."},
#         {"role": "Database Administrator", "type": "system_design", "difficulty": "hard", "question": "Plan a high-availability database system."},
#         {"role": "Machine Learning Engineer", "type": "technical", "difficulty": "easy", "question": "What is gradient descent?"},
#         {"role": "Machine Learning Engineer", "type": "technical", "difficulty": "medium", "question": "How do you evaluate a machine learning model?"},
#         {"role": "Machine Learning Engineer", "type": "technical", "difficulty": "hard", "question": "Implement a custom loss function in PyTorch."},
#         {"role": "Machine Learning Engineer", "type": "behavioral", "difficulty": "medium", "question": "Share a ML project you deployed."},
#         {"role": "Machine Learning Engineer", "type": "system_design", "difficulty": "hard", "question": "Design an ML pipeline for real-time predictions."},
#         {"role": "System Administrator", "type": "technical", "difficulty": "easy", "question": "What is a Linux file permission?"},
#         {"role": "System Administrator", "type": "technical", "difficulty": "medium", "question": "How do you configure a firewall?"},
#         {"role": "System Administrator", "type": "technical", "difficulty": "hard", "question": "Design a backup strategy for a server farm."},
#         {"role": "System Administrator", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a system outage you handled."},
#         {"role": "System Administrator", "type": "system_design", "difficulty": "hard", "question": "Plan a secure server infrastructure."},
#         {"role": "Embedded Systems Engineer", "type": "technical", "difficulty": "easy", "question": "What is an interrupt in embedded systems?"},
#         {"role": "Embedded Systems Engineer", "type": "technical", "difficulty": "medium", "question": "How do you debug a microcontroller?"},
#         {"role": "Embedded Systems Engineer", "type": "technical", "difficulty": "hard", "question": "Design an IoT device with low power consumption."},
#         {"role": "Embedded Systems Engineer", "type": "behavioral", "difficulty": "medium", "question": "Share an embedded project you completed."},
#         {"role": "Embedded Systems Engineer", "type": "system_design", "difficulty": "hard", "question": "Plan an embedded system for a smart home."},
#         {"role": "AR/VR Developer", "type": "technical", "difficulty": "easy", "question": "What is the difference between AR and VR?"},
#         {"role": "AR/VR Developer", "type": "technical", "difficulty": "medium", "question": "How do you optimize a Unity project for VR?"},
#         {"role": "AR/VR Developer", "type": "technical", "difficulty": "hard", "question": "Design an AR app for furniture placement."},
#         {"role": "AR/VR Developer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about an AR/VR project you built."},
#         {"role": "AR/VR Developer", "type": "system_design", "difficulty": "hard", "question": "Plan a multi-user VR collaboration platform."},
#         {"role": "Cybersecurity Specialist", "type": "technical", "difficulty": "easy", "question": "What is a DDoS attack?"},
#         {"role": "Cybersecurity Specialist", "type": "technical", "difficulty": "medium", "question": "How do you conduct a penetration test?"},
#         {"role": "Cybersecurity Specialist", "type": "technical", "difficulty": "hard", "question": "Design a security protocol for a financial app."},
#         {"role": "Cybersecurity Specialist", "type": "behavioral", "difficulty": "medium", "question": "Share a security breach you mitigated."},
#         {"role": "Cybersecurity Specialist", "type": "system_design", "difficulty": "hard", "question": "Plan a cybersecurity framework for a company."},
#         {"role": "Network Engineer", "type": "technical", "difficulty": "easy", "question": "What is the OSI model?"},
#         {"role": "Network Engineer", "type": "technical", "difficulty": "medium", "question": "How do you troubleshoot a network outage?"},
#         {"role": "Network Engineer", "type": "technical", "difficulty": "hard", "question": "Design a network for a multi-office company."},
#         {"role": "Network Engineer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a network upgrade you managed."},
#         {"role": "Network Engineer", "type": "system_design", "difficulty": "hard", "question": "Plan a secure, scalable network infrastructure."}
#     ]
#     try:
#         question_count = mongo.db.questions.count_documents({})
#         if force_reseed or question_count == 0:
#             mongo.db.questions.delete_many({})  # Clear existing questions
#             result = mongo.db.questions.insert_many(sample_questions)
#             print(f"Seeded {len(result.inserted_ids)} interview questions successfully.")
#         else:
#             print(f"Database already contains {question_count} questions—skipping seed unless forced.")
#     except pymongo.errors.PyMongoError as e:
#         print(f"Failed to seed questions: {e}")

# seed_interview_questions(force_reseed=True)  # Force reseed on startup

# @app.route("/interview", methods=["GET"])
# def interview():
#     return render_template("interview.html")

# @app.route("/api/interview/start", methods=["POST"])
# def start_interview():
#     role = request.json.get("role")
#     difficulty = request.json.get("difficulty", "medium")
#     if not role:
#         return jsonify({"success": False, "message": "Oh honey, pick a role to get started!"}), 400

#     try:
#         print(f"Fetching questions for role: {role}, difficulty: {difficulty}")  # Debug log
#         questions = list(mongo.db.questions.find({"role": role, "difficulty": difficulty}))
#         if not questions:
#             print(f"No exact match, falling back to all difficulties for {role}")  # Debug log
#             questions = list(mongo.db.questions.find({"role": role}))
#         if not questions:
#             return jsonify({"success": False, "message": f"No questions for {role} yet—try another one, sweetie!"}), 404
#         question = random.choice(questions)
#         print(f"Selected question: {question['question']}")  # Debug log
#         return jsonify({
#             "success": True,
#             "question": question["question"],
#             "question_id": str(question["_id"]),
#             "type": question["type"],
#             "difficulty": question["difficulty"]
#         })
#     except pymongo.errors.PyMongoError as e:
#         print(f"Database error: {e}")  # Debug log
#         return jsonify({"success": False, "message": f"Yikes, a little glitch: {e}—let’s try again!"}), 500

# @app.route("/api/interview/answer", methods=["POST"])
# def submit_answer():
#     role = request.json.get("role")
#     answer = request.json.get("answer")
#     question_id = request.json.get("question_id")
#     if not role or not answer or not question_id:
#         return jsonify({"success": False, "message": "Hey, give me a role, an answer, and a question ID, please!"}), 400

#     try:
#         question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
#         if not question:
#             return jsonify({"success": False, "message": "Oops, lost that question—let’s start fresh!"}), 404

#         feedback = generate_interview_feedback(answer, question["question"], question["type"])

#         questions = list(mongo.db.questions.find({
#             "role": role,
#             "type": question["type"],
#             "difficulty": question["difficulty"],
#             "_id": {"$ne": ObjectId(question_id)}
#         }))
#         if not questions:
#             questions = list(mongo.db.questions.find({"role": role, "_id": {"$ne": ObjectId(question_id)}}))
#         if questions:
#             next_question = random.choice(questions)
#             return jsonify({
#                 "success": True,
#                 "feedback": feedback,
#                 "next_question": next_question["question"],
#                 "next_question_id": str(next_question["_id"]),
#                 "type": next_question["type"],
#                 "difficulty": next_question["difficulty"]
#             })
#         return jsonify({
#             "success": True,
#             "feedback": feedback,
#             "next_question": "Wow, you rocked all the questions! Ready for a new role, champ?",
#             "next_question_id": "",
#             "type": "",
#             "difficulty": ""
#         })
#     except pymongo.errors.PyMongoError as e:
#         return jsonify({"success": False, "message": f"Uh-oh, database trouble: {e}—give it another go!"}), 500

# def generate_interview_feedback(answer, question, question_type):
#     answer_length = len(answer.strip())
#     # 25 conditions to catch all user quirks and encourage professionalism
#     if not answer or answer_length == 0:
#         return "Oh sweetie, you didn’t say anything! Give me a proper answer to wow them, please!"
#     elif answer.lower() in ["idk", "i don't know", "no idea", "idk sto asking", "dunno", "beats me", "pass"]:
#         return "Aw, don’t give up with ‘I don’t know’! Take a stab at it professionally, you’ve got this!"
#     elif answer_length < 10:
#         return "That’s super short, honey! Stretch it out with some details to show your stuff."
#     elif answer_length < 20:
#         return "Hmm, a bit brief—add more juice, like an example, to impress the interviewer!"
#     elif all(c.isdigit() for c in answer):
#         return "Numbers only? Nope, use words to flex your skills, darling!"
#     elif answer.isupper():
#         return "No shouting, sweetie! Keep it cool and pro—try a calm response."
#     elif any(word in answer.lower() for word in ["lol", "haha", "rofl", "lmao", "hehe"]):
#         return "Love the giggles, but let’s get serious—give a polished answer, okay?"
#     elif any(word in answer.lower() for word in ["dude", "bro", "mate", "yo", "buddy", "pal"]):
#         return "Let’s ditch the casual vibe—answer like you’re in the interview room, champ!"
#     elif any(word in answer.lower() for word in ["maybe", "sort of", "kinda", "eh", "meh"]):
#         return "No vagueness, honey! Be confident and clear—own that answer!"
#     elif any(word in answer.lower() for word in ["whatever", "fine", "ok", "sure", "yep"]):
#         return "‘Whatever’ won’t cut it! Give a thoughtful, detailed response, please!"
#     elif any(word in answer.lower() for word in ["boring", "stupid", "dumb", "lame"]):
#         return "Oh no, don’t call it boring! Show some enthusiasm and answer professionally!"
#     elif question_type in ["technical", "system_design"] and not any(word in answer.lower() for word in ["how", "why", "process", "design", "implement", "build"]):
#         return "Good try, but add ‘how’ or ‘why’ to show your tech chops—let’s make it shine!"
#     elif question_type == "behavioral" and not any(word in answer.lower() for word in ["i", "we", "team", "project", "experience", "job"]):
#         return "Nice start, but tell a personal story—use ‘I’ or ‘we’ to stand out!"
#     elif answer_length > 250:
#         return "Wow, you went big! Trim it down to the key points for a sleek, pro answer."
#     elif any(word in answer.lower() for word in ["not sure", "dunno if", "think so"]):
#         return "Avoid ‘not sure’—sound confident, even if you’re guessing, sweetie!"
#     elif question_type == "technical" and not any(word in answer.lower() for word in ["code", "example", "algorithm", "syntax"]):
#         return "Solid effort! Toss in a code snippet or example to boost your tech cred."
#     elif question_type == "behavioral" and not any(word in answer.lower() for word in ["result", "outcome", "impact", "success"]):
#         return "Great story! Add the result with STAR (Situation, Task, Action, Result)!"
#     elif question_type == "system_design" and not any(word in answer.lower() for word in ["scale", "trade-off", "architecture", "performance"]):
#         return "Nice plan! Talk about scalability or trade-offs to level up your design."
#     elif any(char in "!@#$%^&*()" for char in answer):
#         return "Whoa, no special characters, honey! Keep it clean and professional."
#     elif answer.startswith(("uh", "um", "er")):
#         return "Let’s skip the fillers—jump right into a strong, clear answer, okay?"
#     elif any(word in answer.lower() for word in ["help", "save me", "no clue"]):
#         return "Don’t worry, I’ve got your back! Try your best and give a solid response."
#     elif answer.endswith(("?", ".", "!!")):
#         return "End with confidence—avoid questions or extra punctuation, sweetie!"
#     elif answer_length < 50 and question_type in ["system_design", "technical"]:
#         return "That’s a bit light for a tech question! Add more depth, like steps or logic."
#     elif any(word in answer.lower() for word in ["easy", "hard", "tough"]):
#         return "Focus on the answer, not the difficulty—show your skills, champ!"
#     elif question_type == "behavioral" and answer_length < 30:
#         return "Short stories won’t impress—expand with details, like what you learned!"
#     # New conditions for partially correct answers
#     elif question_type == "technical" and any(word in answer.lower() for word in ["function", "variable", "loop"]) and answer_length < 100:
#         return "You’re on the right track with terms like ‘function’ or ‘loop’! Expand with more details or an example to really shine."
#     elif question_type == "technical" and any(word in answer.lower() for word in ["class", "object", "method"]) and not any(word in answer.lower() for word in ["inheritance", "polymorphism"]):
#         return "Great start mentioning ‘class’ or ‘object’! Add concepts like inheritance to show deeper knowledge."
#     elif question_type == "system_design" and any(word in answer.lower() for word in ["database", "server"]) and answer_length < 150:
#         return "Nice mention of ‘database’ or ‘server’! Build on it with scalability or load balancing details."
#     elif question_type == "behavioral" and any(word in answer.lower() for word in ["problem", "solved"]) and not any(word in answer.lower() for word in ["team", "result"]):
#         return "You’ve got a good start with ‘problem’ and ‘solved’! Include your team’s role or the result for a stronger story."
#     elif question_type == "technical" and any(word in answer.lower() for word in ["api", "endpoint"]) and not any(word in answer.lower() for word in ["rest", "http"]):
#         return "You’re close with ‘API’ or ‘endpoint’! Add REST or HTTP details to level up your answer."
#     elif question_type == "system_design" and any(word in answer.lower() for word in ["cache", "load"]) and answer_length < 200:
#         return "Love seeing ‘cache’ or ‘load’! Expand with how you’d implement it for better performance."
#     elif question_type == "behavioral" and any(word in answer.lower() for word in ["learned", "skill"]) and answer_length < 80:
#         return "You’re on point with ‘learned’ or ‘skill’! Give more context on how you applied it."
#     elif question_type == "technical" and any(word in answer.lower() for word in ["algorithm", "data"]) and not any(word in answer.lower() for word in ["time", "space"]):
#         return "Good use of ‘algorithm’ or ‘data’! Include time or space complexity for a pro touch."
#     elif question_type == "system_design" and any(word in answer.lower() for word in ["microservices", "api"]) and answer_length < 180:
#         return "You’re getting there with ‘microservices’ or ‘API’! Add how they communicate or scale."
#     elif question_type == "behavioral" and any(word in answer.lower() for word in ["challenge", "overcame"]) and not any(word in answer.lower() for word in ["strategy", "plan"]):
#         return "Nice work with ‘challenge’ and ‘overcame’! Share your strategy to make it stand out."
#     return "You’re killing it, honey! Maybe toss in a bit more context to really nail it."


# # Add these routes to your app.py file (replace the existing ones)

# # @app.route("/career-coach")
# # def career_coach_page():
# #     """Render the career coach page with embedded HTML"""
# #     return '''<!DOCTYPE html>
# # <html lang="en">
# # <head>
# #   <meta charset="UTF-8">
# #   <title>Career Coach</title>
# #   <style>
# #     body {
# #       font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
# #       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
# #       margin: 0;
# #       padding: 20px;
# #       min-height: 100vh;
# #     }
# #     .container {
# #       max-width: 800px;
# #       margin: 0 auto;
# #       background: white;
# #       padding: 30px;
# #       border-radius: 15px;
# #       box-shadow: 0 10px 30px rgba(0,0,0,0.1);
# #     }
# #     h1 {
# #       text-align: center;
# #       color: #333;
# #       margin-bottom: 30px;
# #       font-size: 2.5em;
# #     }
# #     #question {
# #       width: 100%;
# #       height: 120px;
# #       padding: 15px;
# #       border: 2px solid #e1e5e9;
# #       border-radius: 8px;
# #       font-size: 16px;
# #       resize: vertical;
# #       box-sizing: border-box;
# #     }
# #     #question:focus {
# #       outline: none;
# #       border-color: #667eea;
# #     }
# #     button {
# #       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
# #       color: white;
# #       padding: 12px 30px;
# #       border: none;
# #       border-radius: 8px;
# #       cursor: pointer;
# #       font-size: 16px;
# #       margin-top: 15px;
# #       transition: transform 0.2s;
# #     }
# #     button:hover {
# #       transform: translateY(-2px);
# #     }
# #     button:disabled {
# #       background: #ccc;
# #       cursor: not-allowed;
# #       transform: none;
# #     }
# #     #response {
# #       margin-top: 20px;
# #       padding: 20px;
# #       background-color: #f8f9fa;
# #       border-radius: 8px;
# #       border-left: 4px solid #667eea;
# #       white-space: pre-wrap;
# #       line-height: 1.6;
# #       min-height: 50px;
# #     }
# #     .loading {
# #       color: #667eea;
# #       font-style: italic;
# #     }
# #     .error {
# #       color: #dc3545;
# #       background-color: #f8d7da;
# #       border-left-color: #dc3545;
# #     }
# #   </style>
# # </head>
# # <body>
# #   <div class="container">
# #     <h1>🎯 AI Career Coach</h1>
# #     <form id="careerForm">
# #       <textarea id="question" placeholder="Ask me anything about your career! For example:
# # • How do I prepare for a software engineering interview?
# # • What skills should I learn for data science?
# # • How can I transition to a tech career?
# # • What should I include in my resume?" required></textarea>
# #       <button type="submit" id="submitBtn">Get Career Advice</button>
# #     </form>
# #     <div id="response"></div>
# #   </div>

# #   <script>
# #     document.getElementById("careerForm").addEventListener("submit", async (e) => {
# #       e.preventDefault();
      
# #       const question = document.getElementById("question").value.trim();
# #       const submitBtn = document.getElementById("submitBtn");
# #       const responseDiv = document.getElementById("response");
      
# #       if (!question) {
# #         responseDiv.innerHTML = "Please enter a question first!";
# #         responseDiv.className = "error";
# #         return;
# #       }
      
# #       // Show loading state
# #       submitBtn.disabled = true;
# #       submitBtn.textContent = "Getting advice...";
# #       responseDiv.innerHTML = "🤔 Thinking about your question...";
# #       responseDiv.className = "loading";

# #       try {
# #         const response = await fetch("/ask-career", {
# #           method: "POST",
# #           headers: {"Content-Type": "application/x-www-form-urlencoded"},
# #           body: new URLSearchParams({question})
# #         });

# #         const data = await response.json();
        
# #         if (data.error) {
# #           responseDiv.innerHTML = "❌ " + data.error;
# #           responseDiv.className = "error";
# #         } else {
# #           responseDiv.innerHTML = "💡 " + data.answer;
# #           responseDiv.className = "";
# #         }
# #       } catch (error) {
# #         responseDiv.innerHTML = "❌ Network error. Please check your connection and try again.";
# #         responseDiv.className = "error";
# #       } finally {
# #         // Reset button
# #         submitBtn.disabled = false;
# #         submitBtn.textContent = "Get Career Advice";
# #       }
# #     });
# #   </script>
# # </body>
# # </html>'''

# # @app.route("/ask-career", methods=["POST"])
# # def ask_career():
# #     """Handle career coaching questions"""
# #     try:
# #         user_input = request.form.get("question")
        
# #         if not user_input or not user_input.strip():
# #             return jsonify({"error": "Please provide a question"}), 400
        
# #         # Limit input length
# #         if len(user_input) > 1000:
# #             return jsonify({"error": "Question too long. Please keep it under 1000 characters."}), 400
        
# #         # Get response from AI model
# #         response = ask_career_bot(user_input.strip())
        
# #         # Check if the response indicates an error
# #         if response.startswith("Error:"):
# #             return jsonify({"error": response}), 500
            
# #         return jsonify({"answer": response})
        
# #     except Exception as e:
# #         return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

# # if __name__ == "__main__":
# #     app.run(debug=True)

# @app.route("/career-coach")
# def career_coach_page():
#     """Render the career coach page"""
#     return render_template("career_coach.html")

# @app.route("/ask-career", methods=["POST"])
# def ask_career():
#     """Handle career coaching questions"""
#     try:
#         user_input = request.form.get("question") or request.json.get("question")

#         if not user_input or not user_input.strip():
#             return jsonify({"error": "Please provide a question"}), 400
        
#         if len(user_input) > 1000:
#             return jsonify({"error": "Question too long. Please keep it under 1000 characters."}), 400
        
#         # Call your AI model
#         response = ask_career_bot(user_input.strip())

#         if response.startswith("Error:"):
#             return jsonify({"error": response}), 500
            
#         return jsonify({"answer": response})
        
#     except Exception as e:
#         print("ERROR in /ask-career:", str(e))  # helpful in terminal
#         return jsonify({"error": f"Something went wrong: {str(e)}"}), 500


# # @app.route("/resume-builder", methods=["GET", "POST"])
# # def resume_builder():
# #     """Resume builder feature"""
# #     if request.method == "POST":
# #         # Get form data
# #         resume_data = {
# #             "personal_info": {
# #                 "full_name": request.form.get("full_name", ""),
# #                 "email": request.form.get("email", ""),
# #                 "phone": request.form.get("phone", ""),
# #                 "address": request.form.get("address", ""),
# #                 "linkedin": request.form.get("linkedin", ""),
# #                 "website": request.form.get("website", "")
# #             },
# #             "professional_summary": request.form.get("professional_summary", ""),
# #             "experience": [],
# #             "education": [],
# #             "skills": request.form.get("skills", "").split(",") if request.form.get("skills") else [],
# #             "projects": [],
# #             "certifications": request.form.get("certifications", "").split(",") if request.form.get("certifications") else []
# #         }
        
# #         # Process experience entries
# #         exp_companies = request.form.getlist("exp_company")
# #         exp_positions = request.form.getlist("exp_position")
# #         exp_start_dates = request.form.getlist("exp_start_date")
# #         exp_end_dates = request.form.getlist("exp_end_date")
# #         exp_descriptions = request.form.getlist("exp_description")
        
# #         for i in range(len(exp_companies)):
# #             if exp_companies[i].strip():
# #                 resume_data["experience"].append({
# #                     "company": exp_companies[i],
# #                     "position": exp_positions[i],
# #                     "start_date": exp_start_dates[i],
# #                     "end_date": exp_end_dates[i],
# #                     "description": exp_descriptions[i]
# #                 })
        
# #         # Process education entries
# #         edu_institutions = request.form.getlist("edu_institution")
# #         edu_degrees = request.form.getlist("edu_degree")
# #         edu_years = request.form.getlist("edu_year")
# #         edu_gpas = request.form.getlist("edu_gpa")
        
# #         for i in range(len(edu_institutions)):
# #             if edu_institutions[i].strip():
# #                 resume_data["education"].append({
# #                     "institution": edu_institutions[i],
# #                     "degree": edu_degrees[i],
# #                     "year": edu_years[i],
# #                     "gpa": edu_gpas[i]
# #                 })
        
# #         # Process project entries
# #         proj_names = request.form.getlist("proj_name")
# #         proj_descriptions = request.form.getlist("proj_description")
# #         proj_technologies = request.form.getlist("proj_tech")
# #         proj_links = request.form.getlist("proj_link")
        
# #         for i in range(len(proj_names)):
# #             if proj_names[i].strip():
# #                 resume_data["projects"].append({
# #                     "name": proj_names[i],
# #                     "description": proj_descriptions[i],
# #                     "technologies": proj_technologies[i],
# #                     "link": proj_links[i]
# #                 })
        
# #         # Save to session for preview
# #         session["resume_data"] = resume_data
        
# #         # Generate resume content
# #         action = request.form.get("action")
# #         if action == "preview":
# #             return render_template("resume_preview.html", resume_data=resume_data)
# #         elif action == "download":
# #             # For now, redirect to preview. You can add PDF generation later
# #             return render_template("resume_preview.html", resume_data=resume_data, download_mode=True)
    
# #     return render_template("resume_builder.html")

# # @app.route("/resume-preview")
# # def resume_preview():
# #     """Show resume preview"""
# #     resume_data = session.get("resume_data")
# #     if not resume_data:
# #         flash("No resume data found. Please build your resume first.", "warning")
# #         return redirect(url_for("resume_builder"))
    
# #     return render_template("resume_preview.html", resume_data=resume_data)

# # @app.route("/download-resume")
# # def download_resume():
# #     """Download resume as HTML file"""
# #     resume_data = session.get("resume_data")
# #     if not resume_data:
# #         flash("No resume data found. Please build your resume first.", "warning")
# #         return redirect(url_for("resume_builder"))
    
# #     # Generate HTML content
# #     html_content = render_template("resume_download.html", resume_data=resume_data)
    
# #     # Create filename
# #     name = resume_data["personal_info"]["full_name"].replace(" ", "_") or "resume"
# #     filename = f"{name}_resume.html"
    
# #     # Save to uploads folder
# #     filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
# #     with open(filepath, "w", encoding="utf-8") as f:
# #         f.write(html_content)
    
# #     return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    

# # #new routes

# # @app.route("/ai-resume-coach")
# # def ai_resume_coach():
# #     """Main AI Resume Coach interface"""
# #     if "user_email" not in session:
# #         return redirect(url_for("login"))
# #     return render_template("ai_resume_coach.html")

# # @app.route("/api/resume-coach/start", methods=["POST"])
# # def start_resume_coaching():
# #     """Initialize a new resume coaching session"""
# #     if "user_email" not in session:
# #         return jsonify({"error": "Login required"}), 401
    
# #     # Initialize coaching session in MongoDB
# #     user = mongo.db.users.find_one({"email": session["user_email"]})
    
# #     coaching_session = {
# #         "user_id": user["_id"],
# #         "session_id": str(ObjectId()),
# #         "created_at": datetime.utcnow(),
# #         "current_step": "intro",
# #         "collected_data": {},
# #         "conversation_history": [],
# #         "resume_drafts": []
# #     }
    
# #     result = mongo.db.coaching_sessions.insert_one(coaching_session)
# #     session["coaching_session_id"] = str(result.inserted_id)
    
# #     intro_message = generate_intro_message(user.get("fullname", "there"))
    
# #     return jsonify({
# #         "success": True,
# #         "message": intro_message,
# #         "session_id": str(result.inserted_id),
# #         "step": "intro"
# #     })

# # @app.route("/api/resume-coach/chat", methods=["POST"])
# # def resume_coach_chat():
# #     """Handle conversational interactions with the AI resume coach"""
# #     if "user_email" not in session:
# #         return jsonify({"error": "Login required"}), 401
    
# #     data = request.json
# #     user_message = data.get("message", "").strip()
# #     session_id = data.get("session_id") or session.get("coaching_session_id")
    
# #     if not user_message:
# #         return jsonify({"error": "Please provide a message"}), 400
    
# #     if not session_id:
# #         return jsonify({"error": "No active coaching session"}), 400
    
# #     try:
# #         # Get current coaching session
# #         coaching_session = mongo.db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
# #         if not coaching_session:
# #             return jsonify({"error": "Coaching session not found"}), 404
        
# #         # Add user message to conversation history
# #         coaching_session["conversation_history"].append({
# #             "role": "user",
# #             "message": user_message,
# #             "timestamp": datetime.utcnow()
# #         })
        
# #         # Process the message and generate AI response
# #         ai_response = process_coaching_conversation(
# #             user_message, 
# #             coaching_session["current_step"],
# #             coaching_session["collected_data"],
# #             coaching_session["conversation_history"]
# #         )
        
# #         # Update coaching session
# #         coaching_session["conversation_history"].append({
# #             "role": "assistant", 
# #             "message": ai_response["message"],
# #             "timestamp": datetime.utcnow()
# #         })
        
# #         # Update collected data and current step
# #         if "data_update" in ai_response:
# #             coaching_session["collected_data"].update(ai_response["data_update"])
        
# #         if "next_step" in ai_response:
# #             coaching_session["current_step"] = ai_response["next_step"]
        
# #         # Save updated session
# #         mongo.db.coaching_sessions.update_one(
# #             {"_id": ObjectId(session_id)},
# #             {"$set": coaching_session}
# #         )
        
# #         return jsonify({
# #             "success": True,
# #             "message": ai_response["message"],
# #             "step": coaching_session["current_step"],
# #             "progress": ai_response.get("progress", 0),
# #             "suggestions": ai_response.get("suggestions", []),
# #             "can_generate_resume": ai_response.get("can_generate_resume", False)
# #         })
        
# #     except Exception as e:
# #         return jsonify({"error": f"Processing error: {str(e)}"}), 500

# # @app.route("/api/resume-coach/generate", methods=["POST"])
# # def generate_ai_resume():
# #     """Generate a complete resume based on collected data"""
# #     if "user_email" not in session:
# #         return jsonify({"error": "Login required"}), 401
    
# #     session_id = session.get("coaching_session_id")
# #     if not session_id:
# #         return jsonify({"error": "No active coaching session"}), 400
    
# #     try:
# #         coaching_session = mongo.db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
# #         if not coaching_session:
# #             return jsonify({"error": "Coaching session not found"}), 404
        
# #         # Generate resume using collected data
# #         resume_content = generate_complete_resume(
# #             coaching_session["collected_data"],
# #             request.json.get("target_role", ""),
# #             request.json.get("industry", "")
# #         )
        
# #         # Save generated resume
# #         resume_draft = {
# #             "generated_at": datetime.utcnow(),
# #             "target_role": request.json.get("target_role", ""),
# #             "industry": request.json.get("industry", ""),
# #             "content": resume_content
# #         }
        
# #         coaching_session["resume_drafts"].append(resume_draft)
        
# #         mongo.db.coaching_sessions.update_one(
# #             {"_id": ObjectId(session_id)},
# #             {"$set": {"resume_drafts": coaching_session["resume_drafts"]}}
# #         )
        
# #         return jsonify({
# #             "success": True,
# #             "resume_html": resume_content["html"],
# #             "resume_text": resume_content["text"],
# #             "suggestions": resume_content.get("suggestions", [])
# #         })
        
# #     except Exception as e:
# #         return jsonify({"error": f"Generation error: {str(e)}"}), 500

# # @app.route("/api/resume-coach/optimize", methods=["POST"])
# # def optimize_resume_for_role():
# #     """Optimize existing resume for a specific job/role"""
# #     if "user_email" not in session:
# #         return jsonify({"error": "Login required"}), 401
    
# #     data = request.json
# #     target_role = data.get("target_role", "")
# #     job_description = data.get("job_description", "")
# #     current_resume = data.get("current_resume", "")
    
# #     if not target_role and not job_description:
# #         return jsonify({"error": "Please provide target role or job description"}), 400
    
# #     try:
# #         optimization = optimize_resume_content(current_resume, target_role, job_description)
        
# #         return jsonify({
# #             "success": True,
# #             "optimized_content": optimization["content"],
# #             "changes_made": optimization["changes"],
# #             "suggestions": optimization["suggestions"],
# #             "keyword_matches": optimization.get("keyword_matches", [])
# #         })
        
# #     except Exception as e:
# #         return jsonify({"error": f"Optimization error: {str(e)}"}), 500

# # # AI Processing Functions (add these to a separate file like ai_resume_coach.py)

# # def generate_intro_message(user_name):
# #     """Generate personalized intro message"""
# #     return f"""Hi {user_name}! I'm your AI Resume Coach, and I'm here to help you create a standout resume that gets interviews.

# # Instead of just filling out a boring form, we're going to have a conversation where I learn about your unique experiences, skills, and career goals. Then I'll craft a personalized resume that tells your story effectively.

# # Let's start with this: What type of role are you targeting, or what's your dream job? For example:
# # • "Software Engineer at a tech startup"
# # • "Marketing Manager in healthcare" 
# # • "Data Scientist transitioning from academia"

# # Tell me about your career goals!"""

# # def process_coaching_conversation(user_message, current_step, collected_data, conversation_history):
# #     """Process user input and generate appropriate AI responses"""
    
# #     # Analyze user message for key information
# #     extracted_info = extract_information_from_message(user_message, current_step)
    
# #     if current_step == "intro":
# #         return handle_intro_step(user_message, extracted_info)
# #     elif current_step == "role_clarification":
# #         return handle_role_step(user_message, extracted_info, collected_data)
# #     elif current_step == "experience_gathering":
# #         return handle_experience_step(user_message, extracted_info, collected_data)
# #     elif current_step == "skills_assessment":
# #         return handle_skills_step(user_message, extracted_info, collected_data)
# #     elif current_step == "achievements_exploration":
# #         return handle_achievements_step(user_message, extracted_info, collected_data)
# #     elif current_step == "education_details":
# #         return handle_education_step(user_message, extracted_info, collected_data)
# #     elif current_step == "final_review":
# #         return handle_final_review_step(user_message, extracted_info, collected_data)
# #     else:
# #         return {
# #             "message": "I'm here to help! What would you like to work on next?",
# #             "next_step": current_step
# #         }

# # def extract_information_from_message(message, current_step):
# #     """Extract structured information from user's natural language input"""
# #     # This would use NLP techniques or AI models to parse the message
# #     # For now, using simple keyword matching and patterns
    
# #     extracted = {
# #         "job_titles": [],
# #         "companies": [],
# #         "skills": [],
# #         "years_experience": None,
# #         "education": {},
# #         "achievements": []
# #     }
    
# #     # Simple pattern matching (you'd want to use more sophisticated NLP here)
# #     import re
    
# #     # Extract years of experience
# #     years_match = re.search(r'(\d+)\s*(?:years?|yrs?)', message.lower())
# #     if years_match:
# #         extracted["years_experience"] = int(years_match.group(1))
    
# #     # Extract common job titles
# #     job_keywords = ['developer', 'engineer', 'analyst', 'manager', 'designer', 'architect', 'consultant']
# #     for keyword in job_keywords:
# #         if keyword in message.lower():
# #             extracted["job_titles"].append(keyword)
    
# #     # Extract skills (look for programming languages, tools)
# #     skill_keywords = ['python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker', 'git']
# #     for skill in skill_keywords:
# #         if skill in message.lower():
# #             extracted["skills"].append(skill)
    
# #     return extracted

# # def handle_intro_step(user_message, extracted_info):
# #     """Handle the introduction step"""
# #     response = f"""Perfect! I can see you're interested in roles involving {', '.join(extracted_info['job_titles']) if extracted_info['job_titles'] else 'your target field'}.

# # Now I need to understand your background better. Let's talk about your work experience:

# # • How many years of professional experience do you have?
# # • What's your most recent or current job title and company?
# # • What are 2-3 key responsibilities or achievements you're proud of?

# # Don't worry about perfect formatting - just tell me about your experience naturally!"""
    
# #     data_update = {
# #         "target_roles": extracted_info["job_titles"],
# #         "raw_intro": user_message
# #     }
    
# #     return {
# #         "message": response,
# #         "next_step": "experience_gathering",
# #         "data_update": data_update,
# #         "progress": 10
# #     }

# # def handle_experience_step(user_message, extracted_info, collected_data):
# #     """Handle experience gathering"""
# #     # Store experience information
# #     if "experience" not in collected_data:
# #         collected_data["experience"] = []
    
# #     collected_data["experience"].append({
# #         "raw_text": user_message,
# #         "extracted_info": extracted_info,
# #         "timestamp": datetime.utcnow().isoformat()
# #     })
    
# #     response = """Great information! I can already see some valuable experience there.

# # Now let's dive into your skills. Instead of just listing them, tell me:

# # • What technical skills do you use daily in your work?
# # • What tools, software, or programming languages are you strongest with?
# # • Any certifications or specialized training you have?
# # • What would colleagues say you're exceptionally good at?

# # Think beyond just technical skills - include soft skills, leadership abilities, or domain expertise!"""

# #     return {
# #         "message": response,
# #         "next_step": "skills_assessment", 
# #         "data_update": {"experience_raw": user_message},
# #         "progress": 35,
# #         "suggestions": generate_experience_suggestions(extracted_info)
# #     }

# # def handle_skills_step(user_message, extracted_info, collected_data):
# #     """Handle skills assessment"""
# #     response = """Excellent! Those skills will definitely make you stand out.

# # Let's talk about your achievements and impact. This is where most people struggle, but it's crucial:

# # • Tell me about a project or accomplishment you're really proud of
# # • Any numbers/metrics that show your impact? (increased efficiency, saved costs, etc.)
# # • Recognition, awards, or positive feedback you've received?
# # • Problems you've solved or improvements you've made?

# # Remember: Employers love seeing concrete results, not just responsibilities!"""

# #     return {
# #         "message": response,
# #         "next_step": "achievements_exploration",
# #         "data_update": {"skills_raw": user_message, "extracted_skills": extracted_info["skills"]},
# #         "progress": 60,
# #         "suggestions": generate_skills_suggestions(extracted_info["skills"])
# #     }

# # def handle_achievements_step(user_message, extracted_info, collected_data):
# #     """Handle achievements exploration"""
# #     response = """Those achievements are impressive! I can already see how they'll strengthen your resume.

# # Let's cover your educational background:

# # • What's your highest degree and field of study?
# # • University/institution name and graduation year?
# # • Any relevant coursework, academic projects, or honors?
# # • Additional certifications, bootcamps, or online courses?

# # Don't undersell yourself - include anything that demonstrates continuous learning!"""

# #     return {
# #         "message": response,
# #         "next_step": "education_details",
# #         "data_update": {"achievements_raw": user_message},
# #         "progress": 80
# #     }

# # def handle_education_step(user_message, extracted_info, collected_data):
# #     """Handle education details"""
# #     response = f"""Perfect! I now have a comprehensive picture of your background.

# # Let me summarize what we've gathered:
# # • Target Role: {', '.join(collected_data.get('target_roles', ['Professional role']))}
# # • Experience: {len(collected_data.get('experience', []))} work experiences shared
# # • Skills: {len(extracted_info.get('skills', []))} technical skills identified
# # • Education: {user_message[:100]}...

# # Would you like me to:
# # 1. Generate your complete resume now
# # 2. Ask a few more targeted questions to strengthen specific sections
# # 3. Focus on optimizing for a particular job posting

# # What sounds best to you?"""

# #     return {
# #         "message": response,
# #         "next_step": "final_review",
# #         "data_update": {"education_raw": user_message},
# #         "progress": 95,
# #         "can_generate_resume": True
# #     }

# # def generate_complete_resume(collected_data, target_role="", industry=""):
# #     """Generate a complete resume from collected conversational data"""
    
# #     # Parse collected data into structured resume sections
# #     resume_sections = parse_conversational_data(collected_data)
    
# #     # Generate AI-enhanced content for each section
# #     enhanced_resume = {
# #         "personal_info": enhance_personal_info(resume_sections.get("personal_info", {})),
# #         "professional_summary": generate_professional_summary(resume_sections, target_role, industry),
# #         "experience": enhance_experience_section(resume_sections.get("experience", []), target_role),
# #         "skills": enhance_skills_section(resume_sections.get("skills", []), target_role),
# #         "education": enhance_education_section(resume_sections.get("education", [])),
# #         "achievements": extract_and_format_achievements(resume_sections.get("achievements", []))
# #     }
    
# #     # Generate HTML and text versions
# #     html_content = generate_resume_html(enhanced_resume)
# #     text_content = generate_resume_text(enhanced_resume)
    
# #     return {
# #         "html": html_content,
# #         "text": text_content,
# #         "structured_data": enhanced_resume,
# #         "suggestions": generate_resume_suggestions(enhanced_resume, target_role)
# #     }

# # def optimize_resume_content(current_resume, target_role, job_description):
# #     """Optimize resume for specific role/job posting"""
    
# #     # Analyze job requirements
# #     job_keywords = extract_job_keywords(job_description)
# #     required_skills = extract_required_skills(job_description)
    
# #     # Analyze current resume
# #     current_keywords = extract_resume_keywords(current_resume)
    
# #     # Generate optimization suggestions
# #     optimizations = {
# #         "keyword_optimization": suggest_keyword_improvements(current_keywords, job_keywords),
# #         "content_rewriting": suggest_content_rewrites(current_resume, target_role),
# #         "section_prioritization": suggest_section_order(current_resume, job_description),
# #         "skill_highlighting": suggest_skill_emphasis(current_resume, required_skills)
# #     }
    
# #     # Apply optimizations
# #     optimized_content = apply_optimizations(current_resume, optimizations)
    
# #     return {
# #         "content": optimized_content,
# #         "changes": optimizations,
# #         "suggestions": [
# #             "Tailored content for target role",
# #             f"Added {len(job_keywords)} relevant keywords",
# #             "Emphasized matching skills and experience",
# #             "Improved action verbs and impact statements"
# #         ],
# #         "keyword_matches": calculate_keyword_overlap(current_keywords, job_keywords)
# #     }

# # # Helper functions for AI processing

# # def generate_professional_summary(resume_sections, target_role, industry):
# #     """Generate AI-powered professional summary"""
# #     experience_years = estimate_years_from_text(resume_sections.get("experience", []))
# #     key_skills = resume_sections.get("skills", [])[:5]  # Top 5 skills
    
# #     summary_template = f"""Results-driven {target_role or 'professional'} with {experience_years}+ years of experience in {industry or 'technology'}. 
# # Proven expertise in {', '.join(key_skills[:3]) if key_skills else 'relevant technologies'} with a track record of delivering impactful solutions. 
# # Strong problem-solving abilities combined with {', '.join(key_skills[3:5]) if len(key_skills) > 3 else 'collaborative leadership'} skills."""
    
# #     return enhance_with_ai_suggestions(summary_template, "professional_summary")

# # def enhance_experience_section(experience_data, target_role):
# #     """Enhance experience descriptions with AI"""
# #     enhanced_experiences = []
    
# #     for exp in experience_data:
# #         enhanced_exp = {
# #             "company": extract_company_name(exp.get("raw_text", "")),
# #             "position": extract_position_title(exp.get("raw_text", "")),
# #             "duration": extract_duration(exp.get("raw_text", "")),
# #             "achievements": enhance_achievement_bullets(exp.get("raw_text", ""), target_role)
# #         }
# #         enhanced_experiences.append(enhanced_exp)
    
# #     return enhanced_experiences

# # def enhance_achievement_bullets(raw_text, target_role):
# #     """Convert raw experience text into polished achievement bullets"""
# #     # This would use AI to rewrite experience descriptions
# #     # For now, using rule-based enhancement
    
# #     sentences = raw_text.split('.')
# #     enhanced_bullets = []
    
# #     action_verbs = ["Developed", "Implemented", "Led", "Optimized", "Designed", "Created", "Managed", "Improved"]
    
# #     for sentence in sentences[:4]:  # Max 4 bullets per role
# #         if len(sentence.strip()) > 10:
# #             enhanced = enhance_sentence_with_action_verb(sentence.strip(), action_verbs)
# #             enhanced_bullets.append(enhanced)
    
# #     return enhanced_bullets

# # def parse_conversational_data(collected_data):
# #     """Parse natural language responses into structured resume data"""
# #     # This would use NLP to extract structured information
# #     # For demonstration, using simple parsing
    
# #     parsed = {
# #         "personal_info": {},
# #         "experience": collected_data.get("experience", []),
# #         "skills": [],
# #         "education": [],
# #         "achievements": []
# #     }
    
# #     # Parse skills from raw text
# #     if "skills_raw" in collected_data:
# #         parsed["skills"] = extract_skills_from_text(collected_data["skills_raw"])
    
# #     # Parse achievements
# #     if "achievements_raw" in collected_data:
# #         parsed["achievements"] = extract_achievements_from_text(collected_data["achievements_raw"])
    
# #     return parsed

# # # Integration with existing model.py functions

# # def generate_interview_feedback(answer, question, question_type):
# #     """Enhanced interview feedback using AI coaching principles"""
    
# #     # Your existing feedback logic here, but enhanced
# #     answer_length = len(answer.strip())
    
# #     if answer_length < 20:
# #         return "That's quite brief! In a real interview, aim for 1-2 minutes of detailed explanation. Try expanding with specific examples or step-by-step reasoning."
    
# #     # Use AI to generate more sophisticated feedback
# #     return generate_ai_interview_feedback(answer, question, question_type)

# # def generate_ai_interview_feedback(answer, question, question_type):
# #     """Generate AI-powered interview feedback"""
    
# #     feedback_prompt = f"""
# #     Question Type: {question_type}
# #     Question: {question}
# #     Candidate Answer: {answer}
    
# #     Provide constructive interview feedback focusing on:
# #     1. Content accuracy and completeness
# #     2. Communication clarity
# #     3. Professional presentation
# #     4. Specific improvement suggestions
# #     """
    
# #     # This would call your AI model (OpenAI, local model, etc.)
# #     # For now, return enhanced rule-based feedback
    
# #     if question_type == "technical":
# #         return generate_technical_feedback(answer, question)
# #     elif question_type == "behavioral":
# #         return generate_behavioral_feedback(answer, question)
# #     elif question_type == "system_design":
# #         return generate_system_design_feedback(answer, question)
    
# #     return "Good effort! Consider adding more specific examples and details to strengthen your response."

# # # Utility functions

# # def extract_skills_from_text(text):
# #     """Extract skills from natural language description"""
# #     # Simple implementation - you'd want more sophisticated NLP here
# #     common_skills = [
# #         'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker', 
# #         'kubernetes', 'git', 'agile', 'scrum', 'leadership', 'project management'
# #     ]
    
# #     found_skills = []
# #     text_lower = text.lower()
    
# #     for skill in common_skills:
# #         if skill in text_lower:
# #             found_skills.append(skill.title())
    
# #     return found_skills

# # def enhance_with_ai_suggestions(content, section_type):
# #     """Enhance content with AI suggestions"""
# #     # This would integrate with your existing AI models
# #     # Return enhanced version of the content
# #     return content

# # def estimate_years_from_text(experience_data):
# #     """Estimate total years of experience from text descriptions"""
# #     # Simple estimation logic
# #     return max(3, len(experience_data))  # Default minimum 3 years

# # # Add these routes for the new AI coach interface    
# # if __name__ == "__main__":
# #     app.run(debug=True)

# resume_coach = ResumeCoach()

# # Replace /resume-builder with redirect to /ai-resume-coach
# @app.route("/resume-builder", methods=["GET", "POST"])
# def resume_builder():
#     """Redirect to AI Resume Coach"""
#     return redirect(url_for("ai_resume_coach"))

# @app.route("/ai-resume-coach")
# def ai_resume_coach():
#     """Main AI Resume Coach interface"""
#     if "user_email" not in session:
#         return redirect(url_for("login"))
#     return render_template("ai_resume_coach.html")

# @app.route("/api/resume-coach/start", methods=["POST"])
# def start_resume_coaching():
#     """Initialize a new resume coaching session"""
#     if "user_email" not in session:
#         return jsonify({"error": "Login required"}), 401
    
#     user = mongo.db.users.find_one({"email": session["user_email"]})
#     coaching_session = {
#         "user_id": user["_id"],
#         "session_id": str(ObjectId()),
#         "created_at": datetime.utcnow(),
#         "current_step": "intro",
#         "collected_data": {},
#         "conversation_history": [],
#         "resume_drafts": []
#     }
    
#     result = mongo.db.coaching_sessions.insert_one(coaching_session)
#     session["coaching_session_id"] = str(result.inserted_id)
    
#     intro_message = f"""Hi {user.get('fullname', 'there')}! I'm your AI Resume Coach, here to craft a standout resume.
# Tell me: **What type of role are you targeting?** (e.g., Software Engineer, Marketing Manager)"""
    
#     return jsonify({
#         "success": True,
#         "message": intro_message,
#         "session_id": str(result.inserted_id),
#         "step": "intro"
#     })

# @app.route("/api/resume-coach/chat", methods=["POST"])
# def resume_coach_chat():
#     """Handle conversational interactions"""
#     if "user_email" not in session:
#         return jsonify({"error": "Login required"}), 401
    
#     data = request.json
#     user_message = data.get("message", "").strip()
#     session_id = data.get("session_id") or session.get("coaching_session_id")
    
#     if not user_message:
#         return jsonify({"error": "Please provide a message"}), 400
    
#     if not session_id:
#         return jsonify({"error": "No active coaching session"}), 400
    
#     try:
#         coaching_session = mongo.db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
#         if not coaching_session:
#             return jsonify({"error": "Coaching session not found"}), 404
        
#         coaching_session["conversation_history"].append({
#             "role": "user",
#             "message": user_message,
#             "timestamp": datetime.utcnow()
#         })
        
#         ai_response = resume_coach.process_conversation(
#             user_message, 
#             coaching_session["current_step"],
#             coaching_session["collected_data"],
#             coaching_session["conversation_history"]
#         )
        
#         coaching_session["conversation_history"].append({
#             "role": "assistant", 
#             "message": ai_response["message"],
#             "timestamp": datetime.utcnow()
#         })
        
#         if "data_update" in ai_response:
#             coaching_session["collected_data"].update(ai_response["data_update"])
        
#         if "next_step" in ai_response:
#             coaching_session["current_step"] = ai_response["next_step"]
        
#         mongo.db.coaching_sessions.update_one(
#             {"_id": ObjectId(session_id)},
#             {"$set": coaching_session}
#         )
        
#         return jsonify({
#             "success": True,
#             "message": ai_response["message"],
#             "step": coaching_session["current_step"],
#             "progress": ai_response.get("progress", 0),
#             "suggestions": ai_response.get("suggestions", []),
#             "can_generate_resume": ai_response.get("can_generate_resume", False)
#         })
#     except Exception as e:
#         return jsonify({"error": f"Processing error: {str(e)}"}), 500

# @app.route("/api/resume-coach/generate", methods=["POST"])
# def generate_ai_resume():
#     """Generate a complete resume"""
#     if "user_email" not in session:
#         return jsonify({"error": "Login required"}), 401
    
#     session_id = session.get("coaching_session_id")
#     if not session_id:
#         return jsonify({"error": "No active coaching session"}), 400
    
#     try:
#         coaching_session = mongo.db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
#         if not coaching_session:
#             return jsonify({"error": "Coaching session not found"}), 404
        
#         resume_content = resume_coach.generate_complete_resume(
#             coaching_session["collected_data"],
#             request.json.get("target_role", ""),
#             request.json.get("industry", "")
#         )
        
#         resume_draft = {
#             "generated_at": datetime.utcnow(),
#             "target_role": request.json.get("target_role", ""),
#             "industry": request.json.get("industry", ""),
#             "content": resume_content
#         }
        
#         coaching_session["resume_drafts"].append(resume_draft)
#         mongo.db.coaching_sessions.update_one(
#             {"_id": ObjectId(session_id)},
#             {"$set": {"resume_drafts": coaching_session["resume_drafts"]}}
#         )
        
#         return jsonify({
#             "success": True,
#             "resume_html": resume_content["html"],
#             "resume_text": resume_content["text"],
#             "suggestions": resume_content.get("suggestions", [])
#         })
#     except Exception as e:
#         return jsonify({"error": f"Generation error: {str(e)}"}), 500

# @app.route("/api/resume-coach/optimize", methods=["POST"])
# def optimize_resume_for_role():
#     """Optimize existing resume for a specific job/role"""
#     if "user_email" not in session:
#         return jsonify({"error": "Login required"}), 401
    
#     data = request.json
#     target_role = data.get("target_role", "")
#     job_description = data.get("job_description", "")
#     current_resume = data.get("current_resume", "")
    
#     if not target_role and not job_description:
#         return jsonify({"error": "Please provide target role or job description"}), 400
    
#     try:
#         optimization = resume_coach.optimize_resume_content(current_resume, target_role, job_description)
#         return jsonify({
#             "success": True,
#             "optimized_content": optimization["content"],
#             "changes_made": optimization["changes"],
#             "suggestions": optimization["suggestions"],
#             "keyword_matches": optimization.get("keyword_matches", [])
#         })
#     except Exception as e:
#         return jsonify({"error": f"Optimization error: {str(e)}"}), 500

# @app.route("/download-ai-resume", methods=["GET"])
# def download_ai_resume():
#     """Download generated resume as HTML"""
#     if "user_email" not in session:
#         flash("Login required to download resume.", "warning")
#         return redirect(url_for("login"))
    
#     session_id = session.get("coaching_session_id")
#     if not session_id:
#         flash("No active coaching session found.", "warning")
#         return redirect(url_for("ai_resume_coach"))
    
#     coaching_session = mongo.db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
#     if not coaching_session or not coaching_session.get("resume_drafts"):
#         flash("No resume generated yet. Complete the coaching session first.", "warning")
#         return redirect(url_for("ai_resume_coach"))
    
#     latest_draft = coaching_session["resume_drafts"][-1]["content"]
#     html_content = latest_draft["html"]
    
#     filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
#     filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    
#     with open(filepath, "w", encoding="utf-8") as f:
#         f.write(html_content)
    
#     return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

# # ... (keep all other existing routes from your app.py)

# if __name__ == "__main__":
#     app.run(debug=True)

from ai_resume_coach import ResumeCoach
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import os
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime
from model import analyze_resume, analyze_resume_file, generate_ai_suggestion, generate_feedback
import random
import pymongo
from career_model import ask_career_bot

app = Flask(__name__)
app.secret_key = "skillbridge_secret_key"

# MongoDB config
app.config["MONGO_URI"] = "mongodb://localhost:27017/skillbridge"
mongo = PyMongo(app)

# Upload config
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def landing():
    return render_template("landingpage.html")

@app.route("/resume", methods=["GET", "POST"])
def resume():
    user_skills = job_skills = missing_skills = []
    ai_suggestion = ""
    feedback_list = []
    resume_text = ""
    filename = None

    if request.method == "POST":
        job = request.form.get("job", "").strip()
        role = request.form.get("role", "").strip()
        file = request.files.get("resume_file", None)
        resume_text = request.form.get("resume", "").strip()

        if not file and not resume_text and not job:
            return render_template("index.html", error="Please provide either a resume or job description.")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            if filepath.lower().endswith(".txt"):
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    resume_text = f.read()
            elif filepath.lower().endswith(".pdf"):
                import PyPDF2
                with open(filepath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    resume_text = "".join(page.extract_text() or "" for page in reader.pages)

            user_skills, job_skills, missing_skills = analyze_resume_file(filepath, job, role)

        elif resume_text:
            user_skills, job_skills, missing_skills = analyze_resume(resume_text, job, role)

        ai_suggestion = generate_ai_suggestion(user_skills, missing_skills, role)
        feedback_list = generate_feedback(resume_text, user_skills, job_skills, missing_skills)

    return render_template(
        "index.html",
        user_skills=user_skills,
        job_skills=job_skills,
        missing_skills=missing_skills,
        ai_suggestion=ai_suggestion,
        feedback=feedback_list,
        filename=filename
    )

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         email = request.form.get("email")
#         if mongo.db.users.find_one({"email": email}):
#             return render_template("register.html", error="Email already registered.")
        
#         user_data = {
#             "fullname": request.form.get("fullname"),
#             "email": email,
#             "password": request.form.get("password"),
#             "career_level": request.form.get("career_level"),
#             "country": request.form.get("country"),
#             "education_level": request.form.get("education_level"),
#         }

#         mongo.db.users.insert_one(user_data)
#         return render_template("register.html", success="Registration successful!")

#     return render_template("register.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        if mongo.db.users.find_one({"email": email}):
            return render_template("register.html", error="Email already registered.")
        
        user_data = {
            "fullname": request.form.get("fullname"),
            "email": email,
            "password": request.form.get("password"),  # ⚠️ consider hashing later
            "career_level": request.form.get("career_level"),
            "country": request.form.get("country"),
            "education_level": request.form.get("education_level"),
        }

        mongo.db.users.insert_one(user_data)
        # ✅ Redirect to login page instead of showing register page again
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = mongo.db.users.find_one({"email": email})
        if user and user["password"] == password:
            session["user_email"] = user["email"]
            session["fullname"] = user["fullname"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid email or password.")
    return render_template("login.html")

@app.route("/api/user")
def get_user():
    if "user_email" in session:
        return {"fullname": session.get("fullname", "User")}
    return {}, 401

@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session["fullname"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))

@app.route("/jobs")
def view_jobs():
    jobs = list(mongo.db.jobs.find())
    return render_template("job_application.html", jobs=jobs)

@app.route("/apply", methods=["POST"])
def apply_job():
    if "user_email" not in session:
        flash("You need to log in to apply.", "warning")
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"email": session["user_email"]})
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login"))

    job_id = request.form.get("job_id")
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    message = request.form.get("message")
    resume = request.files.get("resume")

    resume_path = None
    if resume and allowed_file(resume.filename):
        filename = secure_filename(f"{name.replace(' ', '_')}_{resume.filename}")
        resume_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        resume.save(resume_path)

    mongo.db.applications.insert_one({
        "job_id": ObjectId(job_id),
        "user_id": user["_id"],
        "name": name,
        "email": email,
        "phone": phone,
        "message": message,
        "resume_path": resume_path,
    })

    flash("Your application has been submitted!", "success")
    return redirect(url_for("my_applications"))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        if not all([name, email, subject, message]):
            flash("All fields are required.", "danger")
            return render_template("contact.html")

        # Save contact message to MongoDB
        mongo.db.contact_messages.insert_one({
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "timestamp": datetime.utcnow(),
            "status": "unread"
        })

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")

@app.route("/my-applications")
def my_applications():
    if "user_email" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"email": session["user_email"]})
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("logout"))

    applications = mongo.db.applications.find({"user_id": user["_id"]})
    return render_template("my_applications.html", applications=applications)

@app.route("/bookmark/<job_id>", methods=["POST"])
def bookmark_job(job_id):
    if "user_email" not in session:
        return jsonify({"success": False, "message": "Login required"}), 401

    user = mongo.db.users.find_one({"email": session["user_email"]})
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    user_id = user["_id"]
    job_obj_id = ObjectId(job_id)

    if mongo.db.bookmarks.find_one({"user_id": user_id, "job_id": job_obj_id}):
        return jsonify({"success": False, "message": "Already bookmarked"})

    mongo.db.bookmarks.insert_one({"user_id": user_id, "job_id": job_obj_id})
    return jsonify({"success": True, "message": "Job bookmarked!"})

@app.route("/bookmarks")
def bookmarks():
    if "user_email" not in session:
        flash("Please login to view bookmarks", "warning")
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"email": session["user_email"]})
    if not user:
        flash("User not found", "danger")
        return redirect(url_for("login"))

    bookmark_entries = list(mongo.db.bookmarks.find({"user_id": user["_id"]}))
    job_ids = [entry["job_id"] for entry in bookmark_entries]
    saved_jobs = list(mongo.db.jobs.find({"_id": {"$in": job_ids}}))

    return render_template("bookmarks.html", saved_jobs=saved_jobs)

@app.route("/remove-bookmark/<job_id>", methods=["POST"])
def remove_bookmark(job_id):
    if "user_email" not in session:
        return jsonify({"success": False, "message": "Login required"}), 401

    user = mongo.db.users.find_one({"email": session["user_email"]})
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    mongo.db.bookmarks.delete_one({"user_id": user["_id"], "job_id": ObjectId(job_id)})
    return redirect(url_for("bookmarks"))

@app.route("/notifications")
def notifications():
    if "user_email" not in session:
        return redirect(url_for("login"))

    user_email = session["user_email"]
    user = mongo.db.users.find_one({"email": user_email})
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("logout"))

    notifications = list(mongo.db.applications.find({
        "user_id": user["_id"],
        "notification": {"$exists": True}
    }))

    messages = list(mongo.db.messages.find({"email": user_email}))

    return render_template(
        "notifications.html",
        messages=messages,
        notifications=notifications
    )

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["admin"] = True
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid credentials.")

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    return render_template("admin_dashboard.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    session.pop("role", None)
    return redirect(url_for("admin_login"))

@app.route("/admin/users")
def admin_users():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    users = list(mongo.db.users.find())
    return render_template("admin_users.html", users=users)

@app.route("/admin/jobs", methods=["GET", "POST"])
def manage_jobs():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        job = {
            "title": request.form.get("title"),
            "company": request.form.get("company"),
            "location": request.form.get("location"),
            "type": request.form.get("type"),
            "posted_date": request.form.get("posted_date"),
            "description": request.form.get("description"),
        }
        mongo.db.jobs.insert_one(job)
        return redirect(url_for("manage_jobs"))

    jobs = list(mongo.db.jobs.find())
    return render_template("admin_jobs.html", jobs=jobs)

@app.route("/admin/applications")
def admin_applications():
    if session.get("role") != "admin":
        flash("Admins only!", "danger")
        return redirect(url_for("landing"))

    apps = list(mongo.db.applications.find())
    for app in apps:
        job = mongo.db.jobs.find_one({"_id": ObjectId(app["job_id"])})
        app["job_title"] = job.get("title", "Untitled Job") if job else "Deleted Job"

    return render_template("admin_applications.html", applications=apps)

@app.route('/admin/applications/<app_id>/accept', methods=['POST'])
def accept_application(app_id):
    application = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
    job = mongo.db.jobs.find_one({'_id': application["job_id"]})
    job_title = job.get("title", "This job") if job else "This job"

    mongo.db.applications.update_one(
        {'_id': ObjectId(app_id)},
        {'$set': {
            'status': 'Accepted',
            'notification': f'Your application for "{job_title}" has been accepted!'
        }}
    )
    flash('Application accepted and user notified.')
    return redirect(url_for('admin_applications'))

@app.route('/admin/applications/<app_id>/reject', methods=['POST'])
def reject_application(app_id):
    application = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
    job = mongo.db.jobs.find_one({'_id': application["job_id"]})
    job_title = job.get("title", "This job") if job else "This job"

    mongo.db.applications.update_one(
        {'_id': ObjectId(app_id)},
        {'$set': {
            'status': 'Rejected',
            'notification': f'Sorry, your application for "{job_title}" was rejected.'
        }}
    )
    flash('Application rejected and user notified.')
    return redirect(url_for('admin_applications'))

@app.route('/admin/applications/<app_id>/pending', methods=['POST'])
def pending_application(app_id):
    application = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
    job = mongo.db.jobs.find_one({'_id': application["job_id"]})
    job_title = job.get("title", "This job") if job else "This job"

    mongo.db.applications.update_one(
        {'_id': ObjectId(app_id)},
        {'$set': {
            'status': 'Pending',
            'notification': f'Your application for "{job_title}" is under review.'
        }}
    )
    flash('Application marked as pending and user notified.')
    return redirect(url_for('admin_applications'))

@app.route("/admin/send-message", methods=["POST"])
def send_message():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    email = request.form.get("email")
    message = request.form.get("message")

    if not email or not message:
        flash("Missing data")
        return redirect(url_for("admin_users"))

    mongo.db.messages.insert_one({
        "email": email,
        "message": message,
        "date": datetime.utcnow()
    })

    flash(f"Message sent to {email}")
    return redirect(url_for("admin_users"))
@app.route("/admin/contact-messages")
def admin_contact_messages():
    if not session.get("admin"):
        flash("Admins only!", "danger")
        return redirect(url_for("admin_login"))

    messages = list(mongo.db.contact_messages.find().sort("timestamp", pymongo.DESCENDING))
    return render_template("admin_contact_message.html", messages=messages)
# Interview Prep Feature
def seed_interview_questions(force_reseed=False):
    sample_questions = [
        {"role": "Java Backend Developer", "type": "technical", "difficulty": "easy", "question": "What is the difference between List and Set in Java?"},
        {"role": "Java Backend Developer", "type": "technical", "difficulty": "medium", "question": "How would you optimize a Spring Boot application for performance?"},
        {"role": "Java Backend Developer", "type": "technical", "difficulty": "hard", "question": "Design a REST API for a banking system with transaction history."},
        {"role": "Java Backend Developer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a time you debugged a complex Java issue."},
        {"role": "Java Backend Developer", "type": "system_design", "difficulty": "hard", "question": "Design a scalable microservices architecture using Spring Boot."},
        {"role": "Node.js Backend Developer", "type": "technical", "difficulty": "easy", "question": "What is the event loop in Node.js?"},
        {"role": "Node.js Backend Developer", "type": "technical", "difficulty": "medium", "question": "How would you handle authentication in an Express.js app?"},
        {"role": "Node.js Backend Developer", "type": "technical", "difficulty": "hard", "question": "Implement a rate limiter for an API using Node.js."},
        {"role": "Node.js Backend Developer", "type": "behavioral", "difficulty": "medium", "question": "Describe a challenging Node.js project you worked on."},
        {"role": "Node.js Backend Developer", "type": "system_design", "difficulty": "hard", "question": "Design a real-time chat system with Node.js and WebSockets."},
        {"role": "Full Stack Developer (Java)", "type": "technical", "difficulty": "easy", "question": "What is the role of CSS in a web application?"},
        {"role": "Full Stack Developer (Java)", "type": "technical", "difficulty": "medium", "question": "How do you integrate React with a Spring Boot backend?"},
        {"role": "Full Stack Developer (Java)", "type": "technical", "difficulty": "hard", "question": "Build a full-stack e-commerce app with React and Java."},
        {"role": "Full Stack Developer (Java)", "type": "behavioral", "difficulty": "medium", "question": "Share a time you collaborated on a full-stack project."},
        {"role": "Full Stack Developer (Java)", "type": "system_design", "difficulty": "hard", "question": "Design a scalable full-stack solution for an online store."},
        {"role": "Full Stack Developer (JS)", "type": "technical", "difficulty": "easy", "question": "What is a callback function in JavaScript?"},
        {"role": "Full Stack Developer (JS)", "type": "technical", "difficulty": "medium", "question": "How do you secure a Node.js and React application?"},
        {"role": "Full Stack Developer (JS)", "type": "technical", "difficulty": "hard", "question": "Design a RESTful API with MongoDB and Express."},
        {"role": "Full Stack Developer (JS)", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a full-stack bug you fixed."},
        {"role": "Full Stack Developer (JS)", "type": "system_design", "difficulty": "hard", "question": "Plan a scalable JS full-stack app for a social platform."},
        {"role": "Frontend Developer", "type": "technical", "difficulty": "easy", "question": "What is the box model in CSS?"},
        {"role": "Frontend Developer", "type": "technical", "difficulty": "medium", "question": "How do you optimize a React application?"},
        {"role": "Frontend Developer", "type": "technical", "difficulty": "hard", "question": "Create a responsive design for a multi-device layout."},
        {"role": "Frontend Developer", "type": "behavioral", "difficulty": "medium", "question": "Describe a time you improved a website’s usability."},
        {"role": "Frontend Developer", "type": "system_design", "difficulty": "hard", "question": "Design a frontend for a high-traffic e-commerce site."},
        {"role": "Mobile Developer", "type": "technical", "difficulty": "easy", "question": "What is the difference between Flutter and React Native?"},
        {"role": "Mobile Developer", "type": "technical", "difficulty": "medium", "question": "How do you handle state management in Flutter?"},
        {"role": "Mobile Developer", "type": "technical", "difficulty": "hard", "question": "Design a mobile app for real-time location tracking."},
        {"role": "Mobile Developer", "type": "behavioral", "difficulty": "medium", "question": "Share a mobile app project you’re proud of."},
        {"role": "Mobile Developer", "type": "system_design", "difficulty": "hard", "question": "Plan a cross-platform mobile app architecture."},
        {"role": "Data Scientist", "type": "technical", "difficulty": "easy", "question": "What is a confusion matrix?"},
        {"role": "Data Scientist", "type": "technical", "difficulty": "medium", "question": "Explain the process of feature engineering."},
        {"role": "Data Scientist", "type": "technical", "difficulty": "hard", "question": "Build a predictive model using TensorFlow."},
        {"role": "Data Scientist", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a data project that impacted a business."},
        {"role": "Data Scientist", "type": "system_design", "difficulty": "hard", "question": "Design a data pipeline for a recommendation system."},
        {"role": "AI Engineer", "type": "technical", "difficulty": "easy", "question": "What is a neural network?"},
        {"role": "AI Engineer", "type": "technical", "difficulty": "medium", "question": "How do you prevent overfitting in a model?"},
        {"role": "AI Engineer", "type": "technical", "difficulty": "hard", "question": "Implement an NLP model for sentiment analysis."},
        {"role": "AI Engineer", "type": "behavioral", "difficulty": "medium", "question": "Describe an AI project you led."},
        {"role": "AI Engineer", "type": "system_design", "difficulty": "hard", "question": "Design an AI-powered chatbot system."},
        {"role": "Blockchain Developer", "type": "technical", "difficulty": "easy", "question": "What is a smart contract?"},
        {"role": "Blockchain Developer", "type": "technical", "difficulty": "medium", "question": "How does Ethereum’s consensus mechanism work?"},
        {"role": "Blockchain Developer", "type": "technical", "difficulty": "hard", "question": "Write a Solidity contract for a voting system."},
        {"role": "Blockchain Developer", "type": "behavioral", "difficulty": "medium", "question": "Share a blockchain project you worked on."},
        {"role": "Blockchain Developer", "type": "system_design", "difficulty": "hard", "question": "Design a decentralized finance (DeFi) platform."},
        {"role": "Cloud Engineer", "type": "technical", "difficulty": "easy", "question": "What is the difference between IaaS and PaaS?"},
        {"role": "Cloud Engineer", "type": "technical", "difficulty": "medium", "question": "How do you set up auto-scaling on AWS?"},
        {"role": "Cloud Engineer", "type": "technical", "difficulty": "hard", "question": "Design a multi-cloud strategy for disaster recovery."},
        {"role": "Cloud Engineer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a cloud migration you managed."},
        {"role": "Cloud Engineer", "type": "system_design", "difficulty": "hard", "question": "Plan a cloud architecture for a global app."},
        {"role": "DevOps Engineer", "type": "technical", "difficulty": "easy", "question": "What is CI/CD?"},
        {"role": "DevOps Engineer", "type": "technical", "difficulty": "medium", "question": "How do you configure a Kubernetes pod?"},
        {"role": "DevOps Engineer", "type": "technical", "difficulty": "hard", "question": "Design a CI/CD pipeline with GitHub Actions."},
        {"role": "DevOps Engineer", "type": "behavioral", "difficulty": "medium", "question": "Describe a time you improved deployment speed."},
        {"role": "DevOps Engineer", "type": "system_design", "difficulty": "hard", "question": "Plan a DevOps setup for a microservices app."},
        {"role": "UI/UX Designer", "type": "technical", "difficulty": "easy", "question": "What is the difference between UI and UX?"},
        {"role": "UI/UX Designer", "type": "technical", "difficulty": "medium", "question": "How do you conduct user research?"},
        {"role": "UI/UX Designer", "type": "technical", "difficulty": "hard", "question": "Design a wireframe for a mobile banking app."},
        {"role": "UI/UX Designer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a design project you led."},
        {"role": "UI/UX Designer", "type": "system_design", "difficulty": "hard", "question": "Create a design system for a large-scale app."},
        {"role": "Web Developer", "type": "technical", "difficulty": "easy", "question": "What does HTML5 offer over HTML4?"},
        {"role": "Web Developer", "type": "technical", "difficulty": "medium", "question": "How do you optimize a website for SEO?"},
        {"role": "Web Developer", "type": "technical", "difficulty": "hard", "question": "Build a responsive portfolio site with JavaScript."},
        {"role": "Web Developer", "type": "behavioral", "difficulty": "medium", "question": "Share a web project you completed under pressure."},
        {"role": "Web Developer", "type": "system_design", "difficulty": "hard", "question": "Design a scalable web app architecture."},
        {"role": "Backend Developer", "type": "technical", "difficulty": "easy", "question": "What is REST API?"},
        {"role": "Backend Developer", "type": "technical", "difficulty": "medium", "question": "How do you secure a backend API?"},
        {"role": "Backend Developer", "type": "technical", "difficulty": "hard", "question": "Design a backend for a social media platform."},
        {"role": "Backend Developer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a backend issue you resolved."},
        {"role": "Backend Developer", "type": "system_design", "difficulty": "hard", "question": "Plan a distributed backend system."},
        {"role": "Database Administrator", "type": "technical", "difficulty": "easy", "question": "What is a primary key?"},
        {"role": "Database Administrator", "type": "technical", "difficulty": "medium", "question": "How do you optimize a slow SQL query?"},
        {"role": "Database Administrator", "type": "technical", "difficulty": "hard", "question": "Design a database schema for an e-commerce site."},
        {"role": "Database Administrator", "type": "behavioral", "difficulty": "medium", "question": "Describe a database recovery you performed."},
        {"role": "Database Administrator", "type": "system_design", "difficulty": "hard", "question": "Plan a high-availability database system."},
        {"role": "Machine Learning Engineer", "type": "technical", "difficulty": "easy", "question": "What is gradient descent?"},
        {"role": "Machine Learning Engineer", "type": "technical", "difficulty": "medium", "question": "How do you evaluate a machine learning model?"},
        {"role": "Machine Learning Engineer", "type": "technical", "difficulty": "hard", "question": "Implement a custom loss function in PyTorch."},
        {"role": "Machine Learning Engineer", "type": "behavioral", "difficulty": "medium", "question": "Share a ML project you deployed."},
        {"role": "Machine Learning Engineer", "type": "system_design", "difficulty": "hard", "question": "Design an ML pipeline for real-time predictions."},
        {"role": "System Administrator", "type": "technical", "difficulty": "easy", "question": "What is a Linux file permission?"},
        {"role": "System Administrator", "type": "technical", "difficulty": "medium", "question": "How do you configure a firewall?"},
        {"role": "System Administrator", "type": "technical", "difficulty": "hard", "question": "Design a backup strategy for a server farm."},
        {"role": "System Administrator", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a system outage you handled."},
        {"role": "System Administrator", "type": "system_design", "difficulty": "hard", "question": "Plan a secure server infrastructure."},
        {"role": "Embedded Systems Engineer", "type": "technical", "difficulty": "easy", "question": "What is an interrupt in embedded systems?"},
        {"role": "Embedded Systems Engineer", "type": "technical", "difficulty": "medium", "question": "How do you debug a microcontroller?"},
        {"role": "Embedded Systems Engineer", "type": "technical", "difficulty": "hard", "question": "Design an IoT device with low power consumption."},
        {"role": "Embedded Systems Engineer", "type": "behavioral", "difficulty": "medium", "question": "Share an embedded project you completed."},
        {"role": "Embedded Systems Engineer", "type": "system_design", "difficulty": "hard", "question": "Plan an embedded system for a smart home."},
        {"role": "AR/VR Developer", "type": "technical", "difficulty": "easy", "question": "What is the difference between AR and VR?"},
        {"role": "AR/VR Developer", "type": "technical", "difficulty": "medium", "question": "How do you optimize a Unity project for VR?"},
        {"role": "AR/VR Developer", "type": "technical", "difficulty": "hard", "question": "Design an AR app for furniture placement."},
        {"role": "AR/VR Developer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about an AR/VR project you built."},
        {"role": "AR/VR Developer", "type": "system_design", "difficulty": "hard", "question": "Plan a multi-user VR collaboration platform."},
        {"role": "Cybersecurity Specialist", "type": "technical", "difficulty": "easy", "question": "What is a DDoS attack?"},
        {"role": "Cybersecurity Specialist", "type": "technical", "difficulty": "medium", "question": "How do you conduct a penetration test?"},
        {"role": "Cybersecurity Specialist", "type": "technical", "difficulty": "hard", "question": "Design a security protocol for a financial app."},
        {"role": "Cybersecurity Specialist", "type": "behavioral", "difficulty": "medium", "question": "Share a security breach you mitigated."},
        {"role": "Cybersecurity Specialist", "type": "system_design", "difficulty": "hard", "question": "Plan a cybersecurity framework for a company."},
        {"role": "Network Engineer", "type": "technical", "difficulty": "easy", "question": "What is the OSI model?"},
        {"role": "Network Engineer", "type": "technical", "difficulty": "medium", "question": "How do you troubleshoot a network outage?"},
        {"role": "Network Engineer", "type": "technical", "difficulty": "hard", "question": "Design a network for a multi-office company."},
        {"role": "Network Engineer", "type": "behavioral", "difficulty": "medium", "question": "Tell me about a network upgrade you managed."},
        {"role": "Network Engineer", "type": "system_design", "difficulty": "hard", "question": "Plan a secure, scalable network infrastructure."}
    ]
    try:
        question_count = mongo.db.questions.count_documents({})
        if force_reseed or question_count == 0:
            mongo.db.questions.delete_many({})  # Clear existing questions
            result = mongo.db.questions.insert_many(sample_questions)
            print(f"Seeded {len(result.inserted_ids)} interview questions successfully.")
        else:
            print(f"Database already contains {question_count} questions—skipping seed unless forced.")
    except pymongo.errors.PyMongoError as e:
        print(f"Failed to seed questions: {e}")

seed_interview_questions(force_reseed=True)  # Force reseed on startup

@app.route("/interview", methods=["GET"])
def interview():
    return render_template("interview.html")

@app.route("/api/interview/start", methods=["POST"])
def start_interview():
    role = request.json.get("role")
    difficulty = request.json.get("difficulty", "medium")
    if not role:
        return jsonify({"success": False, "message": "Oh honey, pick a role to get started!"}), 400

    try:
        print(f"Fetching questions for role: {role}, difficulty: {difficulty}")  # Debug log
        questions = list(mongo.db.questions.find({"role": role, "difficulty": difficulty}))
        if not questions:
            print(f"No exact match, falling back to all difficulties for {role}")  # Debug log
            questions = list(mongo.db.questions.find({"role": role}))
        if not questions:
            return jsonify({"success": False, "message": f"No questions for {role} yet—try another one, sweetie!"}), 404
        question = random.choice(questions)
        print(f"Selected question: {question['question']}")  # Debug log
        return jsonify({
            "success": True,
            "question": question["question"],
            "question_id": str(question["_id"]),
            "type": question["type"],
            "difficulty": question["difficulty"]
        })
    except pymongo.errors.PyMongoError as e:
        print(f"Database error: {e}")  # Debug log
        return jsonify({"success": False, "message": f"Yikes, a little glitch: {e}—let’s try again!"}), 500

@app.route("/api/interview/answer", methods=["POST"])
def submit_answer():
    role = request.json.get("role")
    answer = request.json.get("answer")
    question_id = request.json.get("question_id")
    if not role or not answer or not question_id:
        return jsonify({"success": False, "message": "Hey, give me a role, an answer, and a question ID, please!"}), 400

    try:
        question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
        if not question:
            return jsonify({"success": False, "message": "Oops, lost that question—let’s start fresh!"}), 404

        feedback = generate_interview_feedback(answer, question["question"], question["type"])

        questions = list(mongo.db.questions.find({
            "role": role,
            "type": question["type"],
            "difficulty": question["difficulty"],
            "_id": {"$ne": ObjectId(question_id)}
        }))
        if not questions:
            questions = list(mongo.db.questions.find({"role": role, "_id": {"$ne": ObjectId(question_id)}}))
        if questions:
            next_question = random.choice(questions)
            return jsonify({
                "success": True,
                "feedback": feedback,
                "next_question": next_question["question"],
                "next_question_id": str(next_question["_id"]),
                "type": next_question["type"],
                "difficulty": next_question["difficulty"]
            })
        return jsonify({
            "success": True,
            "feedback": feedback,
            "next_question": "Wow, you rocked all the questions! Ready for a new role, champ?",
            "next_question_id": "",
            "type": "",
            "difficulty": ""
        })
    except pymongo.errors.PyMongoError as e:
        return jsonify({"success": False, "message": f"Uh-oh, database trouble: {e}—give it another go!"}), 500

def generate_interview_feedback(answer, question, question_type):
    answer_length = len(answer.strip())
    # 25 conditions to catch all user quirks and encourage professionalism
    if not answer or answer_length == 0:
        return "Oh sweetie, you didn’t say anything! Give me a proper answer to wow them, please!"
    elif answer.lower() in ["idk", "i don't know", "no idea", "idk sto asking", "dunno", "beats me", "pass"]:
        return "Aw, don’t give up with ‘I don’t know’! Take a stab at it professionally, you’ve got this!"
    elif answer_length < 10:
        return "That’s super short, honey! Stretch it out with some details to show your stuff."
    elif answer_length < 20:
        return "Hmm, a bit brief—add more juice, like an example, to impress the interviewer!"
    elif all(c.isdigit() for c in answer):
        return "Numbers only? Nope, use words to flex your skills, darling!"
    elif answer.isupper():
        return "No shouting, sweetie! Keep it cool and pro—try a calm response."
    elif any(word in answer.lower() for word in ["lol", "haha", "rofl", "lmao", "hehe"]):
        return "Love the giggles, but let’s get serious—give a polished answer, okay?"
    elif any(word in answer.lower() for word in ["dude", "bro", "mate", "yo", "buddy", "pal"]):
        return "Let’s ditch the casual vibe—answer like you’re in the interview room, champ!"
    elif any(word in answer.lower() for word in ["maybe", "sort of", "kinda", "eh", "meh"]):
        return "No vagueness, honey! Be confident and clear—own that answer!"
    elif any(word in answer.lower() for word in ["whatever", "fine", "ok", "sure", "yep"]):
        return "‘Whatever’ won’t cut it! Give a thoughtful, detailed response, please!"
    elif any(word in answer.lower() for word in ["boring", "stupid", "dumb", "lame"]):
        return "Oh no, don’t call it boring! Show some enthusiasm and answer professionally!"
    elif question_type in ["technical", "system_design"] and not any(word in answer.lower() for word in ["how", "why", "process", "design", "implement", "build"]):
        return "Good try, but add ‘how’ or ‘why’ to show your tech chops—let’s make it shine!"
    elif question_type == "behavioral" and not any(word in answer.lower() for word in ["i", "we", "team", "project", "experience", "job"]):
        return "Nice start, but tell a personal story—use ‘I’ or ‘we’ to stand out!"
    elif answer_length > 250:
        return "Wow, you went big! Trim it down to the key points for a sleek, pro answer."
    elif any(word in answer.lower() for word in ["not sure", "dunno if", "think so"]):
        return "Avoid ‘not sure’—sound confident, even if you’re guessing, sweetie!"
    elif question_type == "technical" and not any(word in answer.lower() for word in ["code", "example", "algorithm", "syntax"]):
        return "Solid effort! Toss in a code snippet or example to boost your tech cred."
    elif question_type == "behavioral" and not any(word in answer.lower() for word in ["result", "outcome", "impact", "success"]):
        return "Great story! Add the result with STAR (Situation, Task, Action, Result)!"
    elif question_type == "system_design" and not any(word in answer.lower() for word in ["scale", "trade-off", "architecture", "performance"]):
        return "Nice plan! Talk about scalability or trade-offs to level up your design."
    elif any(char in "!@#$%^&*()" for char in answer):
        return "Whoa, no special characters, honey! Keep it clean and professional."
    elif answer.startswith(("uh", "um", "er")):
        return "Let’s skip the fillers—jump right into a strong, clear answer, okay?"
    elif any(word in answer.lower() for word in ["help", "save me", "no clue"]):
        return "Don’t worry, I’ve got your back! Try your best and give a solid response."
    elif answer.endswith(("?", ".", "!!")):
        return "End with confidence—avoid questions or extra punctuation, sweetie!"
    elif answer_length < 50 and question_type in ["system_design", "technical"]:
        return "That’s a bit light for a tech question! Add more depth, like steps or logic."
    elif any(word in answer.lower() for word in ["easy", "hard", "tough"]):
        return "Focus on the answer, not the difficulty—show your skills, champ!"
    elif question_type == "behavioral" and answer_length < 30:
        return "Short stories won’t impress—expand with details, like what you learned!"
    # New conditions for partially correct answers
    elif question_type == "technical" and any(word in answer.lower() for word in ["function", "variable", "loop"]) and answer_length < 100:
        return "You’re on the right track with terms like ‘function’ or ‘loop’! Expand with more details or an example to really shine."
    elif question_type == "technical" and any(word in answer.lower() for word in ["class", "object", "method"]) and not any(word in answer.lower() for word in ["inheritance", "polymorphism"]):
        return "Great start mentioning ‘class’ or ‘object’! Add concepts like inheritance to show deeper knowledge."
    elif question_type == "system_design" and any(word in answer.lower() for word in ["database", "server"]) and answer_length < 150:
        return "Nice mention of ‘database’ or ‘server’! Build on it with scalability or load balancing details."
    elif question_type == "behavioral" and any(word in answer.lower() for word in ["problem", "solved"]) and not any(word in answer.lower() for word in ["team", "result"]):
        return "You’ve got a good start with ‘problem’ and ‘solved’! Include your team’s role or the result for a stronger story."
    elif question_type == "technical" and any(word in answer.lower() for word in ["api", "endpoint"]) and not any(word in answer.lower() for word in ["rest", "http"]):
        return "You’re close with ‘API’ or ‘endpoint’! Add REST or HTTP details to level up your answer."
    elif question_type == "system_design" and any(word in answer.lower() for word in ["cache", "load"]) and answer_length < 200:
        return "Love seeing ‘cache’ or ‘load’! Expand with how you’d implement it for better performance."
    elif question_type == "behavioral" and any(word in answer.lower() for word in ["learned", "skill"]) and answer_length < 80:
        return "You’re on point with ‘learned’ or ‘skill’! Give more context on how you applied it."
    elif question_type == "technical" and any(word in answer.lower() for word in ["algorithm", "data"]) and not any(word in answer.lower() for word in ["time", "space"]):
        return "Good use of ‘algorithm’ or ‘data’! Include time or space complexity for a pro touch."
    elif question_type == "system_design" and any(word in answer.lower() for word in ["microservices", "api"]) and answer_length < 180:
        return "You’re getting there with ‘microservices’ or ‘API’! Add how they communicate or scale."
    elif question_type == "behavioral" and any(word in answer.lower() for word in ["challenge", "overcame"]) and not any(word in answer.lower() for word in ["strategy", "plan"]):
        return "Nice work with ‘challenge’ and ‘overcame’! Share your strategy to make it stand out."
    return "You’re killing it, honey! Maybe toss in a bit more context to really nail it."


# Add these routes to your app.py file (replace the existing ones)

# @app.route("/career-coach")
# def career_coach_page():
#     """Render the career coach page with embedded HTML"""
#     return '''<!DOCTYPE html>
# <html lang="en">
# <head>
#   <meta charset="UTF-8">
#   <title>Career Coach</title>
#   <style>
#     body {
#       font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#       margin: 0;
#       padding: 20px;
#       min-height: 100vh;
#     }
#     .container {
#       max-width: 800px;
#       margin: 0 auto;
#       background: white;
#       padding: 30px;
#       border-radius: 15px;
#       box-shadow: 0 10px 30px rgba(0,0,0,0.1);
#     }
#     h1 {
#       text-align: center;
#       color: #333;
#       margin-bottom: 30px;
#       font-size: 2.5em;
#     }
#     #question {
#       width: 100%;
#       height: 120px;
#       padding: 15px;
#       border: 2px solid #e1e5e9;
#       border-radius: 8px;
#       font-size: 16px;
#       resize: vertical;
#       box-sizing: border-box;
#     }
#     #question:focus {
#       outline: none;
#       border-color: #667eea;
#     }
#     button {
#       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#       color: white;
#       padding: 12px 30px;
#       border: none;
#       border-radius: 8px;
#       cursor: pointer;
#       font-size: 16px;
#       margin-top: 15px;
#       transition: transform 0.2s;
#     }
#     button:hover {
#       transform: translateY(-2px);
#     }
#     button:disabled {
#       background: #ccc;
#       cursor: not-allowed;
#       transform: none;
#     }
#     #response {
#       margin-top: 20px;
#       padding: 20px;
#       background-color: #f8f9fa;
#       border-radius: 8px;
#       border-left: 4px solid #667eea;
#       white-space: pre-wrap;
#       line-height: 1.6;
#       min-height: 50px;
#     }
#     .loading {
#       color: #667eea;
#       font-style: italic;
#     }
#     .error {
#       color: #dc3545;
#       background-color: #f8d7da;
#       border-left-color: #dc3545;
#     }
#   </style>
# </head>
# <body>
#   <div class="container">
#     <h1>🎯 AI Career Coach</h1>
#     <form id="careerForm">
#       <textarea id="question" placeholder="Ask me anything about your career! For example:
# • How do I prepare for a software engineering interview?
# • What skills should I learn for data science?
# • How can I transition to a tech career?
# • What should I include in my resume?" required></textarea>
#       <button type="submit" id="submitBtn">Get Career Advice</button>
#     </form>
#     <div id="response"></div>
#   </div>

#   <script>
#     document.getElementById("careerForm").addEventListener("submit", async (e) => {
#       e.preventDefault();
      
#       const question = document.getElementById("question").value.trim();
#       const submitBtn = document.getElementById("submitBtn");
#       const responseDiv = document.getElementById("response");
      
#       if (!question) {
#         responseDiv.innerHTML = "Please enter a question first!";
#         responseDiv.className = "error";
#         return;
#       }
      
#       // Show loading state
#       submitBtn.disabled = true;
#       submitBtn.textContent = "Getting advice...";
#       responseDiv.innerHTML = "🤔 Thinking about your question...";
#       responseDiv.className = "loading";

#       try {
#         const response = await fetch("/ask-career", {
#           method: "POST",
#           headers: {"Content-Type": "application/x-www-form-urlencoded"},
#           body: new URLSearchParams({question})
#         });

#         const data = await response.json();
        
#         if (data.error) {
#           responseDiv.innerHTML = "❌ " + data.error;
#           responseDiv.className = "error";
#         } else {
#           responseDiv.innerHTML = "💡 " + data.answer;
#           responseDiv.className = "";
#         }
#       } catch (error) {
#         responseDiv.innerHTML = "❌ Network error. Please check your connection and try again.";
#         responseDiv.className = "error";
#       } finally {
#         // Reset button
#         submitBtn.disabled = false;
#         submitBtn.textContent = "Get Career Advice";
#       }
#     });
#   </script>
# </body>
# </html>'''

# @app.route("/ask-career", methods=["POST"])
# def ask_career():
#     """Handle career coaching questions"""
#     try:
#         user_input = request.form.get("question")
        
#         if not user_input or not user_input.strip():
#             return jsonify({"error": "Please provide a question"}), 400
        
#         # Limit input length
#         if len(user_input) > 1000:
#             return jsonify({"error": "Question too long. Please keep it under 1000 characters."}), 400
        
#         # Get response from AI model
#         response = ask_career_bot(user_input.strip())
        
#         # Check if the response indicates an error
#         if response.startswith("Error:"):
#             return jsonify({"error": response}), 500
            
#         return jsonify({"answer": response})
        
#     except Exception as e:
#         return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

# if __name__ == "__main__":
#     app.run(debug=True)

@app.route("/career-coach")
def career_coach_page():
    """Render the career coach page"""
    return render_template("career_coach.html")

@app.route("/ask-career", methods=["POST"])
def ask_career():
    """Handle career coaching questions"""
    try:
        user_input = request.form.get("question") or request.json.get("question")

        if not user_input or not user_input.strip():
            return jsonify({"error": "Please provide a question"}), 400
        
        if len(user_input) > 1000:
            return jsonify({"error": "Question too long. Please keep it under 1000 characters."}), 400
        
        # Call your AI model
        response = ask_career_bot(user_input.strip())

        if response.startswith("Error:"):
            return jsonify({"error": response}), 500
            
        return jsonify({"answer": response})
        
    except Exception as e:
        print("ERROR in /ask-career:", str(e))  # helpful in terminal
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500


# @app.route("/resume-builder", methods=["GET", "POST"])
# def resume_builder():
#     """Resume builder feature"""
#     if request.method == "POST":
#         # Get form data
#         resume_data = {
#             "personal_info": {
#                 "full_name": request.form.get("full_name", ""),
#                 "email": request.form.get("email", ""),
#                 "phone": request.form.get("phone", ""),
#                 "address": request.form.get("address", ""),
#                 "linkedin": request.form.get("linkedin", ""),
#                 "website": request.form.get("website", "")
#             },
#             "professional_summary": request.form.get("professional_summary", ""),
#             "experience": [],
#             "education": [],
#             "skills": request.form.get("skills", "").split(",") if request.form.get("skills") else [],
#             "projects": [],
#             "certifications": request.form.get("certifications", "").split(",") if request.form.get("certifications") else []
#         }
        
#         # Process experience entries
#         exp_companies = request.form.getlist("exp_company")
#         exp_positions = request.form.getlist("exp_position")
#         exp_start_dates = request.form.getlist("exp_start_date")
#         exp_end_dates = request.form.getlist("exp_end_date")
#         exp_descriptions = request.form.getlist("exp_description")
        
#         for i in range(len(exp_companies)):
#             if exp_companies[i].strip():
#                 resume_data["experience"].append({
#                     "company": exp_companies[i],
#                     "position": exp_positions[i],
#                     "start_date": exp_start_dates[i],
#                     "end_date": exp_end_dates[i],
#                     "description": exp_descriptions[i]
#                 })
        
#         # Process education entries
#         edu_institutions = request.form.getlist("edu_institution")
#         edu_degrees = request.form.getlist("edu_degree")
#         edu_years = request.form.getlist("edu_year")
#         edu_gpas = request.form.getlist("edu_gpa")
        
#         for i in range(len(edu_institutions)):
#             if edu_institutions[i].strip():
#                 resume_data["education"].append({
#                     "institution": edu_institutions[i],
#                     "degree": edu_degrees[i],
#                     "year": edu_years[i],
#                     "gpa": edu_gpas[i]
#                 })
        
#         # Process project entries
#         proj_names = request.form.getlist("proj_name")
#         proj_descriptions = request.form.getlist("proj_description")
#         proj_technologies = request.form.getlist("proj_tech")
#         proj_links = request.form.getlist("proj_link")
        
#         for i in range(len(proj_names)):
#             if proj_names[i].strip():
#                 resume_data["projects"].append({
#                     "name": proj_names[i],
#                     "description": proj_descriptions[i],
#                     "technologies": proj_technologies[i],
#                     "link": proj_links[i]
#                 })
        
#         # Save to session for preview
#         session["resume_data"] = resume_data
        
#         # Generate resume content
#         action = request.form.get("action")
#         if action == "preview":
#             return render_template("resume_preview.html", resume_data=resume_data)
#         elif action == "download":
#             # For now, redirect to preview. You can add PDF generation later
#             return render_template("resume_preview.html", resume_data=resume_data, download_mode=True)
    
#     return render_template("resume_builder.html")

# @app.route("/resume-preview")
# def resume_preview():
#     """Show resume preview"""
#     resume_data = session.get("resume_data")
#     if not resume_data:
#         flash("No resume data found. Please build your resume first.", "warning")
#         return redirect(url_for("resume_builder"))
    
#     return render_template("resume_preview.html", resume_data=resume_data)

# @app.route("/download-resume")
# def download_resume():
#     """Download resume as HTML file"""
#     resume_data = session.get("resume_data")
#     if not resume_data:
#         flash("No resume data found. Please build your resume first.", "warning")
#         return redirect(url_for("resume_builder"))
    
#     # Generate HTML content
#     html_content = render_template("resume_download.html", resume_data=resume_data)
    
#     # Create filename
#     name = resume_data["personal_info"]["full_name"].replace(" ", "_") or "resume"
#     filename = f"{name}_resume.html"
    
#     # Save to uploads folder
#     filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#     with open(filepath, "w", encoding="utf-8") as f:
#         f.write(html_content)
    
#     return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    

# #new routes

# @app.route("/ai-resume-coach")
# def ai_resume_coach():
#     """Main AI Resume Coach interface"""
#     if "user_email" not in session:
#         return redirect(url_for("login"))
#     return render_template("ai_resume_coach.html")

# @app.route("/api/resume-coach/start", methods=["POST"])
# def start_resume_coaching():
#     """Initialize a new resume coaching session"""
#     if "user_email" not in session:
#         return jsonify({"error": "Login required"}), 401
    
#     # Initialize coaching session in MongoDB
#     user = mongo.db.users.find_one({"email": session["user_email"]})
    
#     coaching_session = {
#         "user_id": user["_id"],
#         "session_id": str(ObjectId()),
#         "created_at": datetime.utcnow(),
#         "current_step": "intro",
#         "collected_data": {},
#         "conversation_history": [],
#         "resume_drafts": []
#     }
    
#     result = mongo.db.coaching_sessions.insert_one(coaching_session)
#     session["coaching_session_id"] = str(result.inserted_id)
    
#     intro_message = generate_intro_message(user.get("fullname", "there"))
    
#     return jsonify({
#         "success": True,
#         "message": intro_message,
#         "session_id": str(result.inserted_id),
#         "step": "intro"
#     })

# @app.route("/api/resume-coach/chat", methods=["POST"])
# def resume_coach_chat():
#     """Handle conversational interactions with the AI resume coach"""
#     if "user_email" not in session:
#         return jsonify({"error": "Login required"}), 401
    
#     data = request.json
#     user_message = data.get("message", "").strip()
#     session_id = data.get("session_id") or session.get("coaching_session_id")
    
#     if not user_message:
#         return jsonify({"error": "Please provide a message"}), 400
    
#     if not session_id:
#         return jsonify({"error": "No active coaching session"}), 400
    
#     try:
#         # Get current coaching session
#         coaching_session = mongo.db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
#         if not coaching_session:
#             return jsonify({"error": "Coaching session not found"}), 404
        
#         # Add user message to conversation history
#         coaching_session["conversation_history"].append({
#             "role": "user",
#             "message": user_message,
#             "timestamp": datetime.utcnow()
#         })
        
#         # Process the message and generate AI response
#         ai_response = process_coaching_conversation(
#             user_message, 
#             coaching_session["current_step"],
#             coaching_session["collected_data"],
#             coaching_session["conversation_history"]
#         )
        
#         # Update coaching session
#         coaching_session["conversation_history"].append({
#             "role": "assistant", 
#             "message": ai_response["message"],
#             "timestamp": datetime.utcnow()
#         })
        
#         # Update collected data and current step
#         if "data_update" in ai_response:
#             coaching_session["collected_data"].update(ai_response["data_update"])
        
#         if "next_step" in ai_response:
#             coaching_session["current_step"] = ai_response["next_step"]
        
#         # Save updated session
#         mongo.db.coaching_sessions.update_one(
#             {"_id": ObjectId(session_id)},
#             {"$set": coaching_session}
#         )
        
#         return jsonify({
#             "success": True,
#             "message": ai_response["message"],
#             "step": coaching_session["current_step"],
#             "progress": ai_response.get("progress", 0),
#             "suggestions": ai_response.get("suggestions", []),
#             "can_generate_resume": ai_response.get("can_generate_resume", False)
#         })
        
#     except Exception as e:
#         return jsonify({"error": f"Processing error: {str(e)}"}), 500

# @app.route("/api/resume-coach/generate", methods=["POST"])
# def generate_ai_resume():
#     """Generate a complete resume based on collected data"""
#     if "user_email" not in session:
#         return jsonify({"error": "Login required"}), 401
    
#     session_id = session.get("coaching_session_id")
#     if not session_id:
#         return jsonify({"error": "No active coaching session"}), 400
    
#     try:
#         coaching_session = mongo.db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
#         if not coaching_session:
#             return jsonify({"error": "Coaching session not found"}), 404
        
#         # Generate resume using collected data
#         resume_content = generate_complete_resume(
#             coaching_session["collected_data"],
#             request.json.get("target_role", ""),
#             request.json.get("industry", "")
#         )
        
#         # Save generated resume
#         resume_draft = {
#             "generated_at": datetime.utcnow(),
#             "target_role": request.json.get("target_role", ""),
#             "industry": request.json.get("industry", ""),
#             "content": resume_content
#         }
        
#         coaching_session["resume_drafts"].append(resume_draft)
        
#         mongo.db.coaching_sessions.update_one(
#             {"_id": ObjectId(session_id)},
#             {"$set": {"resume_drafts": coaching_session["resume_drafts"]}}
#         )
        
#         return jsonify({
#             "success": True,
#             "resume_html": resume_content["html"],
#             "resume_text": resume_content["text"],
#             "suggestions": resume_content.get("suggestions", [])
#         })
        
#     except Exception as e:
#         return jsonify({"error": f"Generation error: {str(e)}"}), 500

# @app.route("/api/resume-coach/optimize", methods=["POST"])
# def optimize_resume_for_role():
#     """Optimize existing resume for a specific job/role"""
#     if "user_email" not in session:
#         return jsonify({"error": "Login required"}), 401
    
#     data = request.json
#     target_role = data.get("target_role", "")
#     job_description = data.get("job_description", "")
#     current_resume = data.get("current_resume", "")
    
#     if not target_role and not job_description:
#         return jsonify({"error": "Please provide target role or job description"}), 400
    
#     try:
#         optimization = optimize_resume_content(current_resume, target_role, job_description)
        
#         return jsonify({
#             "success": True,
#             "optimized_content": optimization["content"],
#             "changes_made": optimization["changes"],
#             "suggestions": optimization["suggestions"],
#             "keyword_matches": optimization.get("keyword_matches", [])
#         })
        
#     except Exception as e:
#         return jsonify({"error": f"Optimization error: {str(e)}"}), 500

# # AI Processing Functions (add these to a separate file like ai_resume_coach.py)

# def generate_intro_message(user_name):
#     """Generate personalized intro message"""
#     return f"""Hi {user_name}! I'm your AI Resume Coach, and I'm here to help you create a standout resume that gets interviews.

# Instead of just filling out a boring form, we're going to have a conversation where I learn about your unique experiences, skills, and career goals. Then I'll craft a personalized resume that tells your story effectively.

# Let's start with this: What type of role are you targeting, or what's your dream job? For example:
# • "Software Engineer at a tech startup"
# • "Marketing Manager in healthcare" 
# • "Data Scientist transitioning from academia"

# Tell me about your career goals!"""

# def process_coaching_conversation(user_message, current_step, collected_data, conversation_history):
#     """Process user input and generate appropriate AI responses"""
    
#     # Analyze user message for key information
#     extracted_info = extract_information_from_message(user_message, current_step)
    
#     if current_step == "intro":
#         return handle_intro_step(user_message, extracted_info)
#     elif current_step == "role_clarification":
#         return handle_role_step(user_message, extracted_info, collected_data)
#     elif current_step == "experience_gathering":
#         return handle_experience_step(user_message, extracted_info, collected_data)
#     elif current_step == "skills_assessment":
#         return handle_skills_step(user_message, extracted_info, collected_data)
#     elif current_step == "achievements_exploration":
#         return handle_achievements_step(user_message, extracted_info, collected_data)
#     elif current_step == "education_details":
#         return handle_education_step(user_message, extracted_info, collected_data)
#     elif current_step == "final_review":
#         return handle_final_review_step(user_message, extracted_info, collected_data)
#     else:
#         return {
#             "message": "I'm here to help! What would you like to work on next?",
#             "next_step": current_step
#         }

# def extract_information_from_message(message, current_step):
#     """Extract structured information from user's natural language input"""
#     # This would use NLP techniques or AI models to parse the message
#     # For now, using simple keyword matching and patterns
    
#     extracted = {
#         "job_titles": [],
#         "companies": [],
#         "skills": [],
#         "years_experience": None,
#         "education": {},
#         "achievements": []
#     }
    
#     # Simple pattern matching (you'd want to use more sophisticated NLP here)
#     import re
    
#     # Extract years of experience
#     years_match = re.search(r'(\d+)\s*(?:years?|yrs?)', message.lower())
#     if years_match:
#         extracted["years_experience"] = int(years_match.group(1))
    
#     # Extract common job titles
#     job_keywords = ['developer', 'engineer', 'analyst', 'manager', 'designer', 'architect', 'consultant']
#     for keyword in job_keywords:
#         if keyword in message.lower():
#             extracted["job_titles"].append(keyword)
    
#     # Extract skills (look for programming languages, tools)
#     skill_keywords = ['python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker', 'git']
#     for skill in skill_keywords:
#         if skill in message.lower():
#             extracted["skills"].append(skill)
    
#     return extracted

# def handle_intro_step(user_message, extracted_info):
#     """Handle the introduction step"""
#     response = f"""Perfect! I can see you're interested in roles involving {', '.join(extracted_info['job_titles']) if extracted_info['job_titles'] else 'your target field'}.

# Now I need to understand your background better. Let's talk about your work experience:

# • How many years of professional experience do you have?
# • What's your most recent or current job title and company?
# • What are 2-3 key responsibilities or achievements you're proud of?

# Don't worry about perfect formatting - just tell me about your experience naturally!"""
    
#     data_update = {
#         "target_roles": extracted_info["job_titles"],
#         "raw_intro": user_message
#     }
    
#     return {
#         "message": response,
#         "next_step": "experience_gathering",
#         "data_update": data_update,
#         "progress": 10
#     }

# def handle_experience_step(user_message, extracted_info, collected_data):
#     """Handle experience gathering"""
#     # Store experience information
#     if "experience" not in collected_data:
#         collected_data["experience"] = []
    
#     collected_data["experience"].append({
#         "raw_text": user_message,
#         "extracted_info": extracted_info,
#         "timestamp": datetime.utcnow().isoformat()
#     })
    
#     response = """Great information! I can already see some valuable experience there.

# Now let's dive into your skills. Instead of just listing them, tell me:

# • What technical skills do you use daily in your work?
# • What tools, software, or programming languages are you strongest with?
# • Any certifications or specialized training you have?
# • What would colleagues say you're exceptionally good at?

# Think beyond just technical skills - include soft skills, leadership abilities, or domain expertise!"""

#     return {
#         "message": response,
#         "next_step": "skills_assessment", 
#         "data_update": {"experience_raw": user_message},
#         "progress": 35,
#         "suggestions": generate_experience_suggestions(extracted_info)
#     }

# def handle_skills_step(user_message, extracted_info, collected_data):
#     """Handle skills assessment"""
#     response = """Excellent! Those skills will definitely make you stand out.

# Let's talk about your achievements and impact. This is where most people struggle, but it's crucial:

# • Tell me about a project or accomplishment you're really proud of
# • Any numbers/metrics that show your impact? (increased efficiency, saved costs, etc.)
# • Recognition, awards, or positive feedback you've received?
# • Problems you've solved or improvements you've made?

# Remember: Employers love seeing concrete results, not just responsibilities!"""

#     return {
#         "message": response,
#         "next_step": "achievements_exploration",
#         "data_update": {"skills_raw": user_message, "extracted_skills": extracted_info["skills"]},
#         "progress": 60,
#         "suggestions": generate_skills_suggestions(extracted_info["skills"])
#     }

# def handle_achievements_step(user_message, extracted_info, collected_data):
#     """Handle achievements exploration"""
#     response = """Those achievements are impressive! I can already see how they'll strengthen your resume.

# Let's cover your educational background:

# • What's your highest degree and field of study?
# • University/institution name and graduation year?
# • Any relevant coursework, academic projects, or honors?
# • Additional certifications, bootcamps, or online courses?

# Don't undersell yourself - include anything that demonstrates continuous learning!"""

#     return {
#         "message": response,
#         "next_step": "education_details",
#         "data_update": {"achievements_raw": user_message},
#         "progress": 80
#     }

# def handle_education_step(user_message, extracted_info, collected_data):
#     """Handle education details"""
#     response = f"""Perfect! I now have a comprehensive picture of your background.

# Let me summarize what we've gathered:
# • Target Role: {', '.join(collected_data.get('target_roles', ['Professional role']))}
# • Experience: {len(collected_data.get('experience', []))} work experiences shared
# • Skills: {len(extracted_info.get('skills', []))} technical skills identified
# • Education: {user_message[:100]}...

# Would you like me to:
# 1. Generate your complete resume now
# 2. Ask a few more targeted questions to strengthen specific sections
# 3. Focus on optimizing for a particular job posting

# What sounds best to you?"""

#     return {
#         "message": response,
#         "next_step": "final_review",
#         "data_update": {"education_raw": user_message},
#         "progress": 95,
#         "can_generate_resume": True
#     }

# def generate_complete_resume(collected_data, target_role="", industry=""):
#     """Generate a complete resume from collected conversational data"""
    
#     # Parse collected data into structured resume sections
#     resume_sections = parse_conversational_data(collected_data)
    
#     # Generate AI-enhanced content for each section
#     enhanced_resume = {
#         "personal_info": enhance_personal_info(resume_sections.get("personal_info", {})),
#         "professional_summary": generate_professional_summary(resume_sections, target_role, industry),
#         "experience": enhance_experience_section(resume_sections.get("experience", []), target_role),
#         "skills": enhance_skills_section(resume_sections.get("skills", []), target_role),
#         "education": enhance_education_section(resume_sections.get("education", [])),
#         "achievements": extract_and_format_achievements(resume_sections.get("achievements", []))
#     }
    
#     # Generate HTML and text versions
#     html_content = generate_resume_html(enhanced_resume)
#     text_content = generate_resume_text(enhanced_resume)
    
#     return {
#         "html": html_content,
#         "text": text_content,
#         "structured_data": enhanced_resume,
#         "suggestions": generate_resume_suggestions(enhanced_resume, target_role)
#     }

# def optimize_resume_content(current_resume, target_role, job_description):
#     """Optimize resume for specific role/job posting"""
    
#     # Analyze job requirements
#     job_keywords = extract_job_keywords(job_description)
#     required_skills = extract_required_skills(job_description)
    
#     # Analyze current resume
#     current_keywords = extract_resume_keywords(current_resume)
    
#     # Generate optimization suggestions
#     optimizations = {
#         "keyword_optimization": suggest_keyword_improvements(current_keywords, job_keywords),
#         "content_rewriting": suggest_content_rewrites(current_resume, target_role),
#         "section_prioritization": suggest_section_order(current_resume, job_description),
#         "skill_highlighting": suggest_skill_emphasis(current_resume, required_skills)
#     }
    
#     # Apply optimizations
#     optimized_content = apply_optimizations(current_resume, optimizations)
    
#     return {
#         "content": optimized_content,
#         "changes": optimizations,
#         "suggestions": [
#             "Tailored content for target role",
#             f"Added {len(job_keywords)} relevant keywords",
#             "Emphasized matching skills and experience",
#             "Improved action verbs and impact statements"
#         ],
#         "keyword_matches": calculate_keyword_overlap(current_keywords, job_keywords)
#     }

# # Helper functions for AI processing

# def generate_professional_summary(resume_sections, target_role, industry):
#     """Generate AI-powered professional summary"""
#     experience_years = estimate_years_from_text(resume_sections.get("experience", []))
#     key_skills = resume_sections.get("skills", [])[:5]  # Top 5 skills
    
#     summary_template = f"""Results-driven {target_role or 'professional'} with {experience_years}+ years of experience in {industry or 'technology'}. 
# Proven expertise in {', '.join(key_skills[:3]) if key_skills else 'relevant technologies'} with a track record of delivering impactful solutions. 
# Strong problem-solving abilities combined with {', '.join(key_skills[3:5]) if len(key_skills) > 3 else 'collaborative leadership'} skills."""
    
#     return enhance_with_ai_suggestions(summary_template, "professional_summary")

# def enhance_experience_section(experience_data, target_role):
#     """Enhance experience descriptions with AI"""
#     enhanced_experiences = []
    
#     for exp in experience_data:
#         enhanced_exp = {
#             "company": extract_company_name(exp.get("raw_text", "")),
#             "position": extract_position_title(exp.get("raw_text", "")),
#             "duration": extract_duration(exp.get("raw_text", "")),
#             "achievements": enhance_achievement_bullets(exp.get("raw_text", ""), target_role)
#         }
#         enhanced_experiences.append(enhanced_exp)
    
#     return enhanced_experiences

# def enhance_achievement_bullets(raw_text, target_role):
#     """Convert raw experience text into polished achievement bullets"""
#     # This would use AI to rewrite experience descriptions
#     # For now, using rule-based enhancement
    
#     sentences = raw_text.split('.')
#     enhanced_bullets = []
    
#     action_verbs = ["Developed", "Implemented", "Led", "Optimized", "Designed", "Created", "Managed", "Improved"]
    
#     for sentence in sentences[:4]:  # Max 4 bullets per role
#         if len(sentence.strip()) > 10:
#             enhanced = enhance_sentence_with_action_verb(sentence.strip(), action_verbs)
#             enhanced_bullets.append(enhanced)
    
#     return enhanced_bullets

# def parse_conversational_data(collected_data):
#     """Parse natural language responses into structured resume data"""
#     # This would use NLP to extract structured information
#     # For demonstration, using simple parsing
    
#     parsed = {
#         "personal_info": {},
#         "experience": collected_data.get("experience", []),
#         "skills": [],
#         "education": [],
#         "achievements": []
#     }
    
#     # Parse skills from raw text
#     if "skills_raw" in collected_data:
#         parsed["skills"] = extract_skills_from_text(collected_data["skills_raw"])
    
#     # Parse achievements
#     if "achievements_raw" in collected_data:
#         parsed["achievements"] = extract_achievements_from_text(collected_data["achievements_raw"])
    
#     return parsed

# # Integration with existing model.py functions

# def generate_interview_feedback(answer, question, question_type):
#     """Enhanced interview feedback using AI coaching principles"""
    
#     # Your existing feedback logic here, but enhanced
#     answer_length = len(answer.strip())
    
#     if answer_length < 20:
#         return "That's quite brief! In a real interview, aim for 1-2 minutes of detailed explanation. Try expanding with specific examples or step-by-step reasoning."
    
#     # Use AI to generate more sophisticated feedback
#     return generate_ai_interview_feedback(answer, question, question_type)

# def generate_ai_interview_feedback(answer, question, question_type):
#     """Generate AI-powered interview feedback"""
    
#     feedback_prompt = f"""
#     Question Type: {question_type}
#     Question: {question}
#     Candidate Answer: {answer}
    
#     Provide constructive interview feedback focusing on:
#     1. Content accuracy and completeness
#     2. Communication clarity
#     3. Professional presentation
#     4. Specific improvement suggestions
#     """
    
#     # This would call your AI model (OpenAI, local model, etc.)
#     # For now, return enhanced rule-based feedback
    
#     if question_type == "technical":
#         return generate_technical_feedback(answer, question)
#     elif question_type == "behavioral":
#         return generate_behavioral_feedback(answer, question)
#     elif question_type == "system_design":
#         return generate_system_design_feedback(answer, question)
    
#     return "Good effort! Consider adding more specific examples and details to strengthen your response."

# # Utility functions

# def extract_skills_from_text(text):
#     """Extract skills from natural language description"""
#     # Simple implementation - you'd want more sophisticated NLP here
#     common_skills = [
#         'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker', 
#         'kubernetes', 'git', 'agile', 'scrum', 'leadership', 'project management'
#     ]
    
#     found_skills = []
#     text_lower = text.lower()
    
#     for skill in common_skills:
#         if skill in text_lower:
#             found_skills.append(skill.title())
    
#     return found_skills

# def enhance_with_ai_suggestions(content, section_type):
#     """Enhance content with AI suggestions"""
#     # This would integrate with your existing AI models
#     # Return enhanced version of the content
#     return content

# def estimate_years_from_text(experience_data):
#     """Estimate total years of experience from text descriptions"""
#     # Simple estimation logic
#     return max(3, len(experience_data))  # Default minimum 3 years

# # Add these routes for the new AI coach interface    
# if __name__ == "__main__":
#     app.run(debug=True)


resume_coach = ResumeCoach()

# Replace /resume-builder with redirect to /ai-resume-coach
@app.route("/resume-builder", methods=["GET", "POST"])
def resume_builder():
    """Redirect to AI Resume Coach"""
    return redirect(url_for("ai_resume_coach"))

@app.route("/ai-resume-coach")
def ai_resume_coach():
    """Main AI Resume Coach interface"""
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("ai_resume_coach.html")

@app.route("/api/resume-coach/start", methods=["POST"])
def start_resume_coaching():
    """Initialize a new resume coaching session"""
    try:
        if "user_email" not in session:
            return jsonify({"error": "Login required"}), 401
        
        user = mongo.db.users.find_one({"email": session["user_email"]})
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        coaching_session = {
            "user_id": user["_id"],
            "session_id": str(ObjectId()),
            "created_at": datetime.utcnow(),
            "current_step": "intro",
            "collected_data": {},
            "conversation_history": [],
            "resume_drafts": []
        }
        
        result = mongo.db.coaching_sessions.insert_one(coaching_session)
        session["coaching_session_id"] = str(result.inserted_id)
        
        intro_message = f"""Hi {user.get('fullname', 'there')}! I'm your AI Resume Coach, here to craft a standout resume.
Tell me: **What type of role are you targeting?** (e.g., Software Engineer, Marketing Manager)"""
        
        return jsonify({
            "success": True,
            "message": intro_message,
            "session_id": str(result.inserted_id),
            "step": "intro"
        })
    except Exception as e:
        return jsonify({"error": f"Session initialization error: {str(e)}"}), 500

@app.route("/api/resume-coach/chat", methods=["POST"])
def resume_coach_chat():
    """Handle conversational interactions"""
    try:
        if "user_email" not in session:
            return jsonify({"error": "Login required"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        user_message = data.get("message", "").strip()
        session_id = data.get("session_id") or session.get("coaching_session_id")
        
        if not user_message:
            return jsonify({"error": "Please provide a message"}), 400
        
        if not session_id:
            return jsonify({"error": "No active coaching session"}), 400
        
        # Validate ObjectId format
        try:
            coaching_session = mongo.db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
        except Exception as e:
            return jsonify({"error": "Invalid session ID format"}), 400
            
        if not coaching_session:
            return jsonify({"error": "Coaching session not found"}), 404
        
        # Ensure conversation_history exists
        if "conversation_history" not in coaching_session:
            coaching_session["conversation_history"] = []
        if "collected_data" not in coaching_session:
            coaching_session["collected_data"] = {}
        
        coaching_session["conversation_history"].append({
            "role": "user",
            "message": user_message,
            "timestamp": datetime.utcnow()
        })
        
        ai_response = resume_coach.process_conversation(
            user_message, 
            coaching_session.get("current_step", "intro"),
            coaching_session["collected_data"],
            coaching_session["conversation_history"]
        )
        
        coaching_session["conversation_history"].append({
            "role": "assistant", 
            "message": ai_response.get("message", "I'm processing your request..."),
            "timestamp": datetime.utcnow()
        })
        
        # Update collected data if provided
        if "data_update" in ai_response:
            coaching_session["collected_data"].update(ai_response["data_update"])
        
        # Update step if provided
        if "next_step" in ai_response:
            coaching_session["current_step"] = ai_response["next_step"]
        
        # Update the session in database
        mongo.db.coaching_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {
                "conversation_history": coaching_session["conversation_history"],
                "collected_data": coaching_session["collected_data"],
                "current_step": coaching_session.get("current_step", "intro"),
                "updated_at": datetime.utcnow()
            }}
        )
        
        return jsonify({
            "success": True,
            "message": ai_response.get("message", "Response generated"),
            "step": coaching_session.get("current_step", "intro"),
            "progress": ai_response.get("progress", 0),
            "suggestions": ai_response.get("suggestions", []),
            "can_generate_resume": ai_response.get("can_generate_resume", False)
        })
        
    except Exception as e:
        return jsonify({"error": f"Chat processing error: {str(e)}"}), 500

@app.route("/api/resume-coach/generate", methods=["POST"])
def generate_ai_resume():
    """Generate a complete resume"""
    try:
        if "user_email" not in session:
            return jsonify({"error": "Login required"}), 401
        
        session_id = session.get("coaching_session_id")
        if not session_id:
            return jsonify({"error": "No active coaching session"}), 400
        
        try:
            coaching_session = mongo.db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
        except Exception as e:
            return jsonify({"error": "Invalid session ID format"}), 400
            
        if not coaching_session:
            return jsonify({"error": "Coaching session not found"}), 404
        
        # Get request data safely
        request_data = request.get_json() or {}
        target_role = request_data.get("target_role", "")
        industry = request_data.get("industry", "")
        
        # Ensure collected_data exists
        collected_data = coaching_session.get("collected_data", {})
        if not collected_data:
            return jsonify({"error": "No data collected yet. Complete the coaching conversation first."}), 400
        
        # If target_role not provided, try to get from collected data
        if not target_role:
            target_roles = collected_data.get("target_roles", [])
            target_role = target_roles[0] if target_roles else ""
        
        resume_content = resume_coach.generate_complete_resume(
            collected_data,
            target_role,
            industry
        )
        
        resume_draft = {
            "generated_at": datetime.utcnow(),
            "target_role": target_role,
            "industry": industry,
            "content": resume_content
        }
        
        # Ensure resume_drafts exists
        if "resume_drafts" not in coaching_session:
            coaching_session["resume_drafts"] = []
        
        coaching_session["resume_drafts"].append(resume_draft)
        
        mongo.db.coaching_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"resume_drafts": coaching_session["resume_drafts"]}}
        )
        
        return jsonify({
            "success": True,
            "resume_html": resume_content.get("html", ""),
            "resume_text": resume_content.get("text", ""),
            "suggestions": resume_content.get("suggestions", []),
            "structured_data": resume_content.get("structured_data", {})
        })
        
    except Exception as e:
        return jsonify({"error": f"Resume generation error: {str(e)}"}), 500

@app.route("/api/resume-coach/optimize", methods=["POST"])
def optimize_resume_for_role():
    """Optimize existing resume for a specific job/role"""
    try:
        if "user_email" not in session:
            return jsonify({"error": "Login required"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        target_role = data.get("target_role", "")
        job_description = data.get("job_description", "")
        current_resume = data.get("current_resume", "")
        
        if not target_role and not job_description:
            return jsonify({"error": "Please provide target role or job description"}), 400
        
        if not current_resume:
            return jsonify({"error": "Please provide current resume content"}), 400
        
        optimization = resume_coach.optimize_resume_content(current_resume, target_role, job_description)
        
        return jsonify({
            "success": True,
            "optimized_content": optimization.get("content", ""),
            "changes_made": optimization.get("changes", {}),
            "suggestions": optimization.get("suggestions", []),
            "keyword_matches": optimization.get("keyword_matches", [])
        })
        
    except Exception as e:
        return jsonify({"error": f"Optimization error: {str(e)}"}), 500

@app.route("/download-ai-resume", methods=["GET"])
def download_ai_resume():
    """Download generated resume as HTML"""
    try:
        if "user_email" not in session:
            flash("Login required to download resume.", "warning")
            return redirect(url_for("login"))
        
        session_id = session.get("coaching_session_id")
        if not session_id:
            flash("No active coaching session found.", "warning")
            return redirect(url_for("ai_resume_coach"))
        
        try:
            coaching_session = mongo.db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
        except Exception as e:
            flash("Invalid session ID.", "error")
            return redirect(url_for("ai_resume_coach"))
            
        if not coaching_session or not coaching_session.get("resume_drafts"):
            flash("No resume generated yet. Complete the coaching session first.", "warning")
            return redirect(url_for("ai_resume_coach"))
        
        latest_draft = coaching_session["resume_drafts"][-1]["content"]
        html_content = latest_draft.get("html", "")
        
        if not html_content:
            flash("Resume content not available.", "error")
            return redirect(url_for("ai_resume_coach"))
        
        filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Ensure upload folder exists
        upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return send_from_directory(upload_folder, filename, as_attachment=True)
        
    except Exception as e:
        flash(f"Download error: {str(e)}", "error")
        return redirect(url_for("ai_resume_coach"))

# Additional utility endpoint to get session status
@app.route("/api/resume-coach/status", methods=["GET"])
def get_coaching_status():
    """Get current coaching session status"""
    try:
        if "user_email" not in session:
            return jsonify({"error": "Login required"}), 401
        
        session_id = session.get("coaching_session_id")
        if not session_id:
            return jsonify({"active_session": False})
        
        try:
            coaching_session = mongo.db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
        except Exception as e:
            return jsonify({"active_session": False, "error": "Invalid session ID"})
            
        if not coaching_session:
            return jsonify({"active_session": False})
        
        return jsonify({
            "active_session": True,
            "current_step": coaching_session.get("current_step", "intro"),
            "progress": len(coaching_session.get("conversation_history", [])) * 10,
            "has_resume": len(coaching_session.get("resume_drafts", [])) > 0,
            "collected_data_keys": list(coaching_session.get("collected_data", {}).keys())
        })
        
    except Exception as e:
        return jsonify({"error": f"Status check error: {str(e)}"}), 500

# ... (keep all other existing routes from your app.py)

if __name__ == "__main__":
    app.run(debug=True)