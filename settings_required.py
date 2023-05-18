# SPDX-FileCopyrightText: 2023 Tim C
# SPDX-License-Identifier: MIT

"""
Utility function to check whether settings.toml file should be rendered for a project.
Based on whether it uses certain libraries or not.
"""


LIBRARIES_THAT_REQUIRE_SETTINGS = [
    "adafruit_requests.mpy",
    "adafruit_esp32spi",
    "adafruit_minimqtt",
    "adafruit_portalbase",
    "adafruit_azureiot",
]


def settings_required(files_and_libs):
    """
    Returns True if the project needs ot have a settings.toml file

    :param files_and_libs list: a List of all files and libraries used in the project
    """

    if "settings.toml" in files_and_libs:
        # settings.toml file is already in the files so we don't need to add it again
        return False

    # if any of the libraries that require settings.toml are included in this project
    if any(
        libs_that_require_settings in files_and_libs
        for libs_that_require_settings in LIBRARIES_THAT_REQUIRE_SETTINGS
    ):
        return True

    return False
