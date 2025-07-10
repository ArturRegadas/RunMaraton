import os
from src.support.info import name
def getProblems(target):
    current_path = os.getcwd()
    ans = []
    for j in os.listdir(os.path.join(current_path, "problems")):
        if target == j[:5]:
            ans.append(j)
    return sorted(ans)

def getNameProblem(id):
    return name[id]
