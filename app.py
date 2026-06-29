from flask import (
    Flask, 
    request, 
    redirect, 
    url_for, 
    render_template, 
    make_response, 
    jsonify, 
    flash
)
import tempfile
import zipfile
import shutil
import os
import json
import re
from pathlib import Path

from src.runSubmissions import RunSubimission
from src.support.getInfo import getProblems, getNameProblem, getName
from src.support.getDiference import diferenceOf, codesOf
from src.models import load_from_db, createUserInDb, addExerciceInDb
from src import models as mdl

app = mdl.app

with app.app_context():
    mdl.db.create_all()
    users = load_from_db()


def verify_login():
    username = request.cookies.get("username")
    password = request.cookies.get("password")
    
    if not username or not password:
        return False
    if username not in users or users[username]["password"] != password:
        return False
        
    return True


@app.route("/submit", methods=["POST", "GET"])
def submit():
    if not verify_login():
        return redirect(url_for("home"))
        
    data = request.get_json()
    code = data["code"]
    language = data["language"]
    problem = data["problem"]
    username = request.cookies.get("username")
    
    status = RunSubimission(code, language, problem, username)
    
    if status == 0:
        addExerciceInDb(username, problem)
        users[username]["finalized"].add(problem)
        return {"status": "ACCEPT", "color": "#00d062"}
        
    if status == 1:
        return {"status": "COMPILATION ERROR", "color": "#e79907"}

    if status in (2, 8):
        return {"status": "RUNTIME ERROR", "color": "#00d9e0"}
    
    if status == 3:
        return {"status": "TIMELIMIT", "color": "#004ec4"}
    
    if status in (4, 6):
        return {"status": "INTERNAL ERROR", "color": "#3B3B3B"}
    
    if status == 5:
        return {"status": "PARAMS ERROR", "color": "#3B3B3B"}
    
    if status == 7:
        return {"status": "MEMORY LIMIT", "color": "#8A751A"}

    if status == 9:
        user_output, expected_output = diferenceOf(username)
        return {
            "status": "WRONG ANSWER",
            "color": "#DA1D1D",
            "user_output": user_output,
            "expected_output": expected_output
        }
    
    if status == 10:
        user_output, expected_output = codesOf(username)
        return {
            "status": "PRESENTATION ERROR",
            "color": "#9BB602",
            "user_output": user_output,
            "expected_output": expected_output
        }    


@app.route("/seeDetails/<username>")
def see_details(username):
    if not verify_login():
        return redirect(url_for("home"))
        
    user_sub, exp_sub = codesOf(username)
    return render_template(
        "details.html",
        user_submission=user_sub,
        expected_submission=exp_sub,
    )


@app.route("/problem/<problem_id>")
def problem(problem_id):
    if not verify_login():
        return redirect(url_for("home"))
        
    username = request.cookies.get("username")
    is_completed = problem_id in users[username]["finalized"]
    
    return render_template(
        "problem.html",
        username=username,
        filePdf=f"{problem_id}.pdf",
        problemId=problem_id,
        name_problem=getNameProblem(problem_id),
        ended="COMPLETED" if is_completed else ""
    )


@app.route("/tests/<test>")
def tests(test):
    if not verify_login():
        return redirect(url_for("home"))
        
    problems = getProblems(test)
    username = request.cookies.get("username")
    formatted_problems = []
    
    for p_id in problems:
        is_done = p_id in users[username]["finalized"]
        formatted_problems.append({
            "id": p_id, 
            "title": getNameProblem(p_id), 
            "questoes": "✅" if is_done else "❌"
        })
        
    return render_template(
        "index.html", 
        case="Completed", 
        tests=formatted_problems, 
        page="problem"
    )


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    if username in users and users[username]["password"] == password:
        response = make_response(redirect(url_for('home')))
        response.set_cookie("username", username, max_age=60*120)  # 2 hours
        response.set_cookie("password", password, max_age=60*120)
        return response
        
    return render_template("login.html", msg="Incorrect username or password")


@app.route("/")
def home():
    tests_list = []
    names = getName()
    name_counts = {}
    
    for name in names:
        prefix = name[0:5]
        if prefix not in name_counts:
            name_counts[prefix] = 0
        name_counts[prefix] += 1
        
    for prefix in name_counts:
        phase_name = "Fase Local" if prefix[-1] == 'L' else "Fase Final"
        tests_list.append({
            "id": prefix,
            "title": f"INTERIF {prefix[0:4]} - {phase_name}",
            "questoes": name_counts[prefix]
        })
    
    username = request.cookies.get("username")
    password = request.cookies.get("password")
    
    if username and password and username in users:
        if users[username]["password"] == password:
            return render_template(
                "index.html", 
                case="Questions", 
                tests=tests_list, 
                page="tests"
            )

    return render_template("login.html", msg="")


@app.route("/createUser", methods=["POST"])
def create_user():
    new_user = request.form["username"]
    new_password = request.form["password"]
    
    if new_user in users:
        return render_template("createUser.html", msg="User already exists")
        
    if createUserInDb(new_user, new_password):
        users[new_user] = {
            "password": new_password,
            "finalized": set()
        }
        return redirect(url_for("home"))
        
    return "Error"


@app.route("/newUser")
def new_user():
    return render_template("createUser.html", msg="")


@app.route("/logout")
def logout():
    response = make_response(redirect(url_for('home')))
    response.set_cookie("username", "", expires=0)
    response.set_cookie("password", "", expires=0)
    return response


