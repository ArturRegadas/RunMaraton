from flask import *
from src.runSubmissions import RunSubimission
from src.support.getInfo import getProblems, getNameProblem
from src.support.getDiference import diferenceOf, codesOf
from src.models import load_from_db, createUserInDb, addExerciceInDb
from src import models as mdl




app = mdl.app
with app.app_context():
    mdl.db.create_all()
    users = load_from_db()


def verifyLogin():
    username = request.cookies.get("username")
    password = request.cookies.get("password")
    if(not username or not password or not username in users or users[username]["password"] != password):
        return False
    return True



@app.route("/submit", methods=["POST", "GET"])
def submit():
    if(not verifyLogin()):
        return redirect(url_for("home"))
    data = request.get_json()
    code = data["code"]
    lenguage = data["lenguage"]
    problem = data["problem"]
    username = request.cookies.get("username")
    status = RunSubimission(code, lenguage, problem, username)
    if(status == 0):
        addExerciceInDb(username, problem)
        users[username]["finalized"].add(problem)
        return {
            "status": "ACCEPT",
            "color": "#00d062"
        }
    if(status == 1):
        return {
            "status": "COMPILATION ERROR",
            "color": "#e79907"
        }

    if(status == 2 or status == 8):
        return {
            "status": "RUNTIME ERROR",
            "color": "#00d9e0"
        }
    
    if(status == 3):
        return{
            "status": "TIMELIMIT",
            "clor": "#004ec4"
        }
    
    if(status == 4 or status == 6):
        return {
            "status":"INTERNAL ERROR",
            "color": "#3B3B3B"
        }
    
    if(status == 5):
        return {
            "status":"PARAMS ERROR",
            "color": "#3B3B3B"
        }
    
    if(status == 7):
        return {
            "status":"MEMORY LIMIT",
            "color": "#8A751A"
        }

    if(status == 9):
        user_output, expected_output = diferenceOf(username)
        return {
            "status": "WRONG ANSWER",
            "color": "#DA1D1D",
            "user_output":user_output,
            "expected_output": expected_output
        }
    
    if(status == 10):
        user_output, expected_output = codesOf(username)
        return {
            "status": "PRESENTATION ERROR",
            "color": "#9BB602",
            "user_output":user_output,
            "expected_output": expected_output
        }    
    
@app.route("/seeDetails/<username>")
def seeDetails(username):
    if(not verifyLogin()):
        return redirect(url_for("home"))
    us, es = codesOf(username)
    return render_template(
        "details.html",
        user_submission = us,
        expected_submission= es,
        )

@app.route("/problem/<id_problem>")
def problem(id_problem):
    if(not verifyLogin()):
        return redirect(url_for("home"))
    username = request.cookies.get("username")
    return render_template(
        "problem.html",
        username=username,
        filePdf=f"{id_problem}.pdf",
        problemId=id_problem,
        ended='FINALIZADO' if id_problem in users[username]["finalized"] else ""
    )

@app.route("/tests/<test>")
def tests(test):
    if(not verifyLogin()):
        return redirect(url_for("home"))
    problems = getProblems(test)
    ans= []
    for i in problems:
        ans.append({"id":i, "title": getNameProblem(i), "questoes":"✅" if i in users[request.cookies.get("username")]["finalized"] else "❌"})
    return render_template("index.html", case = "Finalizado",tests=ans, page="problem")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    if username in users and users[username]["password"] == password:
        response = make_response(redirect(url_for('home')))
        response.set_cookie("username", username, max_age=60*120)#2hrs
        response.set_cookie("password", password, max_age=60*120)
        return response
    return render_template("login.html", msg="incorrect user or password")

@app.route("/")
def home():
    tests = [
        { "id": "2024F", "title": "INTERIF 2024 - Fase Final", "questoes": 10 },
        { "id": "2024L", "title": "INTERIF 2024 - Fase Local", "questoes": 10 },
        { "id": "2023F", "title": "INTERIF 2023 - Fase Final", "questoes": 8 },
        { "id": "2023L", "title": "INTERIF 2023 - Fase Local", "questoes": 9 }
    ]
    username = request.cookies.get("username")
    password = request.cookies.get("password")
    if username and password:
        if username in users:
            if users[username]["password"] == password:
                return render_template("index.html",case="Questoes" ,tests = tests, page="tests")

    return render_template("login.html", msg="")

@app.route("/createUser", methods=["POST"])
def createUser():
    newUser = request.form["username"]
    newPassword = request.form["password"]
    if newUser in users:
        return render_template("createUser.html", msg="usuario ja existe")
    if(createUserInDb(newUser, newPassword)):
        users[newUser]={}
        users[newUser]["password"] = newPassword
        users[newUser]["finalized"] = set()
        return redirect(url_for("home"))
    return "Error"

@app.route("/newUser")
def newUser():
    return render_template("createUser.html", msg="")

@app.route("/logout")
def logout():
    response = make_response(redirect(url_for('home')))
    response.set_cookie("username", "", expires=0)
    response.set_cookie("password", "", expires=0)
    return response

if(__name__=="__main__"):
    app.run(host="0.0.0.0", port=5000)