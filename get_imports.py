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


ADAFRUIT_BUNDLE_DATA = "latest_bundle_data.json"
ADAFRUIT_BUNDLE_TAG = "latest_bundle_tag.json"

COMMUNITY_BUNDLE_DATA = "latest_community_bundle_data.json"
COMMUNITY_BUNDLE_TAG = "latest_community_bundle_tag.json"

ADAFRUIT_BUNDLE_S3_URL = "https://adafruit-circuit-python.s3.amazonaws.com/bundles/adafruit/adafruit-circuitpython-bundle-{tag}.json"  # pylint: disable=line-too-long
COMMUNITY_BUNDLE_S3_URL = "https://adafruit-circuit-python.s3.amazonaws.com/bundles/community/circuitpython-community-bundle-{tag}.json"  # pylint: disable=line-too-long

SUBDIRECTORY_FILECOUNT_LIMIT = 10

LEARN_GUIDE_REPO = os.environ.get(
    "LEARN_GUIDE_REPO", "../Adafruit_Learning_System_Guides/"
)

SHOWN_FILETYPES = [
    "py",
    "mpy",
    "txt",
    "toml",
    "html",
    "bmp",
    "png",
    "jpg",
    "svg",
    "wav",
    "mp3",
    "mid",
    "pcf",
    "bdf",
    "csv",
    "json",
    "license",
]
SHOWN_FILETYPES_EXAMPLE = [s for s in SHOWN_FILETYPES if s != "py"]


def get_bundle(bundle_url, bundle_data_file):
    """Download the Adafruit and Community bundles data"""
    print(f"get bundle metadata from {bundle_url}")
    r = requests.get(bundle_url)
    with open(bundle_data_file, "wb") as bundle_file:
        bundle_file.write(r.content)


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


def get_latest_tag(repo_url):
    """
    Find the value of the latest tag for the Adafruit CircuitPython library
    bundle.
    :return: The most recent tag value for the project.
    """

    return get_latest_release_from_url(repo_url)


def ensure_latest_bundle(bundle_url, bundle_s3_url, bundle_tag_file, bundle_data_file):
    """
    Ensure that there's a copy of the latest library bundle available so circup
    can check the metadata contained therein.
    """
    print("Checking for library updates.")
    tag = get_latest_tag(bundle_url)
    old_tag = "0"
    if os.path.isfile(bundle_tag_file):
        with open(bundle_tag_file, encoding="utf-8") as data:
            try:
                old_tag = json.load(data)["tag"]
            except json.decoder.JSONDecodeError as _:
                # Sometimes (why?) the JSON file becomes corrupt. In which case
                # log it and carry on as if setting up for first time.
                print(f"Could not parse {bundle_tag_file:r}")
    if tag > old_tag:
        print(f"New version available {tag}.")
        try:
            get_bundle(bundle_s3_url.replace("{tag}", tag), bundle_data_file)
            with open(bundle_tag_file, "w", encoding="utf-8") as data:
                json.dump({"tag": tag}, data)
        except requests.exceptions.HTTPError as _:
            # See #20 for reason this
            print(
                (
                    "There was a problem downloading the bundle. "
                    "Please try again in a moment."
                ),
            )
            raise
    else:
        print(f"Current library bundle up to date {tag}")


ensure_latest_bundle(
    "https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/latest",
    ADAFRUIT_BUNDLE_S3_URL,
    ADAFRUIT_BUNDLE_TAG,
    ADAFRUIT_BUNDLE_DATA,
)
ensure_latest_bundle(
    "https://github.com/adafruit/CircuitPython_Community_Bundle/releases/latest",
    COMMUNITY_BUNDLE_S3_URL,
    COMMUNITY_BUNDLE_TAG,
    COMMUNITY_BUNDLE_DATA,
)

with open(ADAFRUIT_BUNDLE_DATA, "r", encoding="utf-8") as f:
    bundle_data = json.load(f)

with open(COMMUNITY_BUNDLE_DATA, "r", encoding="utf-8") as f:
    community_bundle_data = json.load(f)


