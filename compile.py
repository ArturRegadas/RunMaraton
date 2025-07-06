import os
import subprocess
from datetime import datetime
def compileFile(user, code, lenguage, compile):
    current_path = os.getcwd()
    BASE_DIR = current_path+"/submissions/code"
    EXE_DIR = current_path+"/submissions/scripts"
    print(code)
    name_fileCode ="runOf"+user+lenguage+str(datetime.now())+"."
    name_fileCode = name_fileCode[: -16] + name_fileCode[-15:]
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


    compile_cmd = [compile, SRC_PATH, "-o", name_file]    
    compile_proc = subprocess.run(compile_cmd, cwd=EXE_DIR, capture_output=True, text=True)

    if compile_proc.returncode != 0:
        return {
            'status': 1,
        }
    return {
        "status":0,
        "exe_file_path": EXE_DIR+"/"+name_file}

