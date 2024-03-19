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
python3 create_requirement_images.py --guide [Learn Guide Name]
# OR
python3 create_requirement_images.py -g [Learn Guide Name]
```
