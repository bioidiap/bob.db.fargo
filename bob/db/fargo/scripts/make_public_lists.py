#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Thu 22 Dec 09:00:55 CET 2016

""" Generate file lists for the different protocols of the FARGO database

Usage:
  %(prog)s [--imagesdir=<path>] 
           [--protocol=<string>] [--mod=<string>] [--scores] 
           [--verbose ...] [--plot]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -i, --imagesdir=<path>    Where the images are saved.
  -p, --protocol=<int>      The protocol (MC, UD, UO).
  -m, --mod=<int>           The used modality (RGB, NIR, depth) [default: RGB].
      --scores              If you want to generate score files.
  -v, --verbose             Increase the verbosity (may appear multiple times).
  -P, --plot                Show some stuff

Example:

  To run the generation of file list 

    $ %(prog)s --imagesdir image --set world

See '%(prog)s --help' for more information.

"""

import os
import sys
import pkg_resources

import logging
__logging_format__='[%(levelname)s] %(message)s'
logging.basicConfig(format=__logging_format__)
logger = logging.getLogger("filelist_log")

from docopt import docopt

version = pkg_resources.require('bob.db.fargo')[0].version

#import numpy

#import bob.io.base
#import bob.io.image

def build_list(image_dir, ids, channel, sessions, recordings, list_filename, enroll=False):
  """
  """
  f = open(list_filename, 'w')

  for subject in ids:
    subject = '{:0>3d}'.format(subject)
    for condition in ['SR300-laptop', 'SR300-mobile']:
      for session in sessions:
        for recording in recordings:
          subject_images_dir = os.path.join(image_dir, subject, session, condition, recording, channel)
          for image in os.listdir(subject_images_dir):
            filepath = os.path.splitext(os.path.os.path.join(subject, session, condition, recording, channel, image))[0]
            if enroll:
              f.write(filepath + ' ' + subject + ' ' + subject + '\n')
            else:
              f.write(filepath + ' ' + subject + '\n')

  f.close()

def main(user_input=None):
  """
  
  Main function to generate  protocol file lists

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
      version='List generator (%s)' % version,
      )

  # if the user wants more verbosity, lowers the logging level
  if args['--verbose'] == 1: logging.getLogger("filelist_log").setLevel(logging.INFO)
  elif args['--verbose'] >= 2: logging.getLogger("filelist_log").setLevel(logging.DEBUG)

  if args['--imagesdir'] is None:
    logger.warning("You should provide a valid path to the images")
    sys.exit()

  if not (args['--protocol'] == 'MC' or args['--protocol'] == 'UD' or args['--protocol'] == 'UO'): 
    logger.warning("Please provide a valid protocol name, {0} is not !".format(args['--protocol']))
    sys.exit()
   
  if args['--mod'] == 'RGB':
    modality = 'RGB'
    channel = 'color'
  if args['--mod'] == 'NIR':
    modality = 'NIR'
    channel = 'ir'
  if args['--mod'] == 'depth':
    modality = 'depth'
    channel = 'depth'
  if not (args['--mod'] == 'RGB' or args['--mod'] == 'NIR' or args['--mod'] == 'depth'): 
    logger.warning("Please provide a valid modality, {0} is not !".format(args['--mod']))
    sys.exit()
  
  # build the correct output dir to store file list
  basedir = 'bob/db/fargo/lists'
  lists_dir = os.path.join(basedir, 'public_' + args['--protocol'] + '_' + modality)
  if not os.path.isdir(lists_dir):
    os.makedirs(lists_dir)
  
  # world model
  logger.info("Generating WORLD list for protocol {0} in the {1} channel".format(args['--protocol'], modality))
  world_dir = os.path.join(lists_dir, 'norm') 
  list_filename = os.path.join(world_dir, 'train_world.lst')
  print os.path.dirname(list_filename)
  if not os.path.isdir(os.path.dirname(list_filename)):
    os.makedirs(os.path.dirname(list_filename))
  subjects_ids = range(1, 26, 1)
  sessions = ['controlled']
  recordings =  ['0', '1']
  build_list(args['--imagesdir'], subjects_ids, channel, sessions, recordings, list_filename)

  # development set - enrollment
  logger.info("Generating enrollment list for DEV set (protocol {0} in the {1} channel)".format(args['--protocol'], modality))
  dev_dir = os.path.join(lists_dir, 'dev')
  list_filename = os.path.join(dev_dir, 'for_models.lst')
  if not os.path.isdir(os.path.dirname(list_filename)):
    os.makedirs(os.path.dirname(list_filename))
  subjects_ids = range(26, 51, 1)
  sessions = ['controlled']
  recordings =  ['0' ]
  build_list(args['--imagesdir'], subjects_ids, channel, sessions, recordings, list_filename, True)
  
  # development set - scores
  logger.info("Generating scores list for DEV set (protocol {0} in the {1} channel)".format(args['--protocol'], modality))
  dev_dir = os.path.join(lists_dir, 'dev')
  list_filename = os.path.join(dev_dir, 'for_probes.lst')
  if not os.path.isdir(os.path.dirname(list_filename)):
    os.makedirs(os.path.dirname(list_filename))
  subjects_ids = range(26, 51, 1)
  if args['--protocol'] == 'MC':
    sessions = ['controlled']
    recordings =  ['1' ]
  if args['--protocol'] == 'UD':
    sessions = ['dark']
    recordings =  ['0', '1' ]
  if args['--protocol'] == 'UO':
    sessions = ['outdoor']
    recordings =  ['0''1' ]
  build_list(args['--imagesdir'], subjects_ids, channel, sessions, recordings, list_filename)

  # eval set - enrollment
  logger.info("Generating enrollment list for EVAL set (protocol {0} in the {1} channel)".format(args['--protocol'], modality))
  eval_dir = os.path.join(lists_dir, 'eval')
  list_filename = os.path.join(eval_dir, 'for_models.lst')
  if not os.path.isdir(os.path.dirname(list_filename)):
    os.makedirs(os.path.dirname(list_filename))
  subjects_ids = range(51, 76, 1)
  sessions = ['controlled']
  recordings =  ['0' ]
  build_list(args['--imagesdir'], subjects_ids, channel, sessions, recordings, list_filename, True)
  
  # eval set - scores
  logger.info("Generating scores list for EVAL set (protocol {0} in the {1} channel)".format(args['--protocol'], modality))
  eval_dir = os.path.join(lists_dir, 'eval')
  list_filename = os.path.join(eval_dir, 'for_probes.lst')
  if not os.path.isdir(os.path.dirname(list_filename)):
    os.makedirs(os.path.dirname(list_filename))
  subjects_ids = range(51, 76, 1)
  if args['--protocol'] == 'MC':
    sessions = ['controlled']
    recordings =  ['1' ]
  if args['--protocol'] == 'UD':
    sessions = ['dark']
    recordings =  ['0', '1' ]
  if args['--protocol'] == 'UO':
    sessions = ['outdoor']
    recordings =  ['0''1' ]
  build_list(args['--imagesdir'], subjects_ids, channel, sessions, recordings, list_filename, False)
