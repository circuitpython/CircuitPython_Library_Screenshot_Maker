<!--
SPDX-FileCopyrightText: 2021 foamyguy

SPDX-License-Identifier: MIT
-->

This folder contains scripts that can be run to create requirement screenshots for all of the learn guide projects

To use the scripts you must set the environment `LEARN_GUIDE_REPO` to point to the location of learn guide repo.  It must end with a trailing slash.

The default value is `"../Adafruit_Learning_System_Guides/"`, one directory above the root of this repo.

With that pointed at a learn guide repo you can run:

```
python3 create_requirement_images.py
```
It will create images in the `generated_images` directory.

### Generate Single Learn Guide Image

```shell
python3 create_requirement_images.py learn --guide [Learn Guide Name]
# OR
python3 create_requirement_images.py learn -g [Learn Guide Name]
```

### Generate Single Library Bundle Example Image
```shell
python3 create_requirement_images.py bundle [path to example].py
# e.g.
python3 create_requirement_images.py bundle Adafruit_CircuitPythonBundle/libraries/helpers/wiz/wiz_buttons_controller.py
```

### Help Command
The help command will list all possible commands and arguments.

```shell
python3 create_requirement_images.py --help
```
