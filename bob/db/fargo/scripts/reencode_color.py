#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Wed  1 Feb 15:23:50 CET 2017


"""Reeconding color streams (%(version)s)

Usage:
  %(prog)s <datadir> [--verbose ...] 

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -v, --verbose             Show info.
  -P, --plot                Plot stuff. 

Example:

  To run the reencoding 

    $ %(prog)s path/to/database

See '%(prog)s --help' for more information.

"""

import os
import sys
import pkg_resources

import logging
__logging_format__='[%(levelname)s] %(message)s'
logging.basicConfig(format=__logging_format__)
logger = logging.getLogger("reencode_log")

from docopt import docopt

version = pkg_resources.require('bob.db.fargo')[0].version

def main(user_input=None):
  """
  
  Main function to perform reencoding

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
      version='Reencoding (%s)' % version,
      )

  # if the user wants more verbosity, lowers the logging level
  if args['--verbose'] == 1: logging.getLogger("reencode_log").setLevel(logging.INFO)
  elif args['--verbose'] >= 2: logging.getLogger("reencode_log").setLevel(logging.DEBUG)

  base_dir = args['<datadir>']

  # go through the subjects 
  #subjects = []
  #subjects_ids = range(1, 10, 1)
  #for subject in subjects_ids:
  #  subjects.append('{:0>3d}'.format(subject))
  #for subject in subjects:
  for subject in os.listdir(base_dir):
    if not os.path.isdir(os.path.join(base_dir, subject)):
      logger.warn("Please provide a valid folder for the data")
      sys.exit()

    sessions = ['controlled', 'dark', 'outdoor']
    # small hack to process FdV subjects ...
    if int(subject) >= 129:
      sessions = ['fdv']

    for session in sessions: 
      session_dir = os.path.abspath(os.path.join(base_dir, subject, session))
      
      for condition in ['SR300-laptop', 'SR300-mobile']:
        
        for recording in ['0', '1']:
          recording_dir = os.path.join(base_dir, subject, session, condition, recording)
          logger.info("===== Subject {0}, session {1}, device {2}, recording {3} ...".format(subject, session, condition, recording))

          color_stream_file = os.path.join(recording_dir, 'streams', 'color', 'color.264')
          color_stream_reencoded = os.path.join(recording_dir, 'streams', 'color', 'color.mov')
          temp_file = os.path.join(recording_dir, 'streams', 'color', 'temp.raw')
          
          if os.path.isfile(color_stream_reencoded):
            logger.debug("already done !")
            continue

          command = 'ffmpeg -loglevel panic -i ' + str(color_stream_file) + ' -f rawvideo -b 50000000 -pix_fmt yuv420p -vcodec rawvideo -s 1920x1080 -y ' + str(temp_file)
          os.system(command)
          command = 'ffmpeg -loglevel panic -f rawvideo -pix_fmt yuv420p -r 10 -s 1920x1080 -i ' + str(temp_file) + ' -y ' + str(color_stream_reencoded)
          os.system(command)
          os.remove(temp_file)
