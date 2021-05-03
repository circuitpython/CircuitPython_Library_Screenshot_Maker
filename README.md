<!--
SPDX-FileCopyrightText: 2021 foamyguy

SPDX-License-Identifier: MIT
-->

This folder contains scripts that can be run to create requirement screenshots for all of the learn guide projects

To use the scripts you must set `LEARN_GUIDE_REPO` inside of `get_imports.py` to point to the location of learn guide repo.

default value is `"../../Adafruit_Learning_System_Guides/"`

One directory above the root of this repo.

With that pointed at a learn guide repo you can run:

```
python create_requirement_images.py
```
It will create images in the `generated_images` directory.
