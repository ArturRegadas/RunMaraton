import subprocess
import time
import os
import signal
import resource
import difflib
import sys


OK = 0
COMPILE_ERROR = 1
RUNTIME_ERROR = 2
TIME_LIMIT = 3
INTERNAL_ERROR = 4
PARAM_ERROR = 5
INTERNAL_ERROR_2 = 6
MEMORY_LIMIT = 7
SECURITY_THREAT = 8
WRONG_ANSWER = 9
PRESENTATION_ERROR = 10



def normalize_text(text):
    lines = text.strip().split(r"\n")
    normalized_lines = [' '.join(line.strip().split()) for line in lines] 
    return ''.join(normalized_lines)

def build_command(executable):
    if executable.endswith('.py'):
        return [sys.executable, executable]
    return [executable]

def limit_resources(memory_limit_bytes, output_limit_bytes, cpu_time_limit_seconds):
    def set_limits():
        
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))

        
        cpu_time_limit = int(cpu_time_limit_seconds) + 1
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_time_limit, cpu_time_limit))

    
        resource.setrlimit(resource.RLIMIT_FSIZE, (output_limit_bytes, output_limit_bytes))
    return set_limits

def run_with_limits_linux(
    executable,
    input_file,
    output_file,
    timelimit,
    number_of_repetitions,
    memory_limit_MB,
    output_limit_KB
):

    if not os.path.isfile(executable):
        return COMPILE_ERROR
    if not os.path.isfile(input_file) or not os.path.isfile(output_file):
        return PARAM_ERROR

    memory_limit_bytes = memory_limit_MB * 1024 * 1024
    output_limit_bytes = output_limit_KB * 1024

    try:
        for _ in range(number_of_repetitions):
            with open(input_file, 'rb') as f_in:
                cmd = build_command(executable)
                proc = subprocess.Popen(
                    cmd,
                    stdin=f_in,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=limit_resources(memory_limit_bytes, output_limit_bytes, timelimit)
                )

                try:
                    stdout, stderr = proc.communicate(timeout=timelimit)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    return TIME_LIMIT

                if proc.returncode != 0:
                    if proc.returncode == -9:
                        return MEMORY_LIMIT
                    return RUNTIME_ERROR

                if len(stdout) > output_limit_bytes:
                    return SECURITY_THREAT

                with open('user_output.txt', 'wb') as f_out:
                    f_out.write(stdout)

        with open('user_output.txt', 'r', encoding='utf-8', errors='ignore') as uo, \
             open(output_file, 'r', encoding='utf-8', errors='ignore') as exp:
            user_out = str(uo.read())
            expected_out = str(exp.read())

            if user_out == expected_out:
                return OK
            if normalize_text(user_out) == normalize_text(expected_out):
                return PRESENTATION_ERROR
            return WRONG_ANSWER

    except Exception as e:
        return INTERNAL_ERROR
    


def main():
    current_path = ""
    status = run_with_limits_linux(
        executable=os.path.join(current_path,'run.py'),
        input_file=os.path.join(current_path,'submissions','input'),
        output_file=os.path.join(current_path,'submissions','output'),
        timelimit=1.0,
        number_of_repetitions=10,
        memory_limit_MB=64,
        output_limit_KB=32
    )


