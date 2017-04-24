#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 24 Apr 09:35:40 CEST 2017

""" Run face detection on the FARGO database (%(version)s) 

Usage:
  %(prog)s --imagesdir=<path> --posdir=<path> 
           [--mod=<string>] [--protocol=<string>]
           [--log=<string>] [--verbose ...] [--plot]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -i, --imagesdir=<path>    Where the face images are stored.
  -p, --posdir=<path>       Where to store results.
      --mod=<string>        The modality (RGB or NIR) [default: RGB] 
      --protocol=<string>   The protocol (MC, UD or UO) [default: MC].
  -l, --log=<string>        Log filename [default: log_face_detect.txt]
  -v, --verbose             Increase the verbosity (may appear multiple times).
  -P, --plot                Show some stuff

Example:

  To run the face detection process

    $ %(prog)s --imagesdir path/to/database

See '%(prog)s --help' for more information.

"""

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

  # get the modality and the channel
  if args['--mod'] == 'RGB':
    modality = 'RGB'
    channel = 'color'
  if args['--mod'] == 'NIR':
    modality = 'NIR'
    channel = 'ir'

  db = bob.db.fargo.Database()
  objs = db.objects(protocol='public_MC_RGB', groups=['world', 'dev', 'eval'])

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
    bounding_box, quality = bob.ip.facedetect.detect_single_face(face_image)
    eyes = bob.ip.facedetect.expected_eye_positions(bounding_box, padding = None)
    
    reyex = int(eyes['reye'][1])
    reyey = int(eyes['reye'][0])
    leyex = int(eyes['leye'][1])
    leyey = int(eyes['leye'][0])

    if reyex == 0 or reyey == 0 or leyex == 0 or leyey == 0:
      logger.warn("No face detected in {0}".format(image.path))
      logfile.write("No face detected in {0}".format(image.path))
      no_face_detected += 1

    if bool(args['--plot']):
      from matplotlib import pyplot
      bob.ip.draw.box(face_image, bounding_box.topleft, bounding_box.size, color=(255, 0, 0))
      bob.ip.draw.cross(face_image, (reyey, reyex), 10, (0, 255, 0))
      bob.ip.draw.cross(face_image, (leyey, leyex), 10, (0, 255, 0))
      pyplot.imshow(numpy.rollaxis(numpy.rollaxis(face_image, 2),2))
      pyplot.show()
    

    if not os.path.isdir(os.path.dirname(pos_filename)):
      os.makedirs(os.path.dirname(pos_filename))
    eyes_file = open(pos_filename, 'w')
    eyes_file.write('{0} {1} {2} {3}'.format(reyex, reyey, leyex, leyey))
    eyes_file.close()

    image_counter += 1 

  logger.info("{0} faces were not detected (out of {1})".format(no_face_detected, image_counter))
  logfile.close()

