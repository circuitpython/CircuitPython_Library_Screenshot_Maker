import findimports
import json
import os

LEARN_GUIDE_REPO = "../../Adafruit_Learning_System_Guides/"

with open("adafruit-circuitpython-bundle-20210423.json", "r") as f:
    bundle_data = json.load(f)


def get_files_for_project(project_name):
    found_files = set()
    project_dir = "{}{}/".format(LEARN_GUIDE_REPO, project_name)
    for file in os.listdir(project_dir):
        #print(file)
        found_files.add(file)
    return found_files

def get_libs_for_project(project_name):
    found_libs = set()
    found_imports = []
    project_dir = "{}{}/".format(LEARN_GUIDE_REPO, project_name)
    for file in os.listdir(project_dir):
        if file.endswith(".py"):

            found_imports = findimports.find_imports("{}{}".format(project_dir, file))

            for cur_import in found_imports:
                cur_lib = cur_import.name.split('.')[0]
                if cur_lib in bundle_data:
                    found_libs.add(cur_lib)

    return found_libs


def get_learn_guide_projects():
    return os.listdir(LEARN_GUIDE_REPO)


def get_learn_guide_cp_projects():
    cp_projects = []
    def has_py_file(dir):
        dir_files = os.listdir(dir)
        for file in dir_files:
            if file.endswith(".py"):
                if ".circuitpython.skip" not in dir_files:
                    return True
                else:
                    return False
        return False
    all_projects = get_learn_guide_projects()
    for project in all_projects:
        project_dir = "{}{}/".format(LEARN_GUIDE_REPO, project)
        try:
            if has_py_file(project_dir):
                cp_projects.append(project)
        except NotADirectoryError:
            pass
    return cp_projects
