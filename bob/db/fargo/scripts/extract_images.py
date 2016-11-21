#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 21 Nov 08:25:54 CET 2016

"""Image extractor for the FARGO videos (%(version)s)

Usage:
  %(prog)s [--dbdir=<path>] [--imagesdir=<path>] [--verbose ...] [--plot]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -d, --dbdir=<path>        The path to the database on your disk.
  -i, --imagesdir=<path>    Where to store saved images. 
  -v, --verbose             Increase the verbosity (may appear multiple times).
  -P, --plot                Show some stuff

Example:

  To run the image extraction process

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
import natsort
import glob

import bob.io.video
import bob.io.base
import bob.io.image


def main(user_input=None):

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
  if not os.path.isdir(args['--imagesdir']):
    os.mkdir(args['--imagesdir'])


  # go through the subjects 
  for subject in os.listdir(base_dir):
    if not os.path.isdir(os.path.join(args['--imagesdir'], subject)):
      os.mkdir(os.path.join(args['--imagesdir'], subject))

    for session in ['controlled', 'dark', 'outdoor']:
      if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session)):
        os.mkdir(os.path.join(args['--imagesdir'], subject, session))
      session_dir = os.path.abspath(os.path.join(base_dir, subject, session))
      
      for condition in ['SR300-laptop', 'SR300-mobile']:
        if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session, condition)):
          os.mkdir(os.path.join(args['--imagesdir'], subject, session, condition))
        
        for recording in ['0', '1']:
          logger.info("Subject {0}, session {1}, device {2}, recording {3} ...".format(subject, session, condition, recording))

          # create directories to save the extracted data
          if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session, condition, recording)):
            os.mkdir(os.path.join(args['--imagesdir'], subject, session, condition, recording))
          if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'color')):
            os.mkdir(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'color'))
          if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'ir')):
            os.mkdir(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'ir'))
          if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'depth')):
            os.mkdir(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'depth'))

          # get the original data
          color_dir = os.path.join(session_dir, condition, recording, 'streams', 'color')
          ir_dir = os.path.join(session_dir, condition, recording, 'streams', 'ir')
          depth_dir = os.path.join(session_dir, condition, recording, 'streams', 'depth')

          # process color file 
          color_file = os.path.join(color_dir, 'color.264')
          color_stream = bob.io.video.reader(color_file)

          # get the corresponding (color) annotation file - if it exists ...
          color_annotation = os.path.join(session_dir, condition, recording, 'annotations', 'color_timestamps.txt')
          try:
            f = open(color_annotation, 'r')
            frame_index_first_landmark = int(f.readline().split()[0])
          except IOError:
            logger.warn("No annotations for this recording")
            frame_index_first_landmark = 0
          
          # used as a check, be sure that the annotated frame corresponds to the first frame
          annotated_color_file = os.path.join(session_dir, condition, recording, 'annotations', 'color', str(frame_index_first_landmark) + '.264')
          if os.path.isfile(annotated_color_file): 
            annotated_frames = bob.io.video.reader(annotated_color_file)
            for i, frame in enumerate(annotated_frames):
              if i == frame_index_first_landmark:
                annotated_frame = frame
                break
          else:
            logger.warn("No corresponding annotated frame for this recording".format(color_file))
        
          logger.info("First annotated frame -> {0}".format(frame_index_first_landmark))
          
          # now save frames every 40 ms -> every 4 frames
          saved_image_index = 0
          last_frame_index = frame_index_first_landmark + 40
          for i, frame in enumerate(color_stream):
            
            # just to check
            if os.path.isfile(annotated_color_file): 
              if i == int(frame_index_first_landmark):
                diff = frame - annotated_frame
                if not numpy.all(diff == 0):
                  logger.warn("The difference between current frame and annotated frame is not zero ...")

            toto = i - frame_index_first_landmark
            if toto % 4 == 0 and i <= last_frame_index:

              # save image
              saved_png = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'color', '{:0>2d}.png'.format(saved_image_index))
              bob.io.base.save(frame.astype('uint8'), saved_png)
            
              if bool(args['--plot']):
                from matplotlib import pyplot
                pyplot.imshow(numpy.rollaxis(numpy.rollaxis(frame, 2),2))
                pyplot.title('frame {0}'.format(i))
                pyplot.show()

              ir_file = os.path.join(ir_dir, '{0}.bin'.format(i))
              ir_data = numpy.fromfile(ir_file, dtype=numpy.int16).reshape(-1, 640)
              saved_ir = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'ir', '{:0>2d}.hdf5'.format(saved_image_index))
              bob.io.base.save(ir_data, saved_ir)
              
              depth_file = os.path.join(depth_dir, '{0}.bin'.format(i))
              depth_data = numpy.fromfile(depth_file, dtype=numpy.int16).reshape(-1, 640)
              saved_depth = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'depth', '{:0>2d}.hdf5'.format(saved_image_index))
              bob.io.base.save(depth_data, saved_depth)

              if bool(args['--plot']):
                from matplotlib import pyplot
                pyplot.imshow(ir_data)
                pyplot.title('ir {0}'.format(i))
                pyplot.show()
                pyplot.imshow(depth_data)
                pyplot.title('depth {0}'.format(i))
                pyplot.show()
              
              saved_image_index += 1
           
            if i > last_frame_index:
              break




