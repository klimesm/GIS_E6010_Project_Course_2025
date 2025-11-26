import os

def find_conda_pythons():
    python_list = []

    def add_if_exists(path):
        if os.path.isfile(path):
            python_list.append(path)

    # default conda paths
    default_paths = [
        r"C:\Users\{}\miniconda3\envs".format(os.getenv("USERNAME")),
        r"C:\Users\{}\anaconda3\envs".format(os.getenv("USERNAME")),
    ]

    # custom path
    custom_path = r"C:\conda\envs"

    for root in default_paths + [custom_path]:
        if os.path.isdir(root):
            for env in os.listdir(root):
                exe = os.path.join(root, env, "python.exe")
                add_if_exists(exe)

    return python_list
