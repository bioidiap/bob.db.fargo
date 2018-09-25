#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 24 Apr 09:35:40 CEST 2017

""" Run face detection on the FARGO database (%(version)s) 

Usage:
  %(prog)s --imagesdir=<path> --posdir=<path> 
           [--log=<string>] [--gridcount] 
           [--verbose ...] [--plot]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -i, --imagesdir=<path>    Where the face images are stored.
  -p, --posdir=<path>       Where to store results.
  -l, --log=<string>        Log filename [default: log_face_detect.txt]
  -G, --gridcount           Display the number of objects and exits.
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
import math

import bob.io.base
import bob.io.image
import bob.bio.face
import bob.db.fargo
import bob.ip.facedetect
import bob.ip.draw

import gridtk

def filter_for_sge_task(l):
  '''Breaks down a list of objects as per SGE task requirements'''

  # identify which task I am running on
  task_id = int(os.environ['SGE_TASK_ID'])
  logger.debug('SGE_TASK_ID=%d' % task_id)
  task_first = int(os.environ['SGE_TASK_FIRST'])
  logger.debug('SGE_TASK_FIRST=%d' % task_first)
  task_last = int(os.environ['SGE_TASK_LAST'])
  logger.debug('SGE_TASK_LAST=%d' % task_last)
  task_step = int(os.environ['SGE_TASK_STEPSIZE'])
  logger.debug('SGE_TASK_STEPSIZE=%d' % task_step)

  # build a list of tasks, like the SGE manager has
  tasks = list(range(task_first, task_last+1, task_step))

  # creates an array with the limits of each task
  length = len(l)
  limits = list(range(0, length, int(math.ceil(float(length)/len(tasks)))))

  # get the index of the slot for the given task id
  task_index = tasks.index(task_id)

  # yields only the elements for the current slot
  if task_id != tasks[-1]: # not the last
    logger.info('[SGE task %d/%d] Returning entries %d:%d out of %d samples',
        task_index+1, len(tasks), limits[task_index], limits[task_index+1],
        len(l))
    return l[limits[task_index]:limits[task_index+1]]
  else: # it is the last
    logger.info('[SGE: task %d/%d] Returning entries %d:%d out of %d samples',
        task_index+1, len(tasks), limits[task_index], len(l), len(l))
    return l[limits[task_index]:]


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

  # get the objects to process
  protocols = ['pos_pitch', 'pos_yaw']
  db = bob.db.fargo.Database()
  objs = []
  for p in protocols:
    objs += db.objects(protocol=p, groups=['world', 'dev', 'eval'])

  # if we are on a grid environment, just find what I have to process.
  if 'SGE_TASK_ID' in os.environ:
    objs = filter_for_sge_task(objs)

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

