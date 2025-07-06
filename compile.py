import os
import subprocess
from datetime import datetime
def compileFile(user, code, lenguage, compile):
    current_path = os.getcwd()
    BASE_DIR = os.path.join(current_path, "submissions")
    EXE_DIR = os.path.join(BASE_DIR, "scripts")
    BASE_DIR = os.path.join(BASE_DIR, "code")
    print(code)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    name_fileCode = f"runOf_{user}_{lenguage}_{timestamp}."

    if(lenguage == "py"):
        SRC_PATH = os.path.join(EXE_DIR, name_fileCode+lenguage)

        with open(SRC_PATH, "w") as file:
            file.write(code)
        
        return {
            "status":0,
            "exe_file_path":SRC_PATH
        }


    system = ".exe" if os.name == "nt" else ".out"

    os.makedirs(BASE_DIR, exist_ok=True)

    SRC_PATH = os.path.join(BASE_DIR, name_fileCode+lenguage)
    with open(SRC_PATH, "w") as file:
        file.write(code)
    
    #compile

    name_file=user+system

    os.makedirs(EXE_DIR, exist_ok=True)
    compile_cmd = [compile, SRC_PATH, "-o", name_file]    
    compile_proc = subprocess.run(compile_cmd, cwd=EXE_DIR, capture_output=True, text=True)

    if compile_proc.returncode != 0:
        return {
            'status': 1,
        }
    return {
        "status":0,
        "exe_file_path": os.path.join(EXE_DIR, name_file)}

