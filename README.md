# NuScenes Visualization tool

This is [mayavi](https://github.com/enthought/mayavi) based 3D visualization tool for NuScenes dataset. As of now, it supports lyft's level 5 dataset, I'll extend support for actual nuscenes dataset later on.

## Demo


## Requirements

* mayavi (follow installation instructions from [here](https://github.com/enthought/mayavi#installation)
* [lyft dataset SDK](https://github.com/lyft/nuscenes-devkit/)


## Instructions

### lyft level 5 dataset visualization

#### Required data directory structure

This tool uses lyft dataset sdk, which expects data root directory in the following format:

```
    dataroot/
        - images/
        - lidar/
        - maps/
        - data/          <----- contains json files
```

if you don't want to rename the given directories, use softlinks like this:

```
mkdir dataroot
ln -s /full_path_to_original_root_directory/train_images dataroot/images
ln -s /full_path_to_original_root_directory/train_lidar dataroot/lidar
ln -s /full_path_to_original_root_directory/train_maps dataroot/maps
ln -s /full_path_to_original_root_directory/train_data dataroot/data
```

Once you have the required directory structure present in `dataroot` folder, we are ready to visualize our dataset.

### let's run the visualization script


* To plot samples one by one, iterating over `lyftdata.sample`:
```
python lyft_viz.py -d ./dataroot/
```

* To plot sample of any specific index (say 15th) in `lyftdata.sample` list:
```
python lyft_viz.py -d ./dataroot/ -i 15
```



## References

* https://github.com/hengck23/didi-udacity-2017
* https://github.com/kuixu/kitti_object_vis
* https://github.com/enthought/mayavi#installation
* https://github.com/lyft/nuscenes-devkit/