def get_files_for_project(project_name):
    """Get the set of files for a learn project"""
    found_files = set()
    project_dir = f"{LEARN_GUIDE_REPO}/{project_name}/"

    full_tree = os.walk(project_dir)
    root_level = next(full_tree)

    for file in root_level[2]:
        if "." in file:
            cur_extension = file.split(".")[-1]
            if cur_extension in SHOWN_FILETYPES:
                # print(file)
                found_files.add(file)

    for _dir in root_level[1]:
        dir_tuple = (_dir, tuple())
        for cur_tuple in os.walk(project_dir):
            if cur_tuple[0].split("/")[-1] == _dir:
                for _sub_dir in cur_tuple[1]:
                    dir_tuple = (dir_tuple[0], dir_tuple[1] + (_sub_dir,))
                if len(cur_tuple[2]) < SUBDIRECTORY_FILECOUNT_LIMIT:
                    for _sub_file in cur_tuple[2]:
                        dir_tuple = (dir_tuple[0], dir_tuple[1] + (_sub_file,))

        # e.g. ("dir_name", ("file_1.txt", "file_2.txt"))
        found_files.add(dir_tuple)
    return found_files


def get_libs_for_project(project_name):
    # pylint: disable=too-many-nested-blocks
    """Get the set of libraries for a learn project"""
    found_libs = set()
    found_imports = []
    project_dir = f"{LEARN_GUIDE_REPO}{project_name}/"
    for file in os.listdir(project_dir):
        if file.endswith(".py"):

            found_imports = findimports.find_imports(f"{project_dir}{file}")
            for cur_import in found_imports:
                cur_lib = cur_import.name.split(".")[0]
                if cur_lib in bundle_data or cur_lib in community_bundle_data:
                    found_libs.add(cur_lib)

                # findimports returns import name in the form of "foo.bar.*"
                if cur_import.name.endswith(".*"):
                    filepath = os.path.join(
                        project_dir,
                        os.path.join(*cur_import.name[:-2].split(".")) + ".py",
                    )
                    if os.path.exists(filepath):
                        second_level_imports = findimports.find_imports(filepath)
                        for cur_second_level_import in second_level_imports:
                            cur_lib = cur_second_level_import.name.split(".")[0]
                            if (
                                cur_lib in bundle_data
                                or cur_lib in community_bundle_data
                            ):
                                found_libs.add(cur_lib)

    return found_libs


def get_files_for_example(example_path):
    """Get the set of files for a library example"""
    found_files = set(("code.py",))
    example_dir = os.path.dirname(example_path)

    full_tree = os.walk(example_dir)
    root_level = next(full_tree)

    for file in root_level[2]:
        if "." in file:
            cur_extension = file.split(".")[-1]
            if cur_extension in SHOWN_FILETYPES_EXAMPLE:
                # print(file)
                found_files.add(file)

    for _dir in root_level[1]:
        dir_tuple = (_dir, tuple())
        for cur_tuple in os.walk(example_dir):
            if cur_tuple[0].split("/")[-1] == _dir:
                for _sub_dir in cur_tuple[1]:
                    dir_tuple = (dir_tuple[0], dir_tuple[1] + (_sub_dir,))
                for _sub_file in cur_tuple[2]:
                    if _sub_file.split(".")[-1] in SHOWN_FILETYPES_EXAMPLE:
                        dir_tuple = (dir_tuple[0], dir_tuple[1] + (_sub_file,))

        # e.g. ("dir_name", ("file_1.txt", "file_2.txt"))

        if (
            ".circuitpython.skip-screenshot" not in dir_tuple[1]
            and len(dir_tuple[1]) > 0
        ):
            found_files.add(dir_tuple)
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
        # Do not recurse, but handle files in this folder
        if ".circuitpython.skip-screenshot-sub" in filenames:
            del dirnames[:]

        if any(f for f in filenames if f.endswith(".py")):
            yield os.path.relpath(dirpath, LEARN_GUIDE_REPO)


if __name__ == "__main__":
    for p in get_learn_guide_cp_projects():
        print("PROJECT", p)
