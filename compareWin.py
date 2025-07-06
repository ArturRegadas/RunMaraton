import subprocess
import time
import os
import signal
import psutil
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
    # Remove espaços extras, quebras de linha, tabulações, trailing spaces
    lines = text.strip().split(r"\n")
    normalized_lines = [' '.join(line.strip().split()) for line in lines]  # remove espaços extras entre palavras
    return ''.join(normalized_lines)
def build_command(executable):
    if executable.endswith('.py'):
        return [sys.executable, executable]
    return [executable]

def run_with_limits_windows(
    executable, input_file, output_file,
    timelimit=1.0,
    number_of_repetitions=10,
    memory_limit_MB=128,
    output_limit_KB=64
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
                    stderr=subprocess.PIPE
                )

                try:
                    start_time = time.time()
                    while True:
                        if proc.poll() is not None:
                            break

                        if time.time() - start_time > timelimit:
                            proc.kill()
                            return TIME_LIMIT

                        try:
                            p = psutil.Process(proc.pid)
                            mem = p.memory_info().rss
                            if mem > memory_limit_bytes:
                                proc.kill()
                                return MEMORY_LIMIT
                        except psutil.NoSuchProcess:
                            break  # processo já morreu

                        time.sleep(0.01)

                    stdout, stderr = proc.communicate(timeout=1)

                except subprocess.TimeoutExpired:
                    proc.kill()
                    return TIME_LIMIT

                if proc.returncode != 0:
                    return RUNTIME_ERROR

                if len(stdout) > output_limit_bytes:
                    return SECURITY_THREAT

                with open('user_output.txt', 'wb') as f_out:
                    f_out.write(stdout)

        # Verificação da saída final
        with open('user_output.txt', 'r', encoding='utf-8', errors='ignore') as uo, \
             open(output_file, 'r', encoding='utf-8', errors='ignore') as exp:
            user_out = uo.read()
            expected_out = exp.read()

            if user_out == expected_out:
                return OK
            if normalize_text(user_out) == normalize_text(expected_out):
                return PRESENTATION_ERROR
            return WRONG_ANSWER

    except Exception as e:
        # Você pode querer logar e para debug: print(str(e))
        return INTERNAL_ERROR


