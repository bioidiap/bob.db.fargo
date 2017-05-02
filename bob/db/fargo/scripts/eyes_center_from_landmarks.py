#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 21 Nov 08:25:54 CET 2016

"""Eyes center extractor for the FARGO images (%(version)s)

Usage:
  %(prog)s [--ldmdir=<path>] [--eyesdir=<path>] [--imagesdir=<path>] 
           [--verbose ...] [--plot] [--log=<string>]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -l, --ldmdir=<path>       The path to the landmarks on your disk.
  -e, --eyesdir=<path>      Where to store saved images.
  -i, --imagesdir=<path>    Where the images are stored.
      --log=<string>        Log filename [default: logs.txt]
  -v, --verbose             Increase the verbosity (may appear multiple times).
  -P, --plot                Show some stuff

Example:

  To get the eyes center, do

    $ %(prog)s --ldmdir path/to/database

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
import bob.ip.draw


def get_frame(image_dir, index):
  """ get_frame(image_dir, index) -> frame
  
  This function gets the frame that corresponds to the landmarks.

  **Parameters**

    ``image_dir`` (path):
      The dir continaing the image

    ``index`` (int):
      The index of the image

  **Returns**

    ``frame`` (numpy array):
      The frame where the annotation have been made
  """
  image_file = os.path.join(image_dir, '{:0>2d}.png'.format(index))
  if os.path.isfile(image_file): 
    frame = bob.io.base.load(image_file)
    return frame


def is_annotation_complete(landmarks):
  """ is_annotation_complete(landmarks) -> True or False
 
  This function checks if the landmarks read from the provided 
  file contain what we need to infer eyes center (i.e. eyes corner)
  
  **Parameters**

    ``landmarks`` (dict):
     The landmarks, read from a txt file and stored as a dict 

  **Returns**

    ``bool`` (boolean):
      True if all eyes corners are present, False otherwise.
  """
  if '1' not in landmarks.keys() or '2' not in landmarks.keys() or '3' not in landmarks.keys() or '4' not in landmarks.keys():
    return False
  return True


def get_eyes_center(landmarks):
  """ get_eyes_center(landmarks) -> eyes_center

  This function computes the position of the eyes center,
  based on eyes corners.

  Note that left and right are defined wrt the imaged subject.

  **Parameters**
    
    ``landmarks`` (dict):
     The landmarks, read from a txt file and stored as a dict 

  **Returns**

    ``eyes_center`` (tuple):
     Tuple containing the (x, y) position of the right and left eye. 
  """
  reye_x = int(0.5 * (landmarks['1'][1] + landmarks['2'][1]))
  reye_y = int(0.5 * (landmarks['1'][0] + landmarks['2'][0]))
  leye_x = int(0.5 * (landmarks['3'][1] + landmarks['4'][1]))
  leye_y = int(0.5 * (landmarks['3'][0] + landmarks['4'][0]))
  return (reye_x, reye_y, leye_x, leye_y)


def draw_eyes_center(frame, positions):
  """ draw_eyes_center(frame, positions) -> frame

  This function draws the computed eyes center on the provided image.
  
  **Parameters**
    
    ``frame`` (numpy array):
    The frame on which to draw eyes center. 

    ``positions`` (tuple):
    The position of the center of both eyes.
  """
  reye_x = positions[0]
  reye_y = positions[1]
  leye_x = positions[2]
  leye_y = positions[3]
  if frame.shape[0] == 3:
    bob.ip.draw.cross(frame, (reye_y, reye_x), 4, (255,0,0)) 
    bob.ip.draw.cross(frame, (leye_y, leye_x), 4, (255,0,0)) 
  else:
    bob.ip.draw.cross(frame, (reye_y, reye_x), 4, (255)) 
    bob.ip.draw.cross(frame, (leye_y, leye_x), 4, (255)) 
  return frame


def draw_landmarks(frame, landmarks):
  """ draw_landmarks(frame, landmarks) -> frame
  
  This function draws both the original landmarks (provided in the file)
  and the projected ones.
   
  **Parameters**
    
    ``frame`` (numpy array):
      The frame on which to draw eyes center. 

    ``landmarks`` (dict):
      The landmarks 
  """
  for i in landmarks.keys():  
    if frame.shape[0] == 3:
      bob.ip.draw.plus(frame, (landmarks[i][0], landmarks[i][1]), 4, (0,255,0))
    else:
      bob.ip.draw.plus(frame, (landmarks[i][0], landmarks[i][1]), 4, (255))
  return frame 


def get_landmarks(annotation_file):
  """ get_landmarks(annotation_file) -> landmarks
  
  This function reads landmarks from a file and load
  them into a dictionary.


  Note: left and right are defined in terms of subject
  Landmarks:
  1 right corner of right eye 
  2 left corner of right eye 
  3 right corner of left eye 
  4 left corner of left eye 
  5
  6
  7
  8
  9
  10
  11
  12
  13
  14
  15
  16

  **Parameters**
    
    ``annotated_file`` (path):
      The path to the file containing the landmarks.
   
   **Returns**

    ``landmarks`` (dict):
      The landmarks.
  """
  with open(annotation_file, "r") as c:
    landmarks = {}
    for line in c:
      line = line.rstrip()
      ints = line.split()
      landmarks[ints[0]] = ((int(ints[2]), int(ints[1])))
    return landmarks

def write_eyes_pos(eyes, eyes_dir):
  """ write_eyes_pos(eyes, eyes_dir)

  This function write the eyes center in text file(s).

  **Parameters**
    
    ``eyes`` (tuple):
      tuple containing the (x,y) coordinates of the eyes center.
   
    ``eyes_dir`` (path):
      The path to the dir where the file(s) are written.
  """ 
  if not os.path.isdir(eyes_dir):
    os.makedirs(eyes_dir)
  for i in range(0, 10):
    eyes_filename = os.path.join(eyes_dir, '{:0>2d}.pos'.format(i))
    eyes_file = open(eyes_filename, 'w')
    eyes_file.write('{0} {1} {2} {3}'.format(eyes[0], eyes[1], eyes[2], eyes[3]))
    eyes_file.close()


def annotations_exist(annotation_dir):
  """annotations_exist(annotation_dir) -> [True, False]

  This function checks if the annotation (i.e. eyes center) already exists 
  
  **Parameters**

    ``annotation_dir`` (path):
      The directory where the annotations should be saved.

  **Returns**

    ``bool`` (boolean):
      True if all annotations exist, False otherwise.
  """
  for i in range(0,10):
    annotation_file = os.path.join(annotation_dir, '{:0>2d}.pos'.format(i))
    if not os.path.isfile(annotation_file):
      return False
  return True
  

def main(user_input=None):
  """
  Main function to extract eyes center from existing annotations.
  """

  # Parse the command-line arguments
  if user_input is not None:
      arguments = user_input
  else:
      arguments = sys.argv[1:]

  prog = os.path.basename(sys.argv[0])
  completions = dict(prog=prog,version=version,)
  args = docopt(__doc__ % completions,argv=arguments,
                version='Eyes position extractor (%s)' % version,)

  # if the user wants more verbosity, lowers the logging level
  if args['--verbose'] == 1: logging.getLogger("extract_log").setLevel(logging.INFO)
  elif args['--verbose'] >= 2: logging.getLogger("extract_log").setLevel(logging.DEBUG)

  if args['--ldmdir'] is None:
    logger.warning("You should provide a valid path to the landmarks")
    sys.exit()

  base_dir = args['--ldmdir']
  if not os.path.isdir(args['--eyesdir']):
    os.mkdir(args['--eyesdir'])

  logfile = open(args['--log'], 'w')
  
  # to compute various stats
  total_counter = 0
  inexisting_counter = 0
  incomplete_counter = 0
  projection_counter = 0
  heuristic_counter = 0

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
          logger.debug("===== Subject {0}, session {1}, device {2}, recording {3} ...".format(subject, session, condition, recording))

          # create directories to save the extracted annotations 
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording)):
            os.makedirs(os.path.join(args['--eyesdir'], subject, session, condition, recording))
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'color')):
            os.makedirs(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'color'))
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'ir')):
            os.makedirs(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'ir'))
          if not os.path.isdir(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'depth')):
            os.makedirs(os.path.join(args['--eyesdir'], subject, session, condition, recording, 'depth'))

          # the directories - input
          recording_dir = os.path.join(session_dir, condition, recording)
          color_dir = os.path.join(recording_dir, 'color')
          ir_dir = os.path.join(recording_dir, 'ir')

          # the directories - output
          color_eyes_dir = os.path.join(args['--eyesdir'], subject, session, condition, recording, 'color')
          ir_eyes_dir = os.path.join(args['--eyesdir'], subject, session, condition, recording, 'ir')
          depth_eyes_dir = os.path.join(args['--eyesdir'], subject, session, condition, recording, 'depth')
         
          # check if annotations for this recording already exists
          if annotations_exist(color_eyes_dir) and annotations_exist(ir_eyes_dir) and annotations_exist(depth_eyes_dir):
            logger.warn('Existing annotations for {0}'.format(recording_dir))
            continue
        
          # loop on the images extracted from this sequences
          for i in range(0,10):

            # read the original landmarks - color
            color_ldm_file = os.path.join(color_dir, '{:0>2d}.pos'.format(i))
            try:
              color_landmarks = get_landmarks(color_ldm_file)
            except IOError:
              logger.warn("No color annotations for recording {0}".format(recording_dir))
              logfile.write('[NO ANNOTATIONS] ' + color_dir + '\n')
              inexisting_counter += 1

            # read the original landmarks - ir
            ir_ldm_file = os.path.join(ir_dir, '{:0>2d}.pos'.format(i))
            try:
              ir_landmarks = get_landmarks(ir_ldm_file)
            except IOError:
              logger.warn("No ir annotations for recording {0}".format(recording_dir))
              logfile.write('[NO ANNOTATIONS] ' + ir_dir + '\n')
              inexisting_counter += 1
          
            # check if we have all we need (possibly after re-projection)
            if is_annotation_complete(color_landmarks) and is_annotation_complete(ir_landmarks):
            
              # get the eyes center 
              color_eyes = get_eyes_center(color_landmarks)
              ir_eyes = get_eyes_center(ir_landmarks)

              # and save the file(s) - note that ir and depth are the same
              write_eyes_pos(color_eyes, color_eyes_dir)
              write_eyes_pos(ir_eyes, ir_eyes_dir)
              write_eyes_pos(ir_eyes, depth_eyes_dir)
          
            # plot stuff if asked for 
            if bool(args['--plot']):
              if args['--imagesdir'] is None:
                logger.warn("You should provide an image directory if you want to plot something ...")
              else:
                color_frame_dir = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'color')
                color_frame = get_frame(color_frame_dir, i)
                display_color = draw_eyes_center(color_frame, color_eyes)
                ir_frame_dir = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'ir')
                ir_frame = get_frame(ir_frame_dir, i)
                display_ir = draw_eyes_center(ir_frame, ir_eyes)
                from matplotlib import pyplot
                f, axarr = pyplot.subplots(1, 2)
                pyplot.suptitle('Inferred eyes center')
                axarr[0].imshow(numpy.rollaxis(numpy.rollaxis(display_color, 2),2))
                axarr[0].set_title("Color")
                axarr[1].imshow(display_ir, cmap='gray')
                axarr[1].set_title("NIR")
                pyplot.show()

                if args['--verbose'] >= 2: 
                  display_color = draw_landmarks(color_frame, color_landmarks)
                  display_ir = draw_landmarks(ir_frame, ir_landmarks)
                  f, axarr = pyplot.subplots(1, 2)
                  pyplot.suptitle('Landmarks')
                  axarr[0].imshow(numpy.rollaxis(numpy.rollaxis(display_color, 2),2))
                  axarr[0].set_title("Color")
                  axarr[1].imshow(display_ir, cmap='gray')
                  axarr[1].set_title("NIR")
                  pyplot.show()

            total_counter += 1

  logger.info("Processed {0} sequences".format(total_counter))
  logger.info("\t {0} had no annotations".format(inexisting_counter))
  logger.info("\t {0} needed reprojection".format(projection_counter))
  logger.info("\t {0} where incomplete".format(incomplete_counter))
  logger.info("\t {0} needed heuristic (incomplete after reprojection)".format(heuristic_counter))

  logfile.close()
