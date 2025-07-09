from flask import *
from runSubmissions import RunSubimission
from support.getInfo import getProblems, getNameProblem, getDificult


users={
    "adm":"adm"

}
app = Flask(__name__)


def verifyLogin():
    username = request.cookies.get("username")
    password = request.cookies.get("password")
    if(not username or not password or not username in users or users[username] != password):
        return redirect(url_for("home"))



@app.route("/submit", methods=["POST"])
def submit():
    code = request.form["code"]
    lenguage = request.form["lenguage"]
    status = RunSubimission(code, lenguage, "2024IJ", "Artur")
    return str(status)
@app.route("/problem/<id_problem>")
def problem(id_problem):
    verifyLogin()
    return render_template(
        "problem.html",
        filePdf="InterIF2025_Classificados_FaseFinal.pdf",
        code="",
        ended="",
        result=""
    )

@app.route("/tests/<test>")
def tests(test):
    verifyLogin()
    problems = getProblems(test)
    ans= []
    for i in problems:
        ans.append({"id":i, "title": getNameProblem(i), "questoes":getDificult(i)})
    return render_template("index.html", case = "Difuldade",tests=ans)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    print(request.form)
    if username in users and users[username] == password:
        response = make_response(redirect(url_for('home')))
        response.set_cookie("username", username, max_age=60*120)#2hrs
        response.set_cookie("password", password, max_age=60*120)
        return response
    return render_template("login.html", msg="incorrect user or password")

@app.route("/")
def home():
    verifyLogin()
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
            if users[username] == password:
                print(type(tests))
                return render_template("index.html",case="Questoes" ,tests = tests)

    return render_template("login.html", msg="")

@app.route("/createUser", methods=["POST"])
def createUser():
    newUser = request.form["username"]
    newPassword = request.form["password"]
    if newUser in users:
        return render_template("createUser.html", msg="usuario ja existe")
    users[newUser] = newPassword
    return redirect(url_for("home"))

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
    app.run(debug=True)