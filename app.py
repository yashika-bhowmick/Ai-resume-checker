from flask import Flask,render_template, redirect, request, session
from db import Base, engine, SessionLocal
from models import User, Reports
from ai_new import analyze_resume
import models
import PyPDF2
import docx
import json
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env")
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


#create database tables
Base.metadata.create_all(bind=engine)

#HOME
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

#Signup
@app.route("/signup", methods=["GET","POST"])
def signup():
    db = SessionLocal()

    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password", "")

        existing_user = db.query(models.User).filter_by(email=email).first()
        if existing_user:
            return "This email already has an account. Please log in."
        
        user = models.User(email=email, password=password)
        db.add(user)
        db.commit()

        return redirect("/login")
    
    return render_template("/signup.html")

#LOGIN

@app.route("/login", methods = ["GET","POST"])
def login():
    db = SessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.query(models.User).filter_by(email=email, password=password).first()

        if user:
            session['user'] = user.email
            return redirect("/dashboard")
        else:
            return "Invalid Crendential"
        
    return render_template("login.html")

#DASHBOARD
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")
    
    result = None

    if request.method == "POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("resume")

        file = request.files.get("file")

        #file handling

        if file and file.name != "":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""

                    resume_text = text

                except Exception as e:
                    result = {"error": f"PDF error: {str(e)}"}


            elif file.filename.endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text + "\n"

                    resume_text = text

                except Exception as e:
                    result = {"error: " f"Docx error: {str(e)}"}

        if resume_text and user_goal:
            try:
                result = analyze_resume(resume_text, user_goal)   

                # save to db
                db = SessionLocal()
                user = db.query(models.User).filter_by(email=session["user"]).first()

                report = models.Reports(
                    user_id = user.id,
                    resume_text = resume_text,
                    result = json.dumps(result)

                )

                db.add(report)
                db.commit()

            except Exception as e:
                result = {"error": f"AI error: {str(e)}"}
        
    return render_template(
        "dashboard.html",
        user= session['user'],
        result = result

        )

# History
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()

    try:
        user = db.query(models.User).filter_by(
            email=session["user"]
        ).first()

        if not user:
            return redirect("/login")

        reports = (
            db.query(models.Reports)
            .filter_by(user_id=user.id)
            .order_by(models.Reports.id.desc())
            .all()
        )

        parsed_reports = []

        for report in reports:
            try:
                result_data = json.loads(report.result)
            except (json.JSONDecodeError, TypeError):
                result_data = {}

            parsed_reports.append({
                "resume": report.resume_text,
                "result": result_data
            })

        return render_template(
            "history.html",
            reports=parsed_reports
        )

    finally:
        db.close()


#logout

@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
