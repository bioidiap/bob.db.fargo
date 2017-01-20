#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 21 Nov 08:25:54 CET 2016

"""Eyes center extractor for the FARGO images (%(version)s)

Usage:
  %(prog)s [--dbdir=<path>] [--eyesdir=<path>] 
           [--verbose ...] [--plot]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -d, --dbdir=<path>        The path to the database on your disk.
  -i, --eyesdir=<path>      Where to store saved images.
  -l, --log=<string>        Log filename [default: logs.txt]
  -v, --verbose             Increase the verbosity (may appear multiple times).
  -P, --plot                Show some stuff

Example:

  To get the eyes center, do

    $ %(prog)s --dbdir path/to/database

See '%(prog)s --help' for more information.

"""

import os
import sys
import pkg_resources

import logging
__logging_format__='[%(levelname)s] %(message)s'
logging.basicConfig(format=__logging_format__)
logger = logging.getLogger("extract_log")

from docopt import docopt

version = pkg_resources.require('bob.db.fargo')[0].version

import numpy

import bob.io.base
import bob.io.image
import bob.io.video

import bob.ip.draw
import bob.ip.color

def get_color_frame(annotation_dir):
  
  annotated_file = os.path.join(annotation_dir, '0.264')
  if os.path.isfile(annotated_file): 
    annotated_stream = bob.io.video.reader(annotated_file)
    for i, frame in enumerate(annotated_stream):
      return frame


def get_data_frame(annotation_dir):

  bin_file = os.path.join(annotation_dir, '0.bin')
  if os.path.isfile(bin_file): 
    bin_data = numpy.fromfile(bin_file, dtype=numpy.int16).reshape(-1, 640)
  return bin_data


def get_eyes_center(annotation_file):

  with open(annotation_file, "r") as c:
    keypoints = {}
    for line in c:
      line = line.rstrip()
      ints = line.split()
      keypoints[ints[0]] = ((int(ints[2]), int(ints[1])))
    
    if '1' not in keypoints.keys() or '2' not in keypoints.keys() or '3' not in keypoints.keys() or '4' not in keypoints.keys():
      logger.warn('incomplete annotations in {0} ... '.format(annotation_file))
      return 0,0,0,0
    else: 
      reye_x = int(0.5 * (keypoints['1'][1] + keypoints['2'][1]))
      reye_y = int(0.5 * (keypoints['1'][0] + keypoints['2'][0]))
      leye_x = int(0.5 * (keypoints['3'][1] + keypoints['4'][1]))
      leye_y = int(0.5 * (keypoints['3'][0] + keypoints['4'][0]))
     
      return reye_x, reye_y, leye_x, leye_y


def plot_eyes_center(frame, positions):
 
  reye_x = positions[0]
  reye_y = positions[1]
  leye_x = positions[2]
  leye_y = positions[3]
  if frame.dtype == 'int16':
    frame = frame.astype('uint8')
    frame = bob.ip.color.gray_to_rgb(frame) 
  bob.ip.draw.cross(frame, (reye_y, reye_x), 4, (255,0,0)) 
  bob.ip.draw.cross(frame, (leye_y, leye_x), 4, (0,255,0)) 
  from matplotlib import pyplot
  pyplot.imshow(numpy.rollaxis(numpy.rollaxis(frame, 2),2))
  pyplot.title('Image')
  pyplot.show()
  


