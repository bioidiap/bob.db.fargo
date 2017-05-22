#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 24 Apr 09:35:40 CEST 2017

""" Run face cropping on the FARGO database (%(version)s) 

Usage:
  %(prog)s --imagesdir=<path> --posdir=<path> --croppeddir=<path>
           [--mod=<string>] [--protocol=<string>]
           [--log=<string>] [--gridcount] 
           [--verbose ...] [--plot]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -i, --imagesdir=<path>    Where the face images are stored.
  -p, --posdir=<path>       The position of the eyes.
  -c, --croppeddir=<path>    Where to store results.
      --mod=<string>        The modality (RGB or NIR) [default: RGB] 
      --protocol=<string>   The protocol (MC, UD or UO) [default: MC].
  -l, --log=<string>        Log filename [default: log_face_detect.txt]
  -G, --gridcount           Display the number of objects and exits.
  -v, --verbose             Increase the verbosity (may appear multiple times).
  -P, --plot                Show some stuff

Example:

  To run the face cropping process

    $ %(prog)s --imagesdir path/to/database --posdir path/to/eyes --croppeddir path/to/cropped

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

from bob.bio.face.preprocessor import FaceCrop

import gridtk

def main(user_input=None):
  """
  
  Main function to crop faces in FARGO frontal images 

  """

  # Parse the command-line arguments
  if user_input is not None:
      arguments = user_input
  else:
      arguments = sys.argv[1:]

  prog = os.path.basename(sys.argv[0])
  completions = dict(prog=prog, version=version,)
  args = docopt(__doc__ % completions,argv=arguments,version='Face cropping (%s)' % version,)

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
  protocol = 'public_' + args['--protocol'] + '_' + args['--mod']
  objs = db.objects(protocol=protocol, groups=['world', 'dev', 'eval'])

  # if we are on a grid environment, just find what I have to process.
  if os.environ.has_key('SGE_TASK_ID'):
    pos = int(os.environ['SGE_TASK_ID']) - 1
    if pos >= len(objs):
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, len(objs))
    objs = [objs[pos]]

  if args['--gridcount']:
    print len(objs)
    sys.exit()

  # counters
  image_counter = 0

  # the face cropper
  CROPPED_IMAGE_HEIGHT = 64
  CROPPED_IMAGE_WIDTH = 64 
  RIGHT_EYE_POS = (CROPPED_IMAGE_HEIGHT // 5, CROPPED_IMAGE_WIDTH // 4 - 1)
  LEFT_EYE_POS = (CROPPED_IMAGE_HEIGHT // 5, CROPPED_IMAGE_WIDTH // 4 * 3)
  face_cropper = FaceCrop(cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
                                              cropped_positions={'leye': LEFT_EYE_POS, 'reye': RIGHT_EYE_POS},
                                              color_channel='rgb',
                                              dtype='uint8'
                                              )

  # === LET'S GO ===
  for image in objs:

    filename = os.path.join(args['--imagesdir'], image.path)
    filename += '.png'
    pos_filename = os.path.join(args['--posdir'], image.path)
    pos_filename += '.pos'
    
    if not os.path.isfile(pos_filename):
      logger.warn("pos file for {0} does not exists".format(image.path))
      continue
    
    logger.info("Cropping face in {0}".format(image.path))
    face_image = bob.io.base.load(filename) 

    # load pos file
    eyesfiles = open(pos_filename, 'r')
    eyes = eyesfiles.readline()
    reyex, reyey, leyex, leyey = eyes.split()
    eyes={'reye' : (int(reyey), int(reyex)), 'leye' : (int(leyey), int(leyex))} 

    cropped = face_cropper(face_image, annotations=eyes)
    if bool(args['--plot']):
      from matplotlib import pyplot
      pyplot.imshow(numpy.rollaxis(numpy.rollaxis(cropped, 2),2))
      pyplot.show()
    
    cropped_filename = os.path.join(args['--croppeddir'], image.path)
    cropped_filename += '.png'
   
    if not os.path.isdir(os.path.dirname(cropped_filename)):
      os.makedirs(os.path.dirname(cropped_filename))

    bob.io.base.save(cropped, cropped_filename)

    image_counter += 1 

  logger.info("{0} faces were not detected (out of {1})".format(no_face_detected, image_counter))
  logfile.close()
