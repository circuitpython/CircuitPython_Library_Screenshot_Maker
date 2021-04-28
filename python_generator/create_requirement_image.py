import traceback

from PIL import Image, ImageDraw, ImageFont
import json

from python_generator.get_imports import get_libs_for_project, get_files_for_project, get_learn_guide_cp_projects

OUT_WIDTH = 800
PADDING = 20

INDENT_SIZE = 28
LINE_SPACING = 28
HIGHLIGHT_ROW_COLOR = "#404040"
ROW_COLOR = "#383838"

TEXT_COLOR = "#B0B0B0"
HIDDEN_TEXT_COLOR = "#808080"

SHOWN_FILETYPES = ["py", "mpy", "bmp", "pcf", "bdf", "wav", "mp3", "json", "txt"]
"""
libraries_to_render = ['adafruit_bitmap_font',
                       'adafruit_bus_device',
                       'adafruit_display_shapes',
                       'adafruit_display_text',
                       'adafruit_esp32spi',
                       'adafruit_hashlib',
                       'adafruit_imageload',
                       'adafruit_io',
                       'adafruit_progressbar',
                       'adafruit_pyportal',
                       'adafruit_binascii',
                       'adafruit_button',
                       'adafruit_ntp',
                       'adafruit_requests',
                       'adafruit_sdcard',
                       'adafruit_touchscreen',
                       'neopixel',
                       'simpleio'
                       ]
                       """

f = open("adafruit-circuitpython-bundle-20210423.json", "r")
bundle_data = json.load(f)
f.close()

font = ImageFont.truetype("Roboto-Regular.ttf", 24)
right_triangle = Image.open('img/right_triangle.png')
down_triangle = Image.open('img/down_triangle.png')

folder_icon = Image.open('img/folder.png')
folder_hidden_icon = Image.open('img/folder_hidden.png')
file_icon = Image.open('img/file.png')
file_hidden_icon = Image.open('img/file_hidden.png')
file_empty_icon = Image.open('img/file_empty.png')
file_empty_hidden_icon = Image.open('img/file_empty_hidden.png')


