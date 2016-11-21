#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 21 Nov 08:25:54 CET 2016

"""Image extractor for the FARGO videos (%(version)s)

Usage:
  %(prog)s [--dbdir=<path>] [--verbose ...] [--plot]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -d, --dbdir=<path>        The path to the database on your disk.
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

  # go through the subjects 
  for subject in os.listdir(base_dir):
    logger.info("Processing subject {0}".format(subject))
   
    for session in ['controlled', 'dark', 'outdoor']:
      session_dir = os.path.abspath(os.path.join(base_dir, subject, session))
      for condition in ['SR300-laptop', 'SR300-mobile']:
        for recording in ['0', '1']:

          color_dir = os.path.join(session_dir, condition, recording, 'streams', 'color')
          ir_dir = os.path.join(session_dir, condition, recording, 'streams', 'ir')
          depth_dir = os.path.join(session_dir, condition, recording, 'streams', 'depth')

          # parse color, depth, and ir files
          color_files = natsort.natsorted(glob.glob(os.path.join(color_dir, '*.264')))
          ir_files = natsort.natsorted(glob.glob(os.path.join(ir_dir, '*.bin')))
          depth_files = natsort.natsorted(glob.glob(os.path.join(depth_dir, '*.bin')))

          #for color_frame in color_files:
          #  print color_frame
          for ir_frame in ir_files:
            print ir_frame 


