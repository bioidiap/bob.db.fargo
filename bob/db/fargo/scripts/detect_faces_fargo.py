#!/usr/bin/env python
# encoding: utf-8

""" Run face detection on the FARGO database (%(version)s) 

Usage:
  %(prog)s --imagesdir=<path> --posdir=<path> 
           [--mod=<string>] [--protocol=<string>]
           [--log=<string>] [--gridcount] 
           [--verbose ...] [--plot] [--facedetect=<string>]

Options:
  -h, --help                  Show this screen.
  -V, --version               Show version.
  -i, --imagesdir=<path>      Where the face images are stored.
  -p, --posdir=<path>         Where to store results.
      --mod=<string>          The modality (RGB or NIR) [default: RGB] 
      --protocol=<string>     The protocol (MC, UD or UO) [default: MC].
  -l, --log=<string>          Log filename [default: log_face_detect.txt]
  -G, --gridcount             Display the number of objects and exits.
  -v, --verbose               Increase the verbosity (may appear multiple times).
  -P, --plot                  Show some stuff
      --facedetect=<string>   Face detection algorithm [default: bob]

Example:

  To run the face detection process

    $ %(prog)s --imagesdir path/to/database

See '%(prog)s --help' for more information.

"""
from __future__ import print_function

import os
import sys
import pkg_resources

import logging
__logging_format__='[%(levelname)s] %(message)s'
logging.basicConfig(format=__logging_format__)
logger = logging.getLogger("face_detect_log")

from docopt import docopt

version = pkg_resources.require('bob.db.fargo')[0].version

import numpy

import bob.io.base
import bob.io.image
import bob.bio.face
import bob.db.fargo
import bob.ip.facedetect
import bob.ip.draw

import gridtk

