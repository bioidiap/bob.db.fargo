#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Fri 23 Dec 11:37:33 CET 2016

#!/usr/bin/env python

from bob.db.fargo import Database

fargo_images_directory = "/idiap/project/fargo/databases/images_public/"
fargo_annotations_directory = "/idiap/project/fargo/databases/images_public/"

database_public_MC_RGB = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
    protocol="public_MC_RGB"
)
database_public_UD_RGB = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
    protocol="public_UD_RGB"
)
database_public_UO_RGB = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
    protocol="public_UO_RGB"
)
database_public_MC_NIR = Database(
    original_directory=fargo_images_directory,
    original_extension=".hdf5",
    protocol="public_MC_NIR"
)
database_public_UD_NIR = Database(
    original_directory=fargo_images_directory,
    original_extension=".hdf5",
    protocol="public_UD_NIR"
)
database_public_UO_NIR = Database(
    original_directory=fargo_images_directory,
    original_extension=".hdf5",
    protocol="public_UO_NIR"
)
database_public_MC_depth = Database(
    original_directory=fargo_images_directory,
    original_extension=".hdf5",
    protocol="public_MC_depth"
)
database_public_UD_depth = Database(
    original_directory=fargo_images_directory,
    original_extension=".hdf5",
    protocol="public_UD_depth"
)
database_public_UO_depth = Database(
    original_directory=fargo_images_directory,
    original_extension=".hdf5",
    protocol="public_UO_depth"
)
