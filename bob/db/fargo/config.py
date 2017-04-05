#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Fri 23 Dec 11:37:33 CET 2016

#!/usr/bin/env python

from bob.db.fargo import Database

fargo_images_directory = "/idiap/project/fargo/database/images_public/"
fargo_annotations_directory = "/idiap/project/fargo/database/eyes_center_public/"

database_public_MC_RGB = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
    annotation_directory=fargo_annotations_directory, 
    protocol="public_MC_RGB"
)
database_public_UD_RGB = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
    annotation_directory=fargo_annotations_directory, 
    protocol="public_UD_RGB"
)
database_public_UO_RGB = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
    annotation_directory=fargo_annotations_directory, 
    protocol="public_UO_RGB"
)
database_public_MC_NIR = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
    annotation_directory=fargo_annotations_directory, 
    protocol="public_MC_NIR"
)
database_public_UD_NIR = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
    annotation_directory=fargo_annotations_directory, 
    protocol="public_UD_NIR"
)
database_public_UO_NIR = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
    annotation_directory=fargo_annotations_directory, 
    protocol="public_UO_NIR"
)
database_public_MC_depth = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
    annotation_directory=fargo_annotations_directory, 
    protocol="public_MC_depth"
)
database_public_UD_depth = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
    annotation_directory=fargo_annotations_directory, 
    protocol="public_UD_depth"
)
database_public_UO_depth = Database(
    original_directory=fargo_images_directory,
    annotation_directory=fargo_annotations_directory, 
    original_extension=".png",
    protocol="public_UO_depth"
)

database_public_MC_color_almost_frontal = Database(
    original_directory='/idiap/project/fargo/database/images_pose_clusters',
    annotation_directory=None, 
    original_extension=".png",
    protocol="public_MC_color_almost_frontal"
)