def main(user_input=None):
  """
  
  Main function to detect faces in FARGO frontal images 

  """

  # Parse the command-line arguments
  if user_input is not None:
      arguments = user_input
  else:
      arguments = sys.argv[1:]

  prog = os.path.basename(sys.argv[0])
  completions = dict(prog=prog, version=version,)
  args = docopt(__doc__ % completions,argv=arguments,version='Face detector (%s)' % version,)

  # if the user wants more verbosity, lowers the logging level
  if args['--verbose'] == 1: logging.getLogger("face_detect_log").setLevel(logging.INFO)
  elif args['--verbose'] >= 2: logging.getLogger("face_detect_log").setLevel(logging.DEBUG)

  # log file to record errors ...
  logfile = open(args['--log'], 'a')

  # check user input
  if not (args['--protocol'] == 'MC' or args['--protocol'] == 'UD' or args['--protocol'] == 'UO'): 
    logger.warning("Please provide a valid protocol name, {0} is not !".format(args['--protocol']))
    sys.exit()
  if not (args['--mod'] == 'RGB' or args['--mod'] == 'NIR'): 
    logger.warning("Please provide a valid modality, {0} is not !".format(args['--mod']))
    sys.exit()
  if not (args['--facedetect'] == 'bob' or args['--facedetect'] == 'dlib' or args['--facedetect'] == 'mtcnn'): 
    logger.warning("Please provide a valid facedetector, {0} is not !".format(args['--mod']))
    sys.exit()

  if args['--facedetect'] == 'bob':
    import bob.ip.facedetect
  if args['--facedetect'] == 'dlib':
    import bob.ip.dlib
  if args['--facedetect'] == 'mtcnn':
    import bob.ip.mtcnn

  # get the modality and the channel
  if args['--mod'] == 'RGB':
    modality = 'RGB'
    channel = 'color'
  if args['--mod'] == 'NIR':
    modality = 'NIR'
    channel = 'ir'

  db = bob.db.fargo.Database()
  protocol = 'public_' + args['--protocol'] + '_' + args['--mod']
  objs = db.objects(protocol=protocol, groups=['world', 'dev', 'eval'])

  # if we are on a grid environment, just find what I have to process.
  pos = 0
  if sys.version_info[0] < 3:
    if os.environ.has_key('SGE_TASK_ID'):
      pos = int(os.environ['SGE_TASK_ID']) - 1
      if pos >= len(objs):
        raise RuntimeError ("Grid request for job {} on a setup with {} jobs".format(pos, len(objs)))
      objs = [objs[pos]]
  else:
    if 'SGE_TASK_ID' in os.environ:
      pos = int(os.environ['SGE_TASK_ID']) - 1
      if pos >= len(objs):
        raise RuntimeError ("Grid request for job {} on a setup with {} jobs".format(pos, len(objs)))
      objs = [objs[pos]]

  if args['--gridcount']:
    print(len(objs))
    sys.exit()

  # counters
  image_counter = 0
  no_face_detected = 0

  for image in objs:

    filename = os.path.join(args['--imagesdir'], image.path)
    filename += '.png'
    pos_filename = os.path.join(args['--posdir'], image.path)
    pos_filename += '.pos'
    
    if os.path.isfile(pos_filename):
      logger.warn("pos file for {0} already exists".format(image.path))
      continue
    
    logger.info("Detecting face in {0}".format(image.path))
    
    face_image = bob.io.base.load(filename) 
    
    # bob.ip.facedetect
    if args['--facedetect'] == 'bob':
      bounding_box, quality = bob.ip.facedetect.detect_single_face(face_image)
      if bounding_box is None:
        logger.warn("No face detected in {0}".format(image.path))
        logfile.write("No face detected in {0}".format(image.path))
        no_face_detected += 1
        continue
      eyes = bob.ip.facedetect.expected_eye_positions(bounding_box, padding = None)
      reyex = int(eyes['reye'][1])
      reyey = int(eyes['reye'][0])
      leyex = int(eyes['leye'][1])
      leyey = int(eyes['leye'][0])
    
    # bob.ip.dlib
    if args['--facedetect'] == 'dlib':
      landmarks = bob.ip.dlib.DlibLandmarkExtraction(bob_landmark_format=True)(face_image)
      if landmarks is None:
        leyex = leyey = reyex = reyey = 0
      else:
        # warning: left and right eyes are swapped according to dlib
        leyex = int(landmarks['reye'][1])
        leyey = int(landmarks['reye'][0])
        reyex = int(landmarks['leye'][1])
        reyey = int(landmarks['leye'][0])

    # bob.ip.mtcnn
    if args['--facedetect'] == 'mtcnn':
      bounding_box, landmarks = bob.ip.mtcnn.FaceDetector().detect_single_face(face_image)
      reyex = int(landmarks['reye'][1])
      reyey = int(landmarks['reye'][0])
      leyex = int(landmarks['leye'][1])
      leyey = int(landmarks['leye'][0])


    if reyex == 0 or reyey == 0 or leyex == 0 or leyey == 0:
      logger.warn("No face detected in {0}".format(image.path))
      logfile.write("No face detected in {0}".format(image.path))
      no_face_detected += 1
      
      # write dummy bbox, otherwise bob.bio.face's verify fails ...
      # dummy eyes will be centered in the image
      reyex = 0.4*face_image.shape[0]
      reyey = 0.5*face_image.shape[1]
      leyex = 0.6*face_image.shape[0]
      reyey = 0.5*face_image.shape[1]
      if not os.path.isdir(os.path.dirname(pos_filename)):
        os.makedirs(os.path.dirname(pos_filename))
      eyes_file = open(pos_filename, 'w')
      eyes_file.write('{0} {1} {2} {3}'.format(reyex, reyey, leyex, leyey))
      eyes_file.close()

      continue

    if bool(args['--plot']):
      from matplotlib import pyplot
      if modality == 'RGB':
        #bob.ip.draw.box(face_image, bounding_box.topleft, bounding_box.size, color=(255, 0, 0))
        bob.ip.draw.cross(face_image, (reyey, reyex), 10, (0, 255, 0))
        bob.ip.draw.cross(face_image, (leyey, leyex), 10, (0, 255, 0))
        pyplot.imshow(numpy.rollaxis(numpy.rollaxis(face_image, 2),2))
      else: 
        #bob.ip.draw.box(face_image, bounding_box.topleft, bounding_box.size, color=(255))
        bob.ip.draw.cross(face_image, (reyey, reyex), 5, (255))
        bob.ip.draw.cross(face_image, (leyey, leyex), 5, (255))
        pyplot.imshow(face_image, cmap='gray')
      pyplot.show()
    

    if not os.path.isdir(os.path.dirname(pos_filename)):
      os.makedirs(os.path.dirname(pos_filename))
    eyes_file = open(pos_filename, 'w')
    eyes_file.write('{0} {1} {2} {3}'.format(reyex, reyey, leyex, leyey))
    eyes_file.close()

    image_counter += 1 

  logger.info("{0} faces were not detected (out of {1})".format(no_face_detected, image_counter))
  logfile.close()

