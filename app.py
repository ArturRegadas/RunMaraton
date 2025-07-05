from flask import *
import subprocess
import os

app = Flask(__name__)

BASE_DIR = "submissions"
SCRIPTS_DIR = "scripts"

@app.route("/submit", methods=["POST"])
def submit():
    code = request.form["code"]
    print(code)
    
    os.makedirs(BASE_DIR, exist_ok=True)

    SRC_PATH = os.path.join(BASE_DIR, "user_code.c")
    INPUT_PATH = os.path.join(BASE_DIR, "input.txt")
    OUTPUT_PATH = os.path.join(BASE_DIR, "output.txt")
    EXE_PATH = os.path.join(BASE_DIR, "run")

    with open(SRC_PATH, "w") as file:
        file.write(code)
    
    #compile
    compile_cmd = [os.path.join(SCRIPTS_DIR, "compile.sh"), SRC_PATH, EXE_PATH, '1', "512"]    
    compile_proc = subprocess.run(compile_cmd, cwd=BASE_DIR, capture_output=True, text=True)

    if compile_proc.returncode != 0:
        return jsonify({
            'status': 'compilation_error',
            'message': compile_proc.stdout + compile_proc.stderr
        })
    
    #run
    run_cmd = [os.path.join(SCRIPTS_DIR, "run"), EXE_PATH, INPUT_PATH, '1', '1', "512", "1024"]
    run_proc = subprocess.run(run_cmd, cwd=BASE_DIR, capture_output=True, text=True)

    user_output_path = os.path.join(BASE_DIR, 'stdout0')
    if not os.path.exists(user_output_path):
        return jsonify({'status': 'runtime_error', 'output': run_proc.stderr})
    
    #compare
    compare_cmd = [os.path.join(SCRIPTS_DIR, 'compare'), user_output_path, OUTPUT_PATH, INPUT_PATH]
    compare_proc = subprocess.run(compare_cmd, cwd=BASE_DIR, capture_output=True, text=True)

    compare_code = compare_proc.returncode
    result_map = {
        4: 'accepted',
        5: 'presentation_error',
        6: 'wrong_answer'
    }

    return jsonify({
        'status': result_map.get(compare_code, 'unknown'),
        'compare_output': compare_proc.stdout,
        'run_output': run_proc.stdout
    })

@app.route("/")
def home():
    return render_template("index.html")



if(__name__=="__main__"):
    app.run(debug=True)