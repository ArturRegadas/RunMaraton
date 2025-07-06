import json
import os
from compile import compileFile
def RunSubimission(code, lenguage, problem, user):
    if(lenguage == "c++"):
        response = compileFile(user, code,'cpp',"g++")
        if(response["status"] == 1):
            return 1
        file_path=response["exe_file_path"]
    elif(lenguage == 'c'):
        response = compileFile(user, code,'c',"gcc")
        if(response["status"] == 1):
            return 1
        file_path=response["exe_file_path"]
    elif(lenguage == "py"):
        response = compileFile(user, code, "py", "python3")
        file_path = response["exe_file_path"]
    else:
        return 5
    
    current_path = os.getcwd()
    problem_path = current_path+"/problems/"+problem
    tle_path = problem_path+"/limits.json"
    print(tle_path)
    with open(tle_path, 'r', encoding="utf-8") as file:
        data = json.load(file)
    
    if not "time" in data:
        data["time"] = 1
    if not "number_of_repetitions" in data:
        data["number_of_repetitions"] = 10
    if not "memory_limit_MB" in data:
        data["memory_limit_MB"] = 1024
    if not "output_limit_KB" in data:
        data["output_limit_KB"] = 1024

    return Run(
        file_path,
        current_path+"/problems/"+problem+"/input",
        current_path+"/problems/"+problem+"/output",
        data["time"],
        data["number_of_repetitions"],
        data["memory_limit_MB"],
        data["output_limit_KB"]
    )
#run.o or run.py

def Run(file_path,
        input_path, 
        output_path,
        time_limit,
        number_of_repetitions,
        memory_limit_MB,
        output_limit_KB
    ):
    
    import os
    current_path = os.getcwd()
    caminho = current_path+"/problems/2024IJ/input"


    if os.name == 'nt':
        from compareWin import run_with_limits_windows
        for f in os.listdir(caminho):
            if os.path.isfile(os.path.join(caminho, f)):
                status = run_with_limits_windows(
                    executable=file_path,
                    input_file=input_path,
                    output_file=output_path,
                    timelimit=time_limit,
                    number_of_repetitions=number_of_repetitions,
                    memory_limit_MB=memory_limit_MB,
                    output_limit_KB=output_limit_KB
                )
        
                if status != 0:
                    return status
        return 0

    elif os.name == 'posix':
        from compareLin import run_with_limits_linux
        for f in os.listdir(caminho):
            if os.path.isfile(os.path.join(caminho, f)):
                status = run_with_limits_linux(
                    executable=file_path,
                    input_file=input_path+'/'+f,
                    output_file=output_path+'/'+f,
                    timelimit=time_limit,
                    number_of_repetitions=number_of_repetitions,
                    memory_limit_MB=memory_limit_MB,
                    output_limit_KB=output_limit_KB
                )
        
                if status != 0:
                    return status
        return 0



if (__name__=="__main__"):
    pass