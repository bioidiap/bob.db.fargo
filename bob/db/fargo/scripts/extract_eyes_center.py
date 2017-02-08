#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 21 Nov 08:25:54 CET 2016

"""Eyes center extractor for the FARGO images (%(version)s)

Usage:
  %(prog)s [--dbdir=<path>] [--eyesdir=<path>] 
           [--verbose ...] [--plot] [--log=<string>]

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

from ..camera import IntrinsicParameters 
from ..camera import ExtrinsicParameters 
from ..camera import get_UV_map
from ..camera import get_correspondences


def get_color_frame(annotation_dir):
  """ get_color_frame(annotation_dir) -> frame
  
  This function gets the color frame that corresponds to the first annotations.

  **Parameters**

    ``annotation_dir`` (path):
      The dir with the annotations, and the images that were annotated

  **Returns**

    ``frame`` (numpy 3d array):
      The frame where the annotation have been made
  """
  annotated_file = os.path.join(annotation_dir, '0.264')
  if os.path.isfile(annotated_file): 
    annotated_stream = bob.io.video.reader(annotated_file)
    for i, frame in enumerate(annotated_stream):
      return frame


def get_data_frame(annotation_dir):
  """ get_data_frame(annotation_dir) -> frame

  This function gets the IR frame that corresponds to the first annotations.

  **Parameters**

    ``annotation_dir`` (path):
      The dir with the annotations, and the images that were annotated

  **Returns**

    ``image`` (numpy 3d array):
      The IR image (rescaled) where the annotation have been made
  """
  bin_file = os.path.join(annotation_dir, '0.bin')
  if os.path.isfile(bin_file): 
    bin_data = numpy.fromfile(bin_file, dtype=numpy.int16).reshape(-1, 640)
    bin_image = bin_data / 4.0
    bin_image = bin_image.astype('uint8')
    image = numpy.zeros((3, bin_image.shape[0], bin_image.shape[1]), 'uint8')
    image[0] = image[1] = image[2] = bin_image
  return image 


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
  
 # print "============================"
 # print "right eye right corner (y,x) = {0}".format(landmarks['1'])
 # print "right eye left corner (y,x) = {0}".format(landmarks['2'])
 # print "right eye center (y,x) = {0}".format((reye_y, reye_x))
 # print "----------------------------"
 # print "left eye right corner (y,x) = {0}".format(landmarks['4'])
 # print "left eye right corner (y,x) = {0}".format(landmarks['3'])
 # print "left eye center (y,x) = {0}".format((leye_y, leye_x))
  return (reye_x, reye_y, leye_x, leye_y)


def plot_eyes_center(frame, positions):
  """ plot_eyes_center(frame, positions)

  This function plots the computed eyes center on the provided image.
  
  **Parameters**
    
    ``frame`` (numpy array):
    The frame on which to draw eyes center. 

    ``positions`` (tuple):
    The position of the center of both eyes.
  """
  display = draw_eyes_center(frame, positions)
  from matplotlib import pyplot
  pyplot.imshow(numpy.rollaxis(numpy.rollaxis(display, 2),2))
  pyplot.title('Retrieved eyes center')
  pyplot.show()

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
  bob.ip.draw.cross(frame, (reye_y, reye_x), 4, (255,0,0)) 
  bob.ip.draw.cross(frame, (leye_y, leye_x), 4, (255,0,0)) 
  return frame

def plot_landmarks(frame, annotation_file, retrieved_landmarks):
  """ plot_landmarks(frame, annotation_file, retrieved_landmarks)
  
  This function draws both the original landmarks (provided in the file)
  and the projected ones.
   
  **Parameters**
    
    ``frame`` (numpy array):
      The frame on which to draw eyes center. 

    ``annotation_file`` (path):
      The original annotation file. 

    ``retrieved_landmarks`` (dict):
      The retrieved landmarks (i.e. they may have been obtained
      after reprojection).
  """
  display = draw_landmarks(frame, annotated_file, retrieved_landmarks)
  from matplotlib import pyplot
  pyplot.imshow(numpy.rollaxis(numpy.rollaxis(display, 2),2))
  pyplot.title('Original (red) and projected (green) landmarks')
  pyplot.show()

def draw_landmarks(frame, annotation_file, retrieved_landmarks):
  """ draw_landmarks(frame, annotation_file, retrieved_landmarks) -> frame
  
  This function draws both the original landmarks (provided in the file)
  and the projected ones.
   
  **Parameters**
    
    ``frame`` (numpy array):
      The frame on which to draw eyes center. 

    ``annotation_file`` (path):
      The original annotation file. 

    ``retrieved_landmarks`` (dict):
      The retrieved landmarks (i.e. they may have been obtained
      after reprojection).
  """
  original_landmarks = get_landmarks(annotation_file)
  for i in original_landmarks.keys():
    bob.ip.draw.plus(frame, (original_landmarks[i][0], original_landmarks[i][1]), 4, (255,0,0))
  for i in retrieved_landmarks.keys():  
    bob.ip.draw.cross(frame, (retrieved_landmarks[i][0], retrieved_landmarks[i][1]), 4, (0,255,0))
  return frame 

def draw_eyes_corner(frame, annotation_file, draw_landmarks=True):
  """ draw_eyes_corner(frame, annotation_file) -> frame
  
  This function draws the eyes corner (and the landmarks) 
   
  **Parameters**
    
    ``frame`` (numpy array):
      The frame on which to draw eyes center. 

    ``annotation_file`` (path):
      The original annotation file. 

    ``draw_landmarks`` (boolean):
      Also draws the original landmarks.
  """
  original_landmarks = get_landmarks(annotation_file)
  for i in original_landmarks.keys():
    if i == '1': 
      bob.ip.draw.plus(frame, (original_landmarks[i][0], original_landmarks[i][1]), 4, (255,255,255))
    if i == '2': 
      bob.ip.draw.plus(frame, (original_landmarks[i][0], original_landmarks[i][1]), 4, (255,0,0))
    if i == '3': 
      bob.ip.draw.plus(frame, (original_landmarks[i][0], original_landmarks[i][1]), 4, (0,255,0))
    if i == '4': 
      bob.ip.draw.plus(frame, (original_landmarks[i][0], original_landmarks[i][1]), 4, (0,0,255))
    if draw_landmarks:
      bob.ip.draw.cross(frame, (retrieved_landmarks[i][0], retrieved_landmarks[i][1]), 4, (0,0,0))
  return frame 


def read_landmarks(pos_filename):
  """ read_landmarks(pos_filename) -> landmarks

  This function read landmarks from file.
  It is used to be compliant with camera utilities.
  
  **Parameters**
    
    ``pos_filename`` (path):
      The original annotation file. 
   
   **Returns**

    ``landmarks`` (numpy array (16x2)):
      Array continaing the landmarks 

  """
  landmarks = numpy.zeros((16, 2), dtype=numpy.int32)
  if not os.path.exists(pos_filename):
    logging.warning('{} does not exist'.format(pos_filename))
    return []
  with open(pos_filename, 'r') as f:
    for line in f:
      line_split = line.split()
      if len(line_split) != 3:
        continue
      idx = int(line_split[0])
      landmarks[idx - 1, :] = (int(line_split[1]), int(line_split[2]))
  return landmarks


def load_calibration(recording_dir):
  """ load_calibration(recording_dir) -> depth_intrinsics, color_intrinsics, depth2color 
 
  This function loads camera related parameters from a file.

  **Parameters**
    
    ``recording_dir`` (path):
      The path to the directory corresponding to the recording. 
   
   **Returns**

    ``depth_intrinsics`` (:class: ..camera.IntrinsicParameters):
      Intrinsic parameters of the depth camera 
    
    ``color_intrinsics`` (:class: ..camera.IntrinsicParameters):
      Intrinsic parameters of the color camera 

    ``depth2color`` (:class: ..camera.ExtrinsicParameters):
      Extrinsic parameters relating the depth to the color 
  """
  device_info_filepath = os.path.join(recording_dir, 'device_info.json')
  if not os.path.exists(device_info_filepath):
    logging.error('{} does not exist'.format(device_info_filepath))
  depth_intrinsics = IntrinsicParameters()
  depth_intrinsics.read_json(device_info_filepath, 'depth_intrinsics')
  color_intrinsics = IntrinsicParameters()
  color_intrinsics.read_json(device_info_filepath, 'color_intrinsics')
  depth2color = ExtrinsicParameters()
  depth2color.read_json(device_info_filepath, 'extrinsics')
  return depth_intrinsics, color_intrinsics, depth2color


def project_ir_to_color(ir_file, recording_dir):
  """ project_ir_to_color(ir_file, recording_dir) -> color_landmarks

  This function projects landmarks from the IR image to the
  color image referential.

  **Parameters**
    
    ``ir_file`` (path):
      The path to the file containing the IR landmarks.
   
    ``recording_dir`` (path):
      The path to the directory corresponding to the recording. 
   
   **Returns**

    ``color_landmarks`` (dict):
      The projected landmarks.
  """
  min_depth = 200
  max_pixel_distance = 100
  ir_landmarks = read_landmarks(ir_file)
  depth_file = os.path.join(recording_dir, 'annotations/depth/0.bin') 
  depth_frame = numpy.fromfile(depth_file, dtype=numpy.int16).reshape(-1, 640)
  depth_intrinsics, color_intrinsics, depth2color = load_calibration(recording_dir)
  UV_map = get_UV_map(depth_frame, min_depth, depth_intrinsics, 1e-3, color_intrinsics, depth2color)

  c = 1
  color_landmarks = {}
  for idx, l in enumerate(ir_landmarks):
    min_dist2 = numpy.inf
    min_color = (-1, -1)
    
    for row in range(l[1] - max_pixel_distance, l[1] + max_pixel_distance):
      for col in range(l[0] - max_pixel_distance, l[0] + max_pixel_distance):
        
        if row < 0 or col < 0 or row >= depth_intrinsics.height or col >= depth_intrinsics.width:
          continue
        
        color_col = UV_map[0][row, col] * color_intrinsics.width
        color_row = UV_map[1][row, col] * color_intrinsics.height
        
        if not numpy.isnan(color_col) and not numpy.isnan(color_row):
          dist2 = (l[1] - row) * (l[1] - row) + (l[0] - col) * (l[0] - col)
          if dist2 < min_dist2:
            min_dist2 = dist2
            min_color = (color_row, color_col)
    
    if not numpy.isinf(min_dist2):
      color_col = min_color[1]
      color_row = min_color[0]
      color_landmarks[str(c)] = (int(color_row), int(color_col))
    c += 1

  return color_landmarks


def project_color_to_ir(color_file, recording_dir):
  """ project_color_to_ir(color_file, recording_dir) -> ir_landmarks
  
  This function projects landmarks from the color image to the
  IR image referential.

  **Parameters**
    
    ``color_file`` (path):
      The path to the file containing the color landmarks.
   
    ``recording_dir`` (path):
      The path to the directory corresponding to the recording. 
   
   **Returns**

    ``ir_landmarks`` (dict):
      The projected landmarks.
  """
  min_depth = 200
  max_pixel_distance = 100

  color_landmarks = read_landmarks(color_file)
  depth_file = os.path.join(recording_dir, 'annotations/depth/0.bin') 
  depth_frame = numpy.fromfile(depth_file, dtype=numpy.int16).reshape(-1, 640)
  depth_intrinsics, color_intrinsics, depth2color = load_calibration(recording_dir)
  UV_map = get_UV_map(depth_frame, min_depth, depth_intrinsics, 1e-3, color_intrinsics, depth2color)
  min_dist2, min_idx = get_correspondences(color_landmarks, UV_map, 
                                           color_intrinsics.width, 
                                           color_intrinsics.height,
                                           depth_intrinsics.width,
                                           depth_intrinsics.height)

  ir_landmarks = {}
  c = 1
  for idx in range(min_idx.shape[0]):
    ir_landmarks[str(c)] = (int(min_idx[idx] / depth_intrinsics.width), int(min_idx[idx] % depth_intrinsics.width))
    c += 1

  return ir_landmarks


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

def annotate(image_file, eyes, annotation_dir):

  # create examplar pos file
  f = open('00.pos', 'w')
  f.write('InR InL\n')
  f.write('0 {0} {1} {2} {3}'.format(eyes[0], eyes[1], eyes[2], eyes[3]))
  f.close()

  os.system('./bin/annotate.py ' + image_file + ' 00.pos --output temp.txt')
  raw_input("Press Enter to terminate.")

  # read eyes center from temp annotation file
  f1 = open('temp.txt', 'r')
  for line in f1:
    line = line.rstrip()
    data = line.split()
    if data[0] == '0':
      eyes = (int(data[1]), int(data[2]), int(data[3]), int(data[4]))
  f1.close()
  return eyes


def annotations_exist(annotation_dir):

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

  if args['--dbdir'] is None:
    logger.warning("You should provide a valid path to the data")
    sys.exit()

  base_dir = args['--dbdir']
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
          color_dir = os.path.join(session_dir, condition, recording, 'annotations', 'color')
          ir_dir = os.path.join(session_dir, condition, recording, 'annotations', 'ir')
          depth_dir = os.path.join(session_dir, condition, recording, 'annotations', 'depth')

          # the directories - output
          color_eyes_dir = os.path.join(args['--eyesdir'], subject, session, condition, recording, 'color')
          ir_eyes_dir = os.path.join(args['--eyesdir'], subject, session, condition, recording, 'ir')
          depth_eyes_dir = os.path.join(args['--eyesdir'], subject, session, condition, recording, 'depth')
          
          # check if annotations for this recording already exists
          if annotations_exist(color_eyes_dir) and annotations_exist(ir_eyes_dir) and annotations_exist(depth_eyes_dir):
            logger.warn('Existing annotations for {0}'.format(recording_dir))
            continue
          
          # read the original landmarks - color
          color_file = os.path.join(color_dir, '0.pos')
          try:
            color_landmarks = get_landmarks(color_file)
          except IOError:
            logger.warn("No color annotations for recording {0}".format(recording_dir))
            logfile.write('[NO ANNOTATIONS] ' + color_dir + '\n')
            inexisting_counter += 1

          # read the original landmarks - ir
          ir_file  = os.path.join(ir_dir, '0.pos')
          try:
            ir_landmarks = get_landmarks(ir_file)
          except IOError:
            logger.warn("No ir annotations for recording {0}".format(recording_dir))
            logfile.write('[NO ANNOTATIONS] ' + ir_dir + '\n')
          
          # read the original landmarks - depth
          depth_file  = os.path.join(depth_dir, '0.pos')
          try:
            depth_landmarks = get_landmarks(ir_file)
          except IOError:
            logger.warn("No depth annotations for recording {0}".format(recording_dir))
            logfile.write('[NO ANNOTATIONS] ' + depth_dir + '\n')

          # IR TO COLOR : check if the original landmarks are complete - if not, try to reproject
          if not is_annotation_complete(color_landmarks) and is_annotation_complete(ir_landmarks):
            logger.warn("Projecting IR to color for recording {0}".format(recording_dir))
            logfile.write('[PROJECT] ' + recording_dir + '\n')
            projection_counter += 1
           
            # get color landmarks and eyes from reprojection
            color_landmarks = project_ir_to_color(ir_file, recording_dir)
            color_eyes = get_eyes_center(color_landmarks)
           
            # plot the result of the reprojection
            from matplotlib import pyplot
            color_frame = get_color_frame(color_dir)
            display_color = draw_eyes_center(numpy.copy(color_frame), color_eyes)
            pyplot.title("Projected to color")
            pyplot.imshow(numpy.rollaxis(numpy.rollaxis(display_color, 2),2))
            pyplot.show()

            # ask for re-annotation (i.e. reprojection is not good)
            reannotate = raw_input("Want to re-annotate color ? [y/n]: ")
            if reannotate == 'y':

              # get eyes position in the color frame
              bob.io.base.save(color_frame, '00.png') 
              color_eyes = annotate('00.png', color_eyes, color_eyes_dir)
              
              # save everything and move to the next recording
              write_eyes_pos(color_eyes, color_eyes_dir)
              write_eyes_pos(get_eyes_center(ir_landmarks), ir_eyes_dir)
              write_eyes_pos(get_eyes_center(depth_landmarks), depth_eyes_dir)
              logger.warn("Eyes position saved from the manual annotation")
              continue

          # COLOR TO IR : check if the original landmarks are complete - if not, try to reproject
          if not is_annotation_complete(ir_landmarks) and is_annotation_complete(color_landmarks):
            logger.warn("Projecting color to IR for recording {0}".format(recording_dir))
            logfile.write('[PROJECT] ' + recording_dir + '\n')
            projection_counter += 1
            
            ir_landmarks = project_color_to_ir(color_file, recording_dir)
            ir_eyes = get_eyes_center(ir_landmarks)
            depth_landmarks = ir_landmarks
            depth_eyes = ir_eyes 

            # plot the projected eyes position 
            from matplotlib import pyplot
            ir_frame = get_data_frame(ir_dir)
            display_ir = draw_eyes_center(numpy.copy(ir_frame), ir_eyes)
            pyplot.title('Projected to IR')
            pyplot.imshow(numpy.rollaxis(numpy.rollaxis(display_ir, 2),2))
            pyplot.show()
            
            # ask for re-annotation (i.e. reprojection is not good)
            reannotate = raw_input("Want to re-annotate IR ? [y/n]: ")
            if reannotate == 'y':
              
              # get eyes position in the IR frame
              bob.io.base.save(ir_frame, '00.png') 
              ir_eyes = annotate('00.png', ir_eyes, ir_eyes_dir)
              depth_eyes = ir_eyes
              
              # save everything and move to the next recording
              write_eyes_pos(color_eyes, color_eyes_dir)
              write_eyes_pos(ir_eyes, ir_eyes_dir)
              write_eyes_pos(depth_eyes, depth_eyes_dir)
              logger.warn("Eyes position saved from the manual annotation")
              continue

          # check if we have all we need (possibly after re-projection)
          if is_annotation_complete(color_landmarks) and is_annotation_complete(ir_landmarks) and is_annotation_complete(depth_landmarks):

            print "I'm saving from original annotations (possibly reprojected)"
            # get the eyes center 
            color_eyes = get_eyes_center(color_landmarks)
            ir_eyes = get_eyes_center(ir_landmarks)
            depth_eyes = get_eyes_center(depth_landmarks)

            # and save the file(s)
            write_eyes_pos(color_eyes, color_eyes_dir)
            write_eyes_pos(ir_eyes, ir_eyes_dir)
            write_eyes_pos(depth_eyes, depth_eyes_dir)
          
          # annotate both color and IR when eyes center could not be retrieved from any of the annotations
          else:
            logger.warn("Annotations needed for recording {0}".format(recording_dir))
            logfile.write('[ANNOTATIONS] ' + recording_dir + '\n')
            heuristic_counter += 1
           
            color_eyes = (869, 510, 1040, 509)
            color_frame = get_color_frame(color_dir)
            bob.io.base.save(color_frame, '00.png') 
            color_eyes = annotate('00.png', color_eyes, color_eyes_dir)
           
            ir_eyes = (270, 235, 329, 234)
            ir_frame = get_data_frame(ir_dir)
            bob.io.base.save(ir_frame, '00.png') 
            ir_eyes = annotate('00.png', ir_eyes, ir_eyes_dir)
            depth_eyes = ir_eyes
            
            # and save the file(s)
            write_eyes_pos(color_eyes, color_eyes_dir)
            write_eyes_pos(ir_eyes, ir_eyes_dir)
            write_eyes_pos(depth_eyes, depth_eyes_dir)

          # plot stuff if asked for 
          if bool(args['--plot']):
            color_frame = get_color_frame(color_dir)
            display_color = draw_eyes_center(color_frame, color_eyes)
            ir_frame = get_data_frame(ir_dir)
            display_ir = draw_eyes_center(ir_frame, ir_eyes)
            from matplotlib import pyplot
            f, axarr = pyplot.subplots(1, 2)
            pyplot.suptitle('Inferred eyes center')
            axarr[0].imshow(numpy.rollaxis(numpy.rollaxis(display_color, 2),2))
            axarr[0].set_title("Color")
            axarr[1].imshow(numpy.rollaxis(numpy.rollaxis(display_ir, 2),2))
            axarr[1].set_title("NIR")
            pyplot.show()

            if args['--verbose'] >= 2: 
              display_color = draw_landmarks(color_frame, color_file, color_landmarks)
              display_ir = draw_landmarks(ir_frame, ir_file, ir_landmarks)
              f, axarr = pyplot.subplots(1, 2)
              pyplot.suptitle('Landmarks')
              axarr[0].imshow(numpy.rollaxis(numpy.rollaxis(display_color, 2),2))
              axarr[0].set_title("Color")
              axarr[1].imshow(numpy.rollaxis(numpy.rollaxis(display_ir, 2),2))
              axarr[1].set_title("NIR")
              pyplot.show()

          
          total_counter += 1

  logger.info("Processed {0} sequences".format(total_counter))
  logger.info("\t {0} had no annotations".format(inexisting_counter))
  logger.info("\t {0} needed reprojection".format(projection_counter))
  logger.info("\t {0} where incomplete".format(incomplete_counter))
  logger.info("\t {0} needed heuristic (incomplete after reprojection)".format(heuristic_counter))

  logfile.close()
