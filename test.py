import os
import subprocess
import platform

BASE_DIR = "submissions"
SCRIPTS_DIR = "scripts"

code = "int main() { return 0; }"
print(code)

os.makedirs(BASE_DIR, exist_ok=True)

SRC_PATH = os.path.abspath(os.path.join(BASE_DIR, "user_code.c"))
EXE_PATH = os.path.abspath(os.path.join(BASE_DIR, "run"))

with open(SRC_PATH, "w") as file:
    file.write(code)

# Caminho absoluto do script compile
script_path = os.path.abspath(os.path.join(SCRIPTS_DIR, "compile"))

def windows_path_to_wsl(path):
    # Ex: C:\Users\foo\bar -> /mnt/c/Users/foo/bar
    path = path.replace("\\", "/")
    drive = path[0].lower()
    return f"/mnt/{drive}{path[2:]}"

if platform.system() == "Windows":
    # Converte caminhos para WSL
    script_path_wsl = windows_path_to_wsl(script_path)
    src_path_wsl = windows_path_to_wsl(SRC_PATH)
    exe_path_wsl = windows_path_to_wsl(EXE_PATH)

    compile_cmd = ["wsl", "bash", script_path_wsl, src_path_wsl, exe_path_wsl, '1', "512"]
else:
    compile_cmd = [script_path, SRC_PATH, EXE_PATH, '1', "512"]

# Executa a compilação
compile_proc = subprocess.run(compile_cmd, capture_output=True, text=True)

print("STDOUT:", compile_proc.stdout)
print("STDERR:", compile_proc.stderr)
print("Return code:", compile_proc.returncode)