def generate_requirement_image(learn_guide_project):
    def make_line(requirement_name, position=(0, 0), icon=None, hidden=False, triangle_icon=None):
        if triangle_icon:
            im.paste(triangle_icon, (position[0] - 24, position[1] + (LINE_SPACING - 24) // 2), mask=triangle_icon)
        if icon == None:
            if (requirement_name.endswith(".mpy") or requirement_name.endswith(".py")):
                if hidden:
                    im.paste(file_hidden_icon, (position[0], position[1] + (LINE_SPACING - 24) // 2),
                             mask=file_hidden_icon)
                else:
                    im.paste(file_icon, (position[0], position[1] + (LINE_SPACING - 24) // 2), mask=file_icon)

            elif "." in requirement_name[-5:]:
                if hidden:
                    im.paste(file_empty_hidden_icon, (position[0], position[1] + (LINE_SPACING - 24) // 2), mask=file_empty_icon)
                else:
                    im.paste(file_empty_icon, (position[0], position[1] + (LINE_SPACING - 24) // 2), mask=file_empty_icon)
            else:
                if hidden:
                    im.paste(folder_hidden_icon, (position[0], position[1] + (LINE_SPACING - 24) // 2),
                             mask=folder_hidden_icon)
                else:
                    im.paste(folder_icon, (position[0], position[1] + (LINE_SPACING - 24) // 2), mask=folder_icon)
        else:
            im.paste(icon, (position[0], position[1] + (LINE_SPACING - 24) // 2), mask=icon)

        if not hidden:
            draw.text((position[0] + 30, position[1] + LINE_SPACING // 2),
                      requirement_name, fill=TEXT_COLOR, anchor="lm",
                      font=font)
        else:
            draw.text((position[0] + 30, position[1] + LINE_SPACING // 2),
                      requirement_name, fill=HIDDEN_TEXT_COLOR, anchor="lm",
                      font=font)

    def make_header(position, learn_guide_project):
        # Static files
        make_line("CIRCUITPY", position)
        make_line(".fseventsd", (position[0] + INDENT_SIZE, position[1] + (LINE_SPACING * 1)), hidden=True,
                  triangle_icon=right_triangle)
        make_line(".metadata_never_index", (position[0] + INDENT_SIZE, position[1] + (LINE_SPACING * 2)),
                  icon=file_empty_hidden_icon,
                  hidden=True)
        make_line(".Trashes", (position[0] + INDENT_SIZE, position[1] + (LINE_SPACING * 3)),
                  icon=file_empty_hidden_icon,
                  hidden=True)
        make_line("boot_out.txt", (position[0] + INDENT_SIZE, position[1] + (LINE_SPACING * 4)))
        make_line("code.py", (position[0] + INDENT_SIZE, position[1] + (LINE_SPACING * 5)),
                  icon=file_icon)

        # dynamic files from project dir in learn guide repo
        project_files = get_files_for_project(learn_guide_project)
        rows_added = 0
        project_files_to_draw = []
        project_folders_to_draw = []
        for cur_file in project_files:
            if "." in cur_file[-5:]:
                cur_extension = cur_file.split(".")[-1]
                if cur_extension in SHOWN_FILETYPES:
                    if cur_file != "main.py":
                        project_files_to_draw.append(cur_file)
            else:
                project_folders_to_draw.append(cur_file)

        try:
            project_files_to_draw.remove("code.py")
        except ValueError:
            pass


        for i, file in enumerate(project_files_to_draw):
            make_line(file, (position[0] + INDENT_SIZE, position[1] + (LINE_SPACING * (6 + i ))))
            rows_added += 1

        for i, file in enumerate(project_folders_to_draw):
            make_line(file, (position[0] + INDENT_SIZE, position[1] + (LINE_SPACING * (6 + i + len(project_files_to_draw)))),
                      triangle_icon=right_triangle)
            rows_added += 1

        make_line("lib", (position[0] + INDENT_SIZE, position[1] + (LINE_SPACING * (5 + rows_added + 1))),
                  triangle_icon=down_triangle)

    def make_background_highlights(rows, offset=(0, 0)):
        for i in range(rows):
            if i % 2 == 0:
                draw.rectangle([
                    (0 + offset[0], i * LINE_SPACING + offset[1]),
                    (OUT_WIDTH - offset[0], (i + 1) * LINE_SPACING + offset[1])],
                    fill=HIGHLIGHT_ROW_COLOR)
            else:
                draw.rectangle([
                    (0 + offset[0], i * LINE_SPACING + offset[1]),
                    (OUT_WIDTH - offset[0], (i + 1) * LINE_SPACING + offset[1])],
                    fill=ROW_COLOR)

    def get_dependencies(libraries):
        package_list = set()
        file_list = set()

        libraries_to_check = list(libraries)

        while len(libraries_to_check) > 0:
            lib_name = libraries_to_check[0]
            del libraries_to_check[0]

            lib_obj = bundle_data[lib_name]
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

    def make_libraries(libraries, position):

        for i, lib_name in enumerate(libraries):
            triangle_icon = None
            if not lib_name.endswith(".mpy"):
                triangle_icon = right_triangle
            make_line(lib_name,
                      (position[0] + INDENT_SIZE * 2, position[1] + (LINE_SPACING * i)),
                      triangle_icon=triangle_icon)



    try:
        libs = get_libs_for_project(learn_guide_project)
        final_list_to_render = sort_libraries(libs)

        project_file_list = get_files_for_project(learn_guide_project)

        project_files_count = len(project_file_list)

        if "code.py" in project_file_list:
            project_files_count -= 1

        if "main.py" in project_file_list:
            project_files_count -= 1

        image_height = PADDING * 2 + 7 * LINE_SPACING + len(final_list_to_render) * LINE_SPACING + (
                    project_files_count) * LINE_SPACING
        im = Image.new("RGB", (OUT_WIDTH, image_height), "#303030")
        draw = ImageDraw.Draw(im)

        make_background_highlights(7 + len(final_list_to_render) + project_files_count,
                                   offset=(PADDING, PADDING))

        make_header((PADDING, PADDING), learn_guide_project)
        make_libraries(final_list_to_render,
                       (PADDING, PADDING + (LINE_SPACING * (7 + project_files_count))))

        im.save("generated_images/{}_files.png".format(learn_guide_project))
    except SyntaxError as e:
        print(e)
        traceback.print_exc()
        print("SyntaxError finding imports for {}".format(learn_guide_project))

#print(get_learn_guide_cp_projects())

for cp_project in get_learn_guide_cp_projects():
    print("making screenshot for: {}".format(cp_project))
    generate_requirement_image(cp_project)
