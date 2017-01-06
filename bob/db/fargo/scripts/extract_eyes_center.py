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

def get_color_frame(annotation_dir):
  
  annotated_file = os.path.join(annotation_dir, '0.264')
  if os.path.isfile(annotated_file): 
    annotated_stream = bob.io.video.reader(annotated_file)
    for i, frame in enumerate(annotated_stream):
      return frame


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

  # go through the subjects 
  for subject in os.listdir(base_dir):
    if not os.path.isdir(os.path.join(args['--eyesdir'], subject)):
      os.mkdir(os.path.join(args['--eyesdir'], subject))

    sessions = ['controlled', 'dark', 'outdoor']
    # small hack to process FdV subjects ...
    if int(subject) >= 129:
      sessions = ['fdv']

    for session in sessions: 
      if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session)):
        os.mkdir(os.path.join(args['--eyesdir'], subject, session))
      session_dir = os.path.abspath(os.path.join(base_dir, subject, session))
      
      for condition in ['SR300-laptop', 'SR300-mobile']:
        if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition)):
          os.mkdir(os.path.join(args['--eyesdir'], subject, session, condition))
        
        for recording in ['0', '1']:
          logger.info("===== Subject {0}, session {1}, device {2}, recording {3} ...".format(subject, session, condition, recording))

          # create directories to save the extracted annotations 
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording)):
            os.mkdir(os.path.join(args['--eyesdir'], subject, session, condition, recording))
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'color')):
            os.mkdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'color'))
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'ir')):
            os.mkdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'ir'))
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'depth')):
            os.mkdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'depth'))

          # get the annotations data
          color_dir = os.path.join(session_dir, condition, recording, 'annotations', 'color')
          ir_dir = os.path.join(session_dir, condition, recording, 'annotations', 'ir')
          depth_dir = os.path.join(session_dir, condition, recording, 'annotations', 'depth')

          print color_dir
          frame = get_color_frame(color_dir)

          # process color annotations  - extracted image is *always* the first annotated one (I hope)
          color_file = os.path.join(color_dir, '0.pos')
          color_data = open(color_file, 'r')
          with open(color_file, "r") as c:
            keypoints = []
            for line in c:
              line = line.rstrip()
              ints = line.split()
              keypoints.append((int(ints[2]), int(ints[1])))
          
          reye_x = int(0.5 * (keypoints[0][1] + keypoints[1][1]))
          reye_y = int(0.5 * (keypoints[0][0] + keypoints[1][0]))
          leye_x = int(0.5 * (keypoints[2][1] + keypoints[3][1]))
          leye_y = int(0.5 * (keypoints[2][0] + keypoints[3][0]))
          
          if bool(args['--plot']):
            bob.ip.draw.cross(frame, (reye_y, reye_x), 4, (255,0,0)) 
            bob.ip.draw.cross(frame, (leye_y, leye_x), 4, (0,255,0)) 
            from matplotlib import pyplot
            pyplot.imshow(numpy.rollaxis(numpy.rollaxis(frame, 2),2))
            pyplot.title('Image')
            pyplot.show()

          for i in range(0, 10):
            eyes_filename = os.path.join(args['--eyesdir'], subject, session, condition, recording, 'color', '{:0>2d}.pos'.format(i))
            eyes_file = open(eyes_filename, 'w')
            eyes_file.write('{0} {1} {2} {3}'.format(reye_x, reye_y, leye_x, leye_y))
            eyes_file.close()
