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
        print(file)
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


libs = get_libs_for_project("PyPortal_TOTP_Friend")
print(libs)