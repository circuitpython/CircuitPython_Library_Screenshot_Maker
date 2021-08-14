# SPDX-FileCopyrightText: 2021 foamyguy
# SPDX-FileCopyrightText: 2019 Nicholas Tollervey, written for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Get the list of required libraries based on a file's imports
"""

import json
import os
import findimports
import requests

BUNDLE_DATA = "latest_bundle_data.json"
BUNDLE_TAG = "latest_bundle_tag.json"

LEARN_GUIDE_REPO = os.environ.get(
    "LEARN_GUIDE_REPO", "../Adafruit_Learning_System_Guides/"
)

SHOWN_FILETYPES = ["py", "mpy", "bmp", "pcf", "bdf", "wav", "mp3", "mid", "json", "txt"]
SHOWN_FILETYPES_EXAMPLE = [s for s in SHOWN_FILETYPES if s != "py"]


def get_bundle(tag):
    """Download the given bundle's data to BUNDLE_DATA"""
    url = f"https://adafruit-circuit-python.s3.amazonaws.com/bundles/adafruit/adafruit-circuitpython-bundle-{tag}.json"  # pylint: disable=line-too-long
    print(f"get bundle metadata from {url}")
    r = requests.get(url)
    with open(BUNDLE_DATA, "wb") as bundle_file:
        bundle_file.write(r.content)


LATEST_BUNDLE_VERSION = ""


def get_latest_release_from_url(url):
    """
    Find the tag name of the latest release by using HTTP HEAD and decoding the redirect.

    :return: The most recent tag value for the release.
    """

    print(f"Requesting redirect information: {url}")
    response = requests.head(url)
    responseurl = response.url
    if response.is_redirect:
        responseurl = response.headers["Location"]
    tag = responseurl.rsplit("/", 1)[-1]
    print(f"Tag: {tag!r}")
    return tag


def get_latest_tag():
    """
    Find the value of the latest tag for the Adafruit CircuitPython library
    bundle.
    :return: The most recent tag value for the project.
    """
    global LATEST_BUNDLE_VERSION  # pylint: disable=global-statement
    if LATEST_BUNDLE_VERSION == "":
        LATEST_BUNDLE_VERSION = get_latest_release_from_url(
            "https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/latest"
        )
    return LATEST_BUNDLE_VERSION


def ensure_latest_bundle():
    """
    Ensure that there's a copy of the latest library bundle available so circup
    can check the metadata contained therein.
    """
    print("Checking for library updates.")
    tag = get_latest_tag()
    old_tag = "0"
    if os.path.isfile(BUNDLE_TAG):
        with open(BUNDLE_TAG, encoding="utf-8") as data:
            try:
                old_tag = json.load(data)["tag"]
            except json.decoder.JSONDecodeError as _:
                # Sometimes (why?) the JSON file becomes corrupt. In which case
                # log it and carry on as if setting up for first time.
                print(f"Could not parse {BUNDLE_TAG:r}")
    if tag > old_tag:
        print(f"New version available {tag}.")
        try:
            get_bundle(tag)
            with open(BUNDLE_TAG, "w", encoding="utf-8") as data:
                json.dump({"tag": tag}, data)
        except requests.exceptions.HTTPError as _:
            # See #20 for reason this this
            print(
                (
                    "There was a problem downloading the bundle. "
                    "Please try again in a moment."
                ),
            )
            raise
    else:
        print(f"Current library bundle up to date {tag}")


ensure_latest_bundle()

with open("latest_bundle_data.json", "r") as f:
    bundle_data = json.load(f)


def get_files_for_project(project_name):
    """Get the set of files for a learn project"""
    found_files = set()
    project_dir = "{}/{}/".format(LEARN_GUIDE_REPO, project_name)
    for file in os.listdir(project_dir):
        if "." in file:
            cur_extension = file.split(".")[-1]
            if cur_extension in SHOWN_FILETYPES:
                # print(file)
                found_files.add(file)
        else:
            # add dir
            found_files.add(file)
    return found_files


def get_libs_for_project(project_name):
    """Get the set of libraries for a learn project"""
    found_libs = set()
    found_imports = []
    project_dir = "{}{}/".format(LEARN_GUIDE_REPO, project_name)
    for file in os.listdir(project_dir):
        if file.endswith(".py"):

            found_imports = findimports.find_imports("{}{}".format(project_dir, file))

            for cur_import in found_imports:
                cur_lib = cur_import.name.split(".")[0]
                if cur_lib in bundle_data:
                    found_libs.add(cur_lib)

    return found_libs


def get_files_for_example(example_path):
    """Get the set of files for a library example"""
    found_files = set(("code.py",))
    example_dir = os.path.dirname(example_path)
    for file in os.listdir(example_dir):
        if "." in file:
            cur_extension = file.split(".")[-1]
            if cur_extension in SHOWN_FILETYPES_EXAMPLE:
                # print(file)
                found_files.add(file)
        else:
            # add dir
            found_files.add(file)
    return found_files


def get_libs_for_example(example_path):
    """Get the set of libraries for a library example"""
    found_libs = set()
    found_imports = []
    found_imports = findimports.find_imports(example_path)

    for cur_import in found_imports:
        cur_lib = cur_import.name.split(".")[0]
        if cur_lib in bundle_data:
            found_libs.add(cur_lib)

    return found_libs


def get_learn_guide_cp_projects():
    """Get the list of all circuitpython projects, according to some heuristics"""
    for dirpath, dirnames, filenames in os.walk(LEARN_GUIDE_REPO):
        # Don't consider hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        # The top-level needs special treatment
        if dirpath == LEARN_GUIDE_REPO:
            continue

        # Skip this folder and all subfolders
        if ".circuitpython.skip-screenshot" in filenames:
            del dirnames[:]
            continue
        # Skip files in this folder, but handle sub-folders
        if ".circuitpython.skip-screenshot-here" in filenames:
            continue
        # Do not reurse, but handle files in this folder
        if ".circuitpython.skip-screenshot-sub" in filenames:
            del dirnames[:]

        if any(f for f in filenames if f.endswith(".py")):
            yield os.path.relpath(dirpath, LEARN_GUIDE_REPO)


if __name__ == "__main__":
    for p in get_learn_guide_cp_projects():
        print("PROJECT", p)
