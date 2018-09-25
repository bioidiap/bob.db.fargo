#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Thu 22 Dec 09:00:55 CET 2016

""" Generate file lists for the pose-varying protocols of the FARGO database

Usage:
  %(prog)s [--imagesdir=<path>] 
           [--verbose ...]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -i, --imagesdir=<path>    Where both the frontal images are saved and where
                            the pose varying folders will be saved.
  -v, --verbose             Increase the verbosity (may appear multiple times).

Example:

  To run the generation of file list 

    $ %(prog)s --imagesdir image 

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

def build_enroll_list(image_dir, ids, channel, sessions, recordings, list_filename, world=False):
  """build_list(image_dir, ids, channel, sessions, recordings, list_filename[, world=False])
  
  This function creates a list of images for enrollment.
  Note that this will be the same as the one for frontal face verification
  
  **Parameters**

    ``images_dir`` (path):
      The path where the subject images are stored.
    
    ``ids`` (list):
      list of subjects id for this filelist. 

    ``channel`` (string):
      The type of recorded data (RGB, NIR or depth).

    ``sessions`` (list):
      The list of sessions considered to build this list.

    ``recordings`` (list):
      The list of recordings considered to build this list.

    ``list_filename`` (path):
      The list filename.
  
    ``enroll`` (boolean):
      Set to true if the list is an enrollment list.
  """
  
  f = open(list_filename, 'w')

  for subject in ids:
    subject = '{:0>3d}'.format(subject)
    for condition in ['SR300-laptop', 'SR300-mobile']:
      for session in sessions:
        for recording in recordings:
          subject_images_dir = os.path.join(image_dir, subject, session, condition, recording, channel)
          for image in os.listdir(subject_images_dir):
            # needed since pose-varying images are in subfolders in this folder
            if os.path.isfile(os.path.join(subject_images_dir, image)):
              filepath = os.path.splitext(os.path.os.path.join(subject, session, condition, recording, channel, image))[0]
              if not world:
                f.write(filepath + ' ' + subject + ' ' + subject + '\n')
              else:
                f.write(filepath + ' ' + subject + '\n')
  f.close()

def build_probe_list(image_dir, ids, channel, sessions, recordings, orientation, list_filename):
  """build_probe_list(image_dir, ids, channel, sessions, recordings, orientation, list_filename)
  
  This function creates a list of images for probe testing. 
  
  **Parameters**

    ``images_dir`` (path):
      The path where the subject images are stored.
    
    ``ids`` (list):
      list of subjects id for this filelist. 

    ``channel`` (string):
      The type of recorded data (RGB, NIR or depth).

    ``sessions`` (list):
      The list of sessions considered to build this list.

    ``recordings`` (list):
      The list of recordings considered to build this list.

    ``orientation`` (string):
      The orientation of the probes.
  
    ``list_filename`` (path):
      The list filename.
  
    ``enroll`` (boolean):
      Set to true if the list is an enrollment list.
  """
  
  f = open(list_filename, 'w')

  for subject in ids:
    subject = '{:0>3d}'.format(subject)
    for condition in ['SR300-laptop', 'SR300-mobile']:
      for session in sessions:
        for recording in recordings:
          subject_images_dir = os.path.join(image_dir, subject, session, condition, recording, channel, orientation)
          for image in os.listdir(subject_images_dir):
            filepath = os.path.splitext(os.path.os.path.join(subject, session, condition, recording, channel, orientation, image))[0]
            f.write(filepath + ' ' + subject + '\n')

  f.close()


def main(user_input=None):
  """
  
  Main function to generate protocol file lists for pose-varying face authentication

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

  # check user input
  if args['--imagesdir'] is None:
    idiap_dir = '/idiap/project/fargo/databases/images_public/'
    if os.path.isdir(idiap_dir):
      args['--imagesdir'] = idiap_dir
    else:
      logger.warning("You should provide a valid path to the subjects frontal images")
      sys.exit()
  
  # get the modality and the channel
  modality = 'RGB'
  channel = 'color'
  
  orientations = ['pitch', 'yaw']
  for orientation in orientations:

    # build the correct output dir to store file lists
    basedir = 'bob/db/fargo/lists'
    lists_dir = os.path.join(basedir, 'pos_' + orientation)
    if not os.path.isdir(lists_dir):
      os.makedirs(lists_dir)
    
    # === WORLD MODEL LIST ===
    logger.info("[{0}] Generating WORLD list".format(orientation))
    world_dir = os.path.join(lists_dir, 'norm') 
    list_filename = os.path.join(world_dir, 'train_world.lst')
    if not os.path.isdir(os.path.dirname(list_filename)):
      os.makedirs(os.path.dirname(list_filename))
    subjects_ids = range(1, 26, 1)
    sessions = ['controlled']
    recordings =  ['0', '1']
    build_enroll_list(args['--imagesdir'], subjects_ids, channel, sessions, recordings, list_filename, world=True)

    # === ENROLLMENT LISTS === 
    sessions = ['controlled']
    recordings =  ['0']
    
    # dev
    logger.info("[{0}] Generating enrollment list for DEV set)".format(orientation))
    dev_dir = os.path.join(lists_dir, 'dev')
    list_filename = os.path.join(dev_dir, 'for_models.lst')
    if not os.path.isdir(os.path.dirname(list_filename)):
      os.makedirs(os.path.dirname(list_filename))
    subjects_ids = range(26, 51, 1)
    build_enroll_list(args['--imagesdir'], subjects_ids, channel, sessions, recordings, list_filename)
    
    # eval
    logger.info("[{0}] Generating enrollment list for EVAL set)".format(orientation))
    eval_dir = os.path.join(lists_dir, 'eval')
    list_filename = os.path.join(eval_dir, 'for_models.lst')
    if not os.path.isdir(os.path.dirname(list_filename)):
      os.makedirs(os.path.dirname(list_filename))
    subjects_ids = range(51, 76, 1)
    build_enroll_list(args['--imagesdir'], subjects_ids, channel, sessions, recordings, list_filename)

    # === SCORES LIST ===
    # both recordings are used - even for MC - since probes are pose varying and are not in enrollment
    recordings = ['0', '1']
    sessions = ['controlled']
    
    # dev
    logger.info("[{0}] Generating scores list for DEV set".format(orientation))
    dev_dir = os.path.join(lists_dir, 'dev')
    list_filename = os.path.join(dev_dir, 'for_probes.lst')
    if not os.path.isdir(os.path.dirname(list_filename)):
      os.makedirs(os.path.dirname(list_filename))
    subjects_ids = range(26, 51, 1)
    build_probe_list(args['--imagesdir'], subjects_ids, channel, sessions, recordings, orientation, list_filename)

      # eval
    logger.info("[{0}] Generating scores list for EVAL set".format(orientation))
    eval_dir = os.path.join(lists_dir, 'eval')
    list_filename = os.path.join(eval_dir, 'for_probes.lst')
    if not os.path.isdir(os.path.dirname(list_filename)):
      os.makedirs(os.path.dirname(list_filename))
    subjects_ids = range(51, 76, 1)
    build_probe_list(args['--imagesdir'], subjects_ids, channel, sessions, recordings, orientation, list_filename)
