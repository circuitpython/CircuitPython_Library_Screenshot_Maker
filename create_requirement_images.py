#!/usr/bin/env python3

"""
Create requirement screenshots for learn guide projects
"""

# SPDX-FileCopyrightText: 2021 foamyguy
#
# SPDX-License-Identifier: MIT

from multiprocessing import Pool
import json
import os

import click
from PIL import Image, ImageDraw, ImageFont
from get_imports import SHOWN_FILETYPES

from get_imports import (
    get_libs_for_project,
    get_files_for_project,
    get_libs_for_example,
    get_files_for_example,
    get_learn_guide_cp_projects,
)
from settings_required import settings_required

os.makedirs("generated_images", exist_ok=True)

OUT_WIDTH = 800
PADDING = 20

INDENT_SIZE = 28
LINE_SPACING = 28
HIGHLIGHT_ROW_COLOR = "#404040"
ROW_COLOR = "#383838"

TEXT_COLOR = "#B0B0B0"
HIDDEN_TEXT_COLOR = "#808080"

with open("latest_bundle_data.json", "r", encoding="utf-8") as f:
    bundle_data = json.load(f)


def asset_path(asset_name):
    """Return the location of a file shipped with the screenshot maker"""
    return os.path.join(os.path.dirname(__file__), asset_name)


font = ImageFont.truetype(asset_path("Roboto-Regular.ttf"), 24)
right_triangle = Image.open(asset_path("img/right_triangle.png"))
down_triangle = Image.open(asset_path("img/down_triangle.png"))

folder_icon = Image.open(asset_path("img/folder.png"))
folder_hidden_icon = Image.open(asset_path("img/folder_hidden.png"))
file_icon = Image.open(asset_path("img/file.png"))
file_hidden_icon = Image.open(asset_path("img/file_hidden.png"))
file_empty_icon = Image.open(asset_path("img/file_empty.png"))
file_empty_hidden_icon = Image.open(asset_path("img/file_empty_hidden.png"))

file_image_icon = Image.open(asset_path("img/file_image.png"))
file_music_icon = Image.open(asset_path("img/file_music.png"))
file_font_icon = Image.open(asset_path("img/file_font.png"))

FILE_TYPE_ICON_MAP = {
    "py": file_icon,
    "mpy": file_icon,
    "txt": file_empty_icon,
    "toml": file_icon,
    "bmp": file_image_icon,
    "wav": file_music_icon,
    "mp3": file_music_icon,
    "mid": file_music_icon,
    "pcf": file_font_icon,
    "bdf": file_font_icon,
    "csv": file_empty_icon,
    "json": file_icon,
    "license": file_empty_icon,
}

# If this is not done, the images fail to load in the subprocesses.
for _file_icon in FILE_TYPE_ICON_MAP.values():
    _file_icon.load()


