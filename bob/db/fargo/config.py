#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Fri 23 Dec 11:37:33 CET 2016

#!/usr/bin/env python

from bob.db.fargo import Database

fargo_images_directory = "/idiap/project/fargo/database/images_public/"

# Here are the eyes center derived from the annotations coming with the DB
# You need to change this folder when you have eyes center from other sources
# - from face detection
# - from landmark detection

# EYES FROM ORIGINAL LANDMARKS
fargo_annotations_directory = "/idiap/project/fargo/database/eyes_center_public/"
# EYES FROM BOB FACE DETECTION
#fargo_annotations_directory = "/idiap/project/fargo/database/eyes_center_facedetect/"

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

# ===== POSE VARYING YAW AND PITCH ONLY =====

database_pos_pitch = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch"
)

database_pos_yaw = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw"
)


# ===== POSE VARYING FACE AUTHENTICATION =====

# MC-RGB
database_pos_pitch_small_MC_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_small_MC_RGB"
)
database_pos_pitch_bottom_MC_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_bottom_MC_RGB"
)
database_pos_pitch_top_MC_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_top_MC_RGB"
)
database_pos_yaw_small_MC_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_small_MC_RGB"
)
database_pos_yaw_left_MC_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_left_MC_RGB"
)
database_pos_yaw_right_MC_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_right_MC_RGB"
)

# UD-RGB
database_pos_pitch_small_UD_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_small_UD_RGB"
)
database_pos_pitch_bottom_UD_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_bottom_UD_RGB"
)
database_pos_pitch_top_UD_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_top_UD_RGB"
)
database_pos_yaw_small_UD_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_small_UD_RGB"
)
database_pos_yaw_left_UD_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_left_UD_RGB"
)
database_pos_yaw_right_UD_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_right_UD_RGB"
)

# UO-RGB
database_pos_pitch_small_UO_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_small_UO_RGB"
)
database_pos_pitch_bottom_UO_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_bottom_UO_RGB"
)
database_pos_pitch_top_UO_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_top_UO_RGB"
)
database_pos_yaw_small_UO_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_small_UO_RGB"
)
database_pos_yaw_left_UO_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_left_UO_RGB"
)
database_pos_yaw_right_UO_RGB = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_right_UO_RGB"
)

# MC-NIR 
database_pos_pitch_small_MC_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_small_MC_NIR"
)
database_pos_pitch_bottom_MC_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_bottom_MC_NIR"
)
database_pos_pitch_top_MC_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_top_MC_NIR"
)
database_pos_yaw_small_MC_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_small_MC_NIR"
)
database_pos_yaw_left_MC_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_left_MC_NIR"
)
database_pos_yaw_right_MC_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_right_MC_NIR"
)

# UD-NIR
database_pos_pitch_small_UD_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_small_UD_NIR"
)
database_pos_pitch_bottom_UD_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_bottom_UD_NIR"
)
database_pos_pitch_top_UD_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_top_UD_NIR"
)
database_pos_yaw_small_UD_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_small_UD_NIR"
)
database_pos_yaw_left_UD_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_left_UD_NIR"
)
database_pos_yaw_right_UD_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_right_UD_NIR"
)

# UO-NIR
database_pos_pitch_small_UO_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_small_UO_NIR"
)
database_pos_pitch_bottom_UO_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_bottom_UO_NIR"
)
database_pos_pitch_top_UO_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_pitch_top_UO_NIR"
)
database_pos_yaw_small_UO_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_small_UO_NIR"
)
database_pos_yaw_left_UO_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_left_UO_NIR"
)
database_pos_yaw_right_UO_NIR = Database(
    original_directory=fargo_images_directory,
    annotation_directory=None, 
    original_extension=".png",
    protocol="pos_yaw_right_UO_NIR"
)