def main(user_input=None):
  """
  
  Main function to extract images from recorded streams.

  """

  # Parse the command-line arguments
  if user_input is not None:
      arguments = user_input
  else:
      arguments = sys.argv[1:]

  prog = os.path.basename(sys.argv[0])
  completions = dict(
          prog=prog,
          version=version,
          )
  args = docopt(
      __doc__ % completions,
      argv=arguments,
      version='Image extractor (%s)' % version,
      )

  # if the user wants more verbosity, lowers the logging level
  if args['--verbose'] == 1: logging.getLogger("extract_log").setLevel(logging.INFO)
  elif args['--verbose'] >= 2: logging.getLogger("extract_log").setLevel(logging.DEBUG)

  if args['--dbdir'] is None:
    logger.warning("You should provide a valid path to the data")
    sys.exit()

  base_dir = args['--dbdir']
  if not os.path.isdir(args['--eyesdir']):
    os.mkdir(args['--eyesdir'])

  logfile = open('annotations.txt', 'w')

  # go through the subjects 
  for subject in os.listdir(base_dir):

    sessions = ['controlled', 'dark', 'outdoor']
    # small hack to process FdV subjects ...
    if int(subject) >= 129:
      sessions = ['fdv']

    for session in sessions: 
      session_dir = os.path.abspath(os.path.join(base_dir, subject, session))
      
      for condition in ['SR300-laptop', 'SR300-mobile']:
        
        for recording in ['0', '1']:
          logger.info("===== Subject {0}, session {1}, device {2}, recording {3} ...".format(subject, session, condition, recording))

          # create directories to save the extracted annotations 
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording)):
            os.makedirs(os.path.join(args['--eyesdir'], subject, session, condition, recording))
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'color')):
            os.makedirs(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'color'))
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'ir')):
            os.makedirs(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'ir'))
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'depth')):
            os.makedirs(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'depth'))

          # get the annotations data
          color_dir = os.path.join(session_dir, condition, recording, 'annotations', 'color')
          ir_dir = os.path.join(session_dir, condition, recording, 'annotations', 'ir')
          depth_dir = os.path.join(session_dir, condition, recording, 'annotations', 'depth')

          # process color annotations  - extracted image is *always* the first annotated one (I hope)
          color_file = os.path.join(color_dir, '0.pos')
          try:
            reye_x, reye_y, leye_x, leye_y = get_eyes_center(color_file)
            if reye_x == 0:
              logfile.write(color_file + '(incomplete)\n')
              logger.warn("{0} incomplete -> skipping !")
              continue
            if bool(args['--plot']):
              frame = get_color_frame(color_dir)
              plot_eyes_center(frame, (reye_x, reye_y, leye_x, leye_y))

            for i in range(0, 10):
              eyes_filename = os.path.join(args['--eyesdir'], subject, session, condition, recording, 'color', '{:0>2d}.pos'.format(i))
              if os.path.isfile(eyes_filename):
                logger.info('already exists in {0}'.format(color_dir))
                continue
              else:
                eyes_file = open(eyes_filename, 'w')
                eyes_file.write('{0} {1} {2} {3}'.format(reye_x, reye_y, leye_x, leye_y))
                eyes_file.close()

          except IOError:
            logger.warn("No annotations for recording {0}".format(color_dir))
            logfile.write(color_dir + '\n')
            continue

          # process NIR annotations
          ir_file = os.path.join(ir_dir, '0.pos')
          try:
            reye_x, reye_y, leye_x, leye_y = get_eyes_center(ir_file)
            if reye_x == 0:
              logfile.write(ir_file + '(incomplete)\n')
              logger.warn("{0} incomplete -> skipping !")
              continue
            if bool(args['--plot']):
              frame = get_data_frame(ir_dir)
              plot_eyes_center(frame, (reye_x, reye_y, leye_x, leye_y))

            for i in range(0, 10):
              eyes_filename = os.path.join(args['--eyesdir'], subject, session, condition, recording, 'ir', '{:0>2d}.pos'.format(i))
              if os.path.isfile(eyes_filename):
                logger.info('already exists in {0}'.format(ir_dir))
                continue
              else:
                eyes_file = open(eyes_filename, 'w')
                eyes_file.write('{0} {1} {2} {3}'.format(reye_x, reye_y, leye_x, leye_y))
                eyes_file.close()
          
          except IOError:
            logger.warn("No annotations for recording {0}".format(ir_dir))
            logfile.write(ir_dir + '\n')
            continue

          # process depth annotations
          depth_file = os.path.join(depth_dir, '0.pos')
          try:
            reye_x, reye_y, leye_x, leye_y = get_eyes_center(depth_file)
            if reye_x == 0:
              logfile.write(depth_file + '(incomplete)\n')
              logger.warn("{0} incomplete -> skipping !")
              continue
            if bool(args['--plot']):
              frame = get_data_frame(depth_dir)
              plot_eyes_center(frame, (reye_x, reye_y, leye_x, leye_y))

            eyes_filename = os.path.join(args['--eyesdir'], subject, session, condition, recording, 'depth', '{:0>2d}.pos'.format(i))
            for i in range(0, 10):
              eyes_file = open(eyes_filename, 'w')
              eyes_file.write('{0} {1} {2} {3}'.format(reye_x, reye_y, leye_x, leye_y))
              eyes_file.close()
          
          except IOError:
            logger.warn("No annotations for recording {0}".format(depth_dir))
            logfile.write(depth_dir + '\n')
            continue

  logfile.close()
