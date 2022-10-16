
EGH455 - v7 Generate V5 -with Video -Volve Close-
==============================

This dataset was exported via roboflow.com on October 6, 2022 at 8:28 AM GMT

Roboflow is an end-to-end computer vision platform that helps you
* collaborate with your team on computer vision projects
* collect & organize images
* understand unstructured image data
* annotate, and create datasets
* export, train, and deploy computer vision models
* use active learning to improve your dataset over time

It includes 3369 images.
Fire-extinguisher are annotated in Tensorflow TFRecord (raccoon) format.

The following pre-processing was applied to each image:
* Auto-orientation of pixel data (with EXIF-orientation stripping)

The following augmentation was applied to create 3 versions of each source image:
* 50% probability of horizontal flip
* 50% probability of vertical flip
* Randomly crop between 0 and 30 percent of the image
* Random rotation of between -15 and +15 degrees
* Random Gaussian blur of between 0 and 10 pixels

The following transformations were applied to the bounding boxes of each image:
* Random rotation of between -45 and +45 degrees
* Salt and pepper noise was applied to 5 percent of pixels


