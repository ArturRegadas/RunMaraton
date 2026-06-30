import json
import os
from src.compile_submission import compileFile

def RunSubimission(code, lenguage, problem, user):
    if(lenguage == "cpp"):
        response = compileFile(user, code,'cpp',"g++")
        if(response["status"] == 1):
            return 1
        file_path=response["exe_file_path"]
    elif(lenguage == 'c'):
        response = compileFile(user, code,'c',"gcc")
        if(response["status"] == 1):
            return 1
        file_path=response["exe_file_path"]
    elif(lenguage == "python"):
        response = compileFile(user, code, "py", "python3")
        file_path = response["exe_file_path"]
    else:
        return 5
    
    current_path = os.getcwd()
    problem_path = os.path.join(current_path, "problems", problem)
    #pass
    tle_path = os.path.join(problem_path,"limits.json")
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

    if lenguage == "python":
        data["time"]+=2
    return Run(
        file_path,
        os.path.join(current_path, "problems", problem, "inputs",),
        os.path.join(current_path, "problems", problem, "outputs",),
        int(data["time"]),
        int(data["number_of_repetitions"]),
        int(data["memory_limit_MB"]),
        int(data["output_limit_KB"]),
        user
    )
#run.o or run.py

def Run(file_path,
        input_path, 
        output_path,
        time_limit,
        number_of_repetitions,
        memory_limit_MB,
        output_limit_KB,
        username
    ):
    
    import os
    current_path = os.getcwd()


    if os.name == 'nt':
        from src.compareWin import run_with_limits_windows
        for f in os.listdir(input_path):
            if os.path.isfile(os.path.join(input_path, f)):
                status = run_with_limits_windows(
                    executable=file_path,
                    input_file=os.path.join(input_path, f),
                    output_file=os.path.join(output_path, f),
                    timelimit=time_limit,
                    number_of_repetitions=number_of_repetitions,
                    memory_limit_MB=memory_limit_MB,
                    output_limit_KB=output_limit_KB,
                    username=username
                )
        
                if status != 0:
                    return status
        return 0

    elif os.name == 'posix':
        from src.compareLin import run_with_limits_linux
        for f in os.listdir(input_path):
            if os.path.isfile(os.path.join(input_path, f)):
                status = run_with_limits_linux(
                    executable=file_path,
                    input_file=os.path.join(input_path, f),
                    output_file=os.path.join(output_path, f),
                    timelimit=time_limit,
                    number_of_repetitions=number_of_repetitions,
                    memory_limit_MB=memory_limit_MB,
                    output_limit_KB=output_limit_KB,
                    username=username
                )
        
                if status != 0:
                    return status
        return 0





if (__name__=="__main__"):
    pass