STATIC_FOLDER = Path("src/static")
PROBLEMS_FOLDER = Path("problems")
INFO_FILE = Path("src/support/info.txt")


def parse_problem_info(info_file):
    data = {}
    with open(info_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()
    return data


def parse_limits(path):
    path = Path(path)
    if path.is_dir():
        path = path / "c"

    if not path.exists():
        raise FileNotFoundError(f"Limits file not found: {path}")

    values = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("echo"):
                values.append(line.split()[1])

    if len(values) < 4:
        raise Exception("Invalid limits file.")

    return {
        "time": values[0],
        "number_of_repetitions": values[1],
        "memory_limit_MB": values[2],
        "output_limit_KB": values[3],
    }


def add_info(code, name):
    INFO_FILE.parent.mkdir(parents=True, exist_ok=True)

    existing_lines = set()
    if INFO_FILE.exists():
        with open(INFO_FILE, encoding="utf-8") as f:
            existing_lines = {x.strip() for x in f if x.strip()}

    line = f"{code} = {name}"
    if line not in existing_lines:
        with open(INFO_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def import_problem(problem_zip, year, phase, tmp_dir):
    match = re.match(r"([A-Z])-", problem_zip.stem)
    if not match:
        raise Exception("Invalid zip name.")

    letter = match.group(1)
    code = f"{year}{phase}{letter}"

    destination = PROBLEMS_FOLDER / code
    inputs_dest = destination / "inputs"
    outputs_dest = destination / "outputs"

    inputs_dest.mkdir(parents=True, exist_ok=True)
    outputs_dest.mkdir(parents=True, exist_ok=True)
    STATIC_FOLDER.mkdir(parents=True, exist_ok=True)

    work_dir = Path(tmp_dir) / code
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    with zipfile.ZipFile(problem_zip) as z:
        z.extractall(work_dir)

    if not (work_dir / "description").exists():
        subdirs = [d for d in work_dir.iterdir() if d.is_dir()]
        if len(subdirs) == 1:
            work_dir = subdirs[0]

    description_dir = work_dir / "description"
    if not description_dir.exists():
        raise Exception("'description' folder not found.")

    problem_info_file = description_dir / "problem.info"
    if not problem_info_file.exists():
        raise Exception("problem.info file not found.")

    info = parse_problem_info(problem_info_file)

    # ---------------- PDF ----------------
    if "descfile" not in info:
        raise Exception("Missing descfile field in problem.info.")

    pdf_file = description_dir / info["descfile"]
    if not pdf_file.exists():
        raise Exception(f"PDF '{info['descfile']}' not found.")

    shutil.copy2(pdf_file, STATIC_FOLDER / f"{code}.pdf")

    # ---------------- INPUT ----------------
    input_dir = work_dir / "input"
    if input_dir.exists():
        for file in sorted(input_dir.iterdir()):
            if file.is_file():
                shutil.copy2(file, inputs_dest / file.name)

    # ---------------- OUTPUT ----------------
    output_dir = work_dir / "output"
    if output_dir.exists():
        for file in sorted(output_dir.iterdir()):
            if file.is_file():
                shutil.copy2(file, outputs_dest / file.name)

    # ---------------- LIMITS ----------------
    limits_file = work_dir / "limits"
    if limits_file.is_dir():
        limits_file = limits_file / "c"

    if not limits_file.exists():
        raise Exception("limits/c file not found.")

    with open(destination / "limits.json", "w", encoding="utf-8") as f:
        json.dump(
            parse_limits(limits_file),
            f,
            indent=4,
            ensure_ascii=False
        )

    # ---------------- INFO ----------------
    if "fullname" not in info:
        raise Exception("Missing fullname field in problem.info.")

    add_info(code, info["fullname"])


@app.route("/import-problems", methods=["POST"])
def import_problems():
    #try hack me -------------
    if not (verify_login() and request.cookies.get("username") == "adm"):
        return jsonify({"error": "Unauthorized"}), 300
        
    if "file" not in request.files:
        return jsonify({"error": "Please upload a ZIP file."}), 400

    uploaded_file = request.files["file"]

    with tempfile.TemporaryDirectory() as tmp:
        main_zip = Path(tmp) / "main.zip"
        uploaded_file.save(main_zip)

        extracted_dir = Path(tmp) / "extracted"
        with zipfile.ZipFile(main_zip) as z:
            z.extractall(extracted_dir)

        subfolders = [p for p in extracted_dir.iterdir() if p.is_dir()]
        if len(subfolders) != 1:
            return jsonify({"error": "Expected a folder named 'Casos de teste - ANO'."}), 400

        root_folder = subfolders[0]
        print(root_folder)
        match = re.search(r"([A-Za-z0-9]{4})", root_folder.name)
        if not match:
            return jsonify({"error": "Invalid Format"}), 400

        year = match.group(1)
        phases = []
        
        if (root_folder / "Fase Final").exists():
            phases.append(("F", root_folder / "Fase Final"))
        if (root_folder / "Fase Local").exists():
            phases.append(("L", root_folder / "Fase Local"))
        if not phases:
            phases.append(("F", root_folder))

        for phase, path in phases:
            for problem_zip in path.glob("*.zip"):
                import_problem(problem_zip, year, phase, tmp)

    return jsonify({"status": "ok"})


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("carregar.html")

    if "file" not in request.files or request.files["file"].filename == "":
        flash("Please select a ZIP file.")
        return redirect(request.url)

    return import_problems()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)