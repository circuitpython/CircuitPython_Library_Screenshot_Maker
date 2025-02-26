# SPDX-FileCopyrightText: 2023 Tim C
# SPDX-License-Identifier: MIT

"""
Utility function to check whether settings.toml file should be rendered for a project.
Based on whether it uses certain libraries or not.
"""


def settings_required(files_and_libs):
    """
    Returns True if the project needs ot have a settings.toml file

    :param files_and_libs list: a List of all files and libraries used in the project
    """

    if "settings.toml" in files_and_libs:
        # settings.toml file is already in the files so we don't need to add it again
        return False

    # always show settings.toml because it is created by default when
    # circuitpython is loaded, and when storage.erase_filesystem() is called
    return True
