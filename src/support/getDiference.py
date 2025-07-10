import os
def diferenceOf(user):
    user_output_path = os.path.join(os.getcwd(), "submissions", "outputs", user+".txt")
    expected_output_path = os.path.join(os.getcwd(), "submissions", "error", user+".txt")
    with open(user_output_path, "r") as file:
        user_output = file.read().splitlines()
    with open(expected_output_path,"r") as file:
        expected_output = file.read().splitlines()

    for i in range(min(len(user_output), len(expected_output))):
        if user_output[i] != expected_output[i]:
            return user_output[i], expected_output[i]
    return "", expected_output[-1]

def codesOf(user):
    user_output_path = os.path.join(os.getcwd(), "submissions", "outputs", user+".txt")
    expected_output_path = os.path.join(os.getcwd(), "submissions", "error", user+".txt")
    with open(user_output_path, "r") as file:
        user_output = file.read()
    with open(expected_output_path,"r") as file:
        expected_output = file.read()

    return user_output, expected_output