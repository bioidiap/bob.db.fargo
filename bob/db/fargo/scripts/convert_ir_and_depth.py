#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 21 Nov 08:25:54 CET 2016

"""Image conversion for the FARGO NIR and depth channels (%(version)s)

Usage:
  %(prog)s [--imagesdir=<path>] [--verbose ...] 

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -v, --verbose             Show info.
  -i, --imagesdir=<path>    Where to store saved images.

Example:

  To run the image conversion process

    $ %(prog)s --imagesdir path/to/database

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

def main(user_input=None):
  """
  
  Main function to convert NIR and depth images from int16 to uint8.

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
      version='Image conversion (%s)' % version,
      )

  # if the user wants more verbosity, lowers the logging level
  if args['--verbose'] == 1: logging.getLogger("extract_log").setLevel(logging.INFO)
  elif args['--verbose'] >= 2: logging.getLogger("extract_log").setLevel(logging.DEBUG)

  if args['--imagesdir'] is None:
    logger.warning("You should provide a valid path to the data")
    sys.exit()

  base_dir = args['--imagesdir']

  # go through the subjects 
  for subject in os.listdir(base_dir):
    if not os.path.isdir(os.path.join(args['--imagesdir'], subject)):
      logger.warn("Please provide a valid folder for the images")
      sys.exit()

    sessions = ['controlled', 'dark', 'outdoor']
    # small hack to process FdV subjects ...
    if int(subject) >= 129:
      sessions = ['fdv']

    for session in sessions: 
      session_dir = os.path.abspath(os.path.join(base_dir, subject, session))
      
      for condition in ['SR300-laptop', 'SR300-mobile']:
        
        for recording in ['0', '1']:
          logger.info("===== Subject {0}, session {1}, device {2}, recording {3} ...".format(subject, session, condition, recording))

          # load data, convert and save back
          for i in range(10):
            
            ir_data_file = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'ir', '{:0>2d}.hdf5'.format(i))
            ir_data_file_int16 = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'ir', '{:0>2d}.int16.hdf5'.format(i))
            ir_data = bob.io.base.load(ir_data_file)
            bob.io.base.save(ir_data, ir_data_file_int16)
            bob.io.base.save(ir_data.astype('uint8'), ir_data_file)
            
            depth_data_file = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'depth', '{:0>2d}.hdf5'.format(i))
            depth_data_file_int16 = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'depth', '{:0>2d}.int16.hdf5'.format(i))
            depth_data = bob.io.base.load(depth_data_file)
            bob.io.base.save(depth_data, depth_data_file_int16)
            bob.io.base.save(depth_data.astype('uint8'), depth_data_file)
