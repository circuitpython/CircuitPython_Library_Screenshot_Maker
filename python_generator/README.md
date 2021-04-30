This folder contains scripts that can be run to create requirement screenshots for all of the learn guide projects

To use the scripts you must set `LEARN_GUIDE_REPO` to point to the learn guide repo.

Then you can run

```
python get_bundle_data.py
```
to download `latest_bundle_data.json`

Once this file is present run
```
python create_requirement_images.py
```
It will create images in the `generated_images` directory.
