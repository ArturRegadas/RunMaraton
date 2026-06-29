import os
from pathlib import Path

def getName():
    name = {}

    file_path = Path(__file__).parent / "info.txt"

    with file_path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:  
                continue

            a, b = line.split(" = ", 1)
            name[a] = b

    return name


def getProblems(target):
    current_path = os.getcwd()
    ans = []
    for j in os.listdir(os.path.join(current_path, "problems")):
        if target == j[:5]:
            ans.append(j)
    return sorted(ans)

def getNameProblem(id):
    return getName()[id]
