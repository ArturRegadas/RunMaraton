import os
#from info import info
def getProblems(target):
    current_path = os.getcwd()
    ans = []
    for j in os.listdir(os.path.join(current_path, "problems")):
        if target == j[:5]:
            ans.append(j)
    return sorted(ans)

def getNameProblem(id):
    names={"2024LJ":"Jogo da Bocha"}
    return names[id]

def getDificult(id):
    dif={"2024LJ":1}

    return dif[id]