def generate_requirement_image(
    project_files, libs, image_name
):  # pylint: disable=too-many-statements, too-many-locals
    """Generate a single requirement image"""

    context = {"added_settings_toml": False}

    def make_line(
        requirement_name, position=(0, 0), icon=None, hidden=False, triangle_icon=None
    ):  # pylint: disable=too-many-branches
        if triangle_icon:
            img.paste(
                triangle_icon,
                (position[0] - 24, position[1] + (LINE_SPACING - 24) // 2),
                mask=triangle_icon,
            )
        if icon is None:
            if requirement_name.endswith(".mpy") or requirement_name.endswith(".py"):
                if hidden:
                    img.paste(
                        file_hidden_icon,
                        (position[0], position[1] + (LINE_SPACING - 24) // 2),
                        mask=file_hidden_icon,
                    )
                else:
                    img.paste(
                        file_icon,
                        (position[0], position[1] + (LINE_SPACING - 24) // 2),
                        mask=file_icon,
                    )

            elif "." in requirement_name[-5:]:
                if hidden:
                    img.paste(
                        file_empty_hidden_icon,
                        (position[0], position[1] + (LINE_SPACING - 24) // 2),
                        mask=file_empty_icon,
                    )
                else:
                    img.paste(
                        file_empty_icon,
                        (position[0], position[1] + (LINE_SPACING - 24) // 2),
                        mask=file_empty_icon,
                    )
            else:
                if hidden:
                    img.paste(
                        folder_hidden_icon,
                        (position[0], position[1] + (LINE_SPACING - 24) // 2),
                        mask=folder_hidden_icon,
                    )
                else:
                    img.paste(
                        folder_icon,
                        (position[0], position[1] + (LINE_SPACING - 24) // 2),
                        mask=folder_icon,
                    )
        else:
            img.paste(
                icon, (position[0], position[1] + (LINE_SPACING - 24) // 2), mask=icon
            )

        if not hidden:
            draw.text(
                (position[0] + 30, position[1] + LINE_SPACING // 2),
                requirement_name,
                fill=TEXT_COLOR,
                anchor="lm",
                font=font,
            )
        else:
            draw.text(
                (position[0] + 30, position[1] + LINE_SPACING // 2),
                requirement_name,
                fill=HIDDEN_TEXT_COLOR,
                anchor="lm",
                font=font,
            )

    def make_header(position, project_files, files_and_libs):
        # pylint: disable=too-many-locals
        # Static files
        make_line(
            "CIRCUITPY",
            (position[0] + INDENT_SIZE, position[1]),
            triangle_icon=down_triangle,
        )
        make_line(
            ".fseventsd",
            (position[0] + INDENT_SIZE * 2, position[1] + (LINE_SPACING * 1)),
            hidden=True,
            triangle_icon=right_triangle,
        )
        make_line(
            ".metadata_never_index",
            (position[0] + INDENT_SIZE * 2, position[1] + (LINE_SPACING * 2)),
            icon=file_empty_hidden_icon,
            hidden=True,
        )
        make_line(
            ".Trashes",
            (position[0] + INDENT_SIZE * 2, position[1] + (LINE_SPACING * 3)),
            icon=file_empty_hidden_icon,
            hidden=True,
        )
        make_line(
            "boot_out.txt",
            (position[0] + INDENT_SIZE * 2, position[1] + (LINE_SPACING * 4)),
        )
        make_line(
            "code.py",
            (position[0] + INDENT_SIZE * 2, position[1] + (LINE_SPACING * 5)),
            icon=file_icon,
        )

        # TODO: Add settings.toml if it's needed

        if settings_required(files_and_libs):
            make_line(
                "settings.toml",
                (position[0] + INDENT_SIZE * 2, position[1] + (LINE_SPACING * 6)),
                icon=file_icon,
            )
            context["added_settings_toml"] = True

            if project_files:
                print(image_name)
                print(project_files)
                print("=============")

        # dynamic files from project dir in learn guide repo
        rows_added = 0
        project_files_to_draw = []
        project_folders_to_draw = {}
        for cur_file in project_files:
            # string for individual file
            if isinstance(cur_file, str):
                if "." in cur_file[-5:]:
                    cur_extension = cur_file.split(".")[-1]
                    if cur_extension in SHOWN_FILETYPES:
                        project_files_to_draw.append(cur_file)
            # tuple for directory
            elif isinstance(cur_file, tuple):
                if ".circuitpython.skip-screenshot" not in cur_file[1]:
                    project_folders_to_draw[cur_file[0]] = cur_file[1]

        begin_y_offset = 7 if context["added_settings_toml"] else 6
        for i, file in enumerate(sorted(project_files_to_draw)):
            cur_file_extension = file.split(".")[-1]

            cur_file_icon = FILE_TYPE_ICON_MAP.get(cur_file_extension, file_empty_icon)

            make_line(
                file,
                (
                    position[0] + INDENT_SIZE * 2,
                    position[1] + (LINE_SPACING * (begin_y_offset + i)),
                ),
                icon=cur_file_icon,
            )
            rows_added += 1

        extra_rows = 0
        for i, file in enumerate(sorted(project_folders_to_draw.keys())):
            make_line(
                file,
                (
                    position[0] + INDENT_SIZE * 2,
                    position[1]
                    + (
                        LINE_SPACING
                        * (begin_y_offset + i + len(project_files_to_draw) + extra_rows)
                    ),
                ),
                triangle_icon=down_triangle,
            )
            rows_added += 1
            for sub_file in sorted(project_folders_to_draw[file]):
                extra_rows += 1
                cur_file_extension = sub_file.split(".")[-1]
                cur_file_icon = FILE_TYPE_ICON_MAP.get(cur_file_extension, folder_icon)
                triangle_icon = None
                if cur_file_icon == folder_icon:
                    triangle_icon = right_triangle
                make_line(
                    sub_file,
                    (
                        position[0] + INDENT_SIZE * 3,
                        position[1] + (LINE_SPACING * (begin_y_offset + rows_added)),
                    ),
                    triangle_icon=triangle_icon,
                    icon=cur_file_icon,
                )
                rows_added += 1

        make_line(
            "lib",
            (
                position[0] + INDENT_SIZE * 2,
                position[1] + (LINE_SPACING * ((begin_y_offset - 1) + rows_added + 1)),
            ),
            triangle_icon=down_triangle,
        )

    def make_background_highlights(rows, offset=(0, 0)):
        for i in range(rows):
            if i % 2 == 0:
                draw.rectangle(
                    [
                        (0 + offset[0], i * LINE_SPACING + offset[1]),
                        (OUT_WIDTH - offset[0], (i + 1) * LINE_SPACING + offset[1]),
                    ],
                    fill=HIGHLIGHT_ROW_COLOR,
                )
            else:
                draw.rectangle(
                    [
                        (0 + offset[0], i * LINE_SPACING + offset[1]),
                        (OUT_WIDTH - offset[0], (i + 1) * LINE_SPACING + offset[1]),
                    ],
                    fill=ROW_COLOR,
                )

    def get_dependencies(libraries):
        package_list = set()
        file_list = set()

        libraries_to_check = list(libraries)

        while len(libraries_to_check) > 0:
            lib_name = libraries_to_check[0]
            del libraries_to_check[0]

            try:
                lib_obj = bundle_data[lib_name]
            except KeyError:
                # Library isn't in bundle, so we don't know about its
                # dependencies.
                if "." in lib_name:
                    file_list.add(lib_name)
                else:
                    package_list.add(lib_name)
                continue

            for dep_name in lib_obj["dependencies"]:
                libraries_to_check.append(dep_name)
                dep_obj = bundle_data[dep_name]
                if dep_obj["package"]:
                    package_list.add(dep_name)
                else:
                    file_list.add(dep_name + ".mpy")

            if lib_obj["package"]:
                package_list.add(lib_name)
            else:
                file_list.add(lib_name + ".mpy")

        return package_list, file_list

    def sort_libraries(libraries):
        package_list, file_list = get_dependencies(libraries)
        return sorted(package_list) + sorted(file_list)

    def count_files(files_list):
        _count = 0
        for _file in files_list:
            # string for individual file
            if isinstance(_file, str):
                _count += 1

            # tuple for directory
            elif isinstance(_file, tuple):
                if ".circuitpython.skip-screenshot" not in _file[1]:
                    _count += 1
                    _count += len(_file[1])
        return _count

    def make_libraries(libraries, position):

        for i, lib_name in enumerate(libraries):
            triangle_icon = None
            if not lib_name.endswith(".mpy"):
                triangle_icon = right_triangle
            make_line(
                lib_name,
                (
                    position[0] + INDENT_SIZE * 3,
                    position[1]
                    + (
                        LINE_SPACING
                        * (i + (1 if context["added_settings_toml"] else 0))
                    ),
                ),
                triangle_icon=triangle_icon,
            )

    def make_sd_dir(position):
        make_line(
            "sd",
            position,
            triangle_icon=right_triangle,
        )

    def filter_custom_project_libs(project_file_set):
        """
        Find and remove the custom project lib folder.
        Returns a tuple with the contents of the custom project lib folder
        which will in turn get included in the libraries list that the
        tool uses to generate the "main" lib folder in the screenshot.
        """
        _custom_libs = None
        remove_files = []
        for file in project_file_set:
            if not isinstance(file, tuple):
                continue
            if file[0] == "lib":
                _custom_libs = file[1]
                remove_files.append(file)
        for file in remove_files:
            project_file_set.remove(file)
        return _custom_libs

    custom_libs = filter_custom_project_libs(project_files)
    libs_list = list(libs)
    libs_list.extend(custom_libs)
    libs = set(libs_list)
    final_list_to_render = sort_libraries(libs)
    if settings_required(final_list_to_render):
        context["added_settings_toml"] = True

    if "code.py" in project_files:
        project_files.remove("code.py")

    if "main.py" in project_files:
        project_files.remove("main.py")

    project_files_count = count_files(project_files)

    image_height = (
        PADDING * 2
        + 7 * LINE_SPACING
        + len(final_list_to_render) * LINE_SPACING
        + (project_files_count) * LINE_SPACING
        + (1 if context["added_settings_toml"] else 0) * LINE_SPACING
        + 1 * LINE_SPACING  # /sd/ dir
    )
    img = Image.new("RGB", (OUT_WIDTH, image_height), "#303030")
    draw = ImageDraw.Draw(img)

    make_background_highlights(
        7
        + len(final_list_to_render)
        + project_files_count
        + (1 if context["added_settings_toml"] else 0)
        + 1,  # for /sd/ dir
        offset=(PADDING, PADDING),
    )
    print(f"fltr: {final_list_to_render}")
    make_header((PADDING, PADDING), project_files, final_list_to_render)
    _libraries_position = (
        PADDING,
        PADDING + (LINE_SPACING * (7 + project_files_count)),
    )
    make_libraries(final_list_to_render, _libraries_position)

    _sd_dir_position = (
        76,
        PADDING
        + (LINE_SPACING * (7 + project_files_count + len(final_list_to_render)))
        + (1 if context["added_settings_toml"] else 0) * LINE_SPACING,
    )
    make_sd_dir(_sd_dir_position)

    img.save(f"generated_images/{image_name}.png")


def generate_learn_requirement_image(  # pylint: disable=invalid-name
    learn_guide_project,
):
    """Generate an image for a single learn project"""
    image_name = learn_guide_project.replace("/", "_")
    libs = get_libs_for_project(learn_guide_project)
    project_files = get_files_for_project(learn_guide_project)
    generate_requirement_image(project_files, libs, image_name)


def generate_example_requirement_image(example_path):  # pylint: disable=invalid-name
    """Generate an image for a library example"""
    image_name = "_".join(
        element
        for element in example_path.split("/")
        if element not in ("libraries", "drivers", "helpers", "examples")
    )
    libs = get_libs_for_example(example_path)
    project_files = get_files_for_example(example_path)
    generate_requirement_image(project_files, libs, image_name)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Main entry point; invokes the learn subcommand if nothing is specified"""
    if ctx.invoked_subcommand is None:
        learn()


@cli.command()
@click.option(
    "-g", "--guide", help="Guide Name of a single Learn Guide to generate an image for."
)
def learn(guide=None):
    """Generate images for a learn-style repo"""
    if guide is None:
        with Pool() as pool:
            for _ in pool.imap(
                generate_learn_requirement_image, get_learn_guide_cp_projects()
            ):
                pass
    else:
        print(f"generating image for single guide: {guide}")
        generate_learn_requirement_image(guide)


@cli.command()
@click.argument("paths", nargs=-1)
def bundle(paths):
    """Generate images for a bundle-style repo"""
    with Pool() as pool:
        for _ in pool.imap(generate_example_requirement_image, paths):
            pass


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
