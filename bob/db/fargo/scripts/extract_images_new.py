#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 21 Nov 08:25:54 CET 2016

"""Image extractor for the FARGO videos (%(version)s)

Usage:
  %(prog)s [--dbdir=<path>] [--imagesdir=<path>] [--interval=<int>] 
           [--log=<string>] [--verbose ...] [--plot]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -d, --dbdir=<path>        The path to the database on your disk.
  -i, --imagesdir=<path>    Where to store saved images.
      --interval=<int>      Interval [*10ms] between saved images [default: 4]
  -l, --log=<string>        Log filename [default: logs.txt]
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
import subprocess

import bob.io.video
import bob.io.base
import bob.io.image
import bob.ip.color

def find_closest_frame_index(color_time, other_timestamps):
  """find_closest_frame_index(color_time, ir_timestamps) -> return_index
  This function finds the closest frame in other channels.

  Finds the closest frame in either NIR or depth stream 
  from the current frame extracted from the color stream
  
  **Parameters**

    ``color_time`` (int):
      Timestamp [ms] of the current color frame

    ``other_timestamps`` (dict):
      Dictionary with the frame index and the 
      corresponding timestamp for the other stream

  **Returns**

    ``return_index`` (int):
      Index of the closest frame
  """
  return_index = -1
  diff = sys.maxint
  for index in other_timestamps:
    if abs(other_timestamps[index] - color_time) < diff:
      diff = abs(other_timestamps[index] - color_time)
      return_index = index
  return return_index


def load_timestamps(filename):
  """load_timestamps(filename) -> timestamps:
  This function load timestamps from a text file.
  
  Each line contains two numbers: the frame index and the corresponding time in milliseconds.
  
  **Parameters**

    ``filename`` (path):
      The file to extract timestamps from.

  **Returns**

    ``timestamps`` (dict):
      dictionary with index as key and timestamp as value.
  """
  
  timestamps = {}
  try:
    f = open(filename, 'r')
    for line in f:
      line = line.rstrip('\n')
      splitted = line.split(' ')
      timestamps[int(splitted[0])] = int(splitted[1])   
  except IOError:
    logger.warn("No timestamps for {0}".format(filename))
  return timestamps


def get_first_annotated_frame_index(filename):
  """get_first_annotated_frame_index(filename) -> (frame_index, frame_timestamp)
  This function determines the frame index of the first annotated frame .
 
  It is based on the timestamps file provided with the annoations.
  
  **Parameters**

    ``filename`` (path):
      The file with annotations timestamps. 

  **Returns**

    ``indices`` (list of tuples):
      list of (frame_index, timestamp) for annotated frames in the sequence.

    ``status`` (int):
      Status of the process (-1 meaning failure)
  """
  status = 0 
  try:
    f = open(filename, 'r')
    first_line = f.readline().rstrip()
    first_line = first_line.split(' ')
    indices = (int(first_line[0]), int(first_line[1]))
  except IOError:
    status = -1 
    logger.warn("No annotations for this recording")
    indices = (0, 0)
  
  return indices, status

def get_annotated_image(first_annotated_frame_indices, annotation_dir):
  """get_annotated_image(first_annotated_frame_indices, annotation_dir) -> annotated_frame, status
  This function gets the frame that has been used for annotations.

  This frame is in the annotation folder, and hence does not come from
  the stream where we'll extract frames.

  **Parameters**

    ``first_annotated_frame_indices`` (tuple):
      The tuple containing the index and the timestamp
      of the first annotated frame.

    ``annotation_dir`` (path):
      The dir with the annotations, and the 
      images that were annotated

  **Returns**

    ``annotated_frame`` (numpy 3d array):
      The frame where the annotation have been made

    ``status`` (int):
      Tells if the process was ok (!= -1)
  """
  annotated_frame = numpy.array([0, 0])
  status = -1
  annotation_timestamps = []

  try:
    f = open(os.path.join(annotation_dir, 'color_timestamps.txt'), 'r')
    for line in f:
      line = line.rstrip('\n')
      splitted = line.split(' ')
      annotation_timestamps.append((int(splitted[0]), int(splitted[1])))   
  except IOError:
    logger.warn("No timestamps for {0}".format(annotation_dir))
 
  frame_counter = 0
  for frame_indices in annotation_timestamps:
    if frame_indices == first_annotated_frame_indices:
      annotated_file = os.path.join(annotation_dir, 'color', str(frame_counter) + '.264')
      if os.path.isfile(annotated_file): 
        annotated_stream = bob.io.video.reader(annotated_file)
        for i, frame in enumerate(annotated_stream):
          return frame, 0
    frame_counter += 1

  return annotated_frame, -1 

def check_if_recording_is_ok(images_dir, subject, session, condition, recording):
  """check_if_recording_is_ok(images_dir, subject, session, condition, recording) -> [True, False]
  This function checks if the processing of an existing recording is complete.

  This function goes recursively through the folder where the data from
  this recording are supposed to be saved. Returns True if every file
  supposed to be here is present, and False otherwise.

  **Parameters**

    ``images_dir`` (path):
      The path where extracted images are supposed to be saved.

    ``subject`` (string):
      The subject's ID

    ``session`` (string):
      The session (controlled, dark, outdoor)

    ``condition`` (string):
      The condition (either laptop or mobile)

    ``recording`` (string):
      The recording (0 or 1)

  **Returns**

    ``[True, False]`` (bool)
  """
  base_path = os.path.join(images_dir, subject, session, condition, recording)
  color_dir = os.path.join(base_path, 'color')
  ir_dir = os.path.join(base_path, 'ir')
  depth_dir = os.path.join(base_path, 'depth')

  for index in range(10):
    filename = os.path.join(color_dir, '{:0>2d}.png'.format(index))
    if not os.path.isfile(filename):
      return False
    filename = os.path.join(ir_dir, '{:0>2d}.hdf5'.format(index))
    if not os.path.isfile(filename):
      return False
    filename = os.path.join(depth_dir, '{:0>2d}.hdf5'.format(index))
    if not os.path.isfile(filename):
      return False
  
  return True

def write_bindata_as_image(data, filename, ir=True):

    # rescale to 0-255
    min_value = numpy.min(data)
    max_value = numpy.max(data)
    print min_value
    print max_value
    new_data = (data - min_value) / (max_value - min_value) * 255.0

    from matplotlib import pyplot
    if ir:
      pyplot.imshow(data, cmap='gray')
    else:
      pyplot.imshow(data, cmap='bwr')
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
  completions = dict(prog=prog, version=version,)
  args = docopt(__doc__ % completions,argv=arguments,version='Image extractor (%s)' % version,)

  # if the user wants more verbosity, lowers the logging level
  if args['--verbose'] == 1: logging.getLogger("extract_log").setLevel(logging.INFO)
  elif args['--verbose'] >= 2: logging.getLogger("extract_log").setLevel(logging.DEBUG)

  if args['--dbdir'] is None:
    logger.warning("You should provide a valid path to the data")
    sys.exit()

  base_dir = args['--dbdir']
  if not os.path.isdir(args['--imagesdir']):
    os.makedirs(args['--imagesdir'])

  # log file to record errors ...
  logfile = open(args['--log'], 'a')

  # go through the subjects 
  for subject in os.listdir(base_dir):

    sessions = ['controlled', 'dark', 'outdoor']
    # small hack to process FdV subjects ...
    if int(subject) >= 129:
      sessions = ['fdv']

    for session in sessions: 
      for condition in ['SR300-laptop', 'SR300-mobile']:
        for recording in ['0', '1']:
          
          logger.info("===== Subject {0}, session {1}, device {2}, recording {3} ...".format(subject, session, condition, recording))

          # create directories to save the extracted data
          if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session, condition, recording)):
            os.makedirs(os.path.join(args['--imagesdir'], subject, session, condition, recording))
          if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'color')):
            os.makedirs(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'color'))
          if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'ir')):
            os.makedirs(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'ir'))
          if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'depth')):
            os.makedirs(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'depth'))

          # get the original data
          color_dir = os.path.join(base_dir, subject, session, condition, recording, 'streams', 'color')
          ir_dir = os.path.join(base_dir, subject, session, condition, recording, 'streams', 'ir')
          depth_dir = os.path.join(base_dir, subject, session, condition, recording, 'streams', 'depth')

          
          # uncompress the 7z archive - both ir and depth
          ir_compressed = os.path.join(ir_dir, 'ir.7z')
          command = "7z x -y -o" + ir_dir + ' ' + ir_compressed
          try:
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdoutdata, stderrdata = p.communicate()
          except:
            pass
          depth_compressed = os.path.join(depth_dir, 'depth.7z')
          command = "7z x -y -o" + depth_dir + ' ' + depth_compressed
          try:
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdoutdata, stderrdata = p.communicate()
          except:
            pass

          # process color file
          color_file = os.path.join(color_dir, 'color.264')
          if os.path.isfile(color_file):
            color_stream = bob.io.video.reader(color_file)
          else:
            logfile.write('subject {0}, session {1}, condition {2}, rec {3} -> NO DATA\n'.format(subject, session, condition, recording))
            logger.warn('subject {0}, session {1}, condition {2}, rec {3} -> NO DATA'.format(subject, session, condition, recording))
            continue

          # get the timestamps of the color frames
          color_timestamps = load_timestamps(os.path.join(base_dir, subject, session, condition, recording, 'streams', 'color_timestamps.txt'))
          ir_timestamps = load_timestamps(os.path.join(base_dir, subject, session, condition, recording, 'streams', 'ir_timestamps.txt'))
          depth_timestamps = load_timestamps(os.path.join(base_dir, subject, session, condition, recording, 'streams', 'depth_timestamps.txt'))
          
          # get the index of the first annotated frame in the stream
          first_annotated_frame_indices, status = get_first_annotated_frame_index(os.path.join(base_dir, subject, session, condition, recording, 'annotations', 'color_timestamps.txt'))
          if status < 0:
            logfile.write('subject {0}, session {1}, condition {2}, rec {3} -> no annotations\n'.format(subject, session, condition, recording))
          logger.info("First annotated frame is frame #{0}, at time {1}".format(first_annotated_frame_indices[0], first_annotated_frame_indices[1]))
          
          # get the provided image corresponding to the annotated frame - debugging purposes
          annotation_dir = os.path.join(base_dir, subject, session, condition, recording, 'annotations')
          annotated_frame, status = get_annotated_image(first_annotated_frame_indices, annotation_dir)
          if status == -1:
            logger.warn("No provided annotated frame for this recording".format(color_file))
          else:
            if bool(args['--plot']):
              from matplotlib import pyplot
              pyplot.imshow(numpy.rollaxis(numpy.rollaxis(annotated_frame, 2),2))
              pyplot.title('Provided annotated frame')
              pyplot.show()
          
          interval = int(args['--interval'])
          saved_image_index = 0
          last_frame_index = first_annotated_frame_indices[0] + (10 * interval)
          
          # now loop on the color stream
          for i, frame in enumerate(color_stream):
            
            # get the frames of interest (i.e. at each interval)
            toto = i - first_annotated_frame_indices[0]
            if toto % 4 == 0 and i < last_frame_index:

              # save color image
              saved_png = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'color', '{:0>2d}.png'.format(saved_image_index))
              #to_save = bob.ip.color.rgb_to_gray(frame)
              bob.io.base.save(frame, saved_png)
           
              # if this is the first frame to save, make a check to be sure that this frame corresponds to the provided annotated frame ...
              if i == first_annotated_frame_indices[0] and status == 0:
                diff = annotated_frame - frame
                if numpy.any(diff):
                  logfile.write('subject {0}, session {1}, condition {2}, rec {3} -> current frame and annotated frame are different\n'.format(subject, session, condition, recording))
                  #if bool(args['--plot']):
                  from matplotlib import pyplot
                  f, axarr = pyplot.subplots(1, 3)
                  axarr[0].imshow(numpy.rollaxis(numpy.rollaxis(frame, 2),2))
                  axarr[0].set_title("Frame in the color stream")
                  axarr[1].imshow(numpy.rollaxis(numpy.rollaxis(annotated_frame, 2),2))
                  axarr[1].set_title("Image provided with annotations")
                  axarr[2].imshow(numpy.rollaxis(numpy.rollaxis(diff, 2),2))
                  axarr[2].set_title("Difference")
                  pyplot.show()

              # find the closest ir frame, and save the data 
              ir_index = find_closest_frame_index(color_timestamps[toto], ir_timestamps)
              logger.debug("Closest IR frame is at {0} with index {1} (color is at {2})".format(ir_timestamps[ir_index], ir_index, color_timestamps[toto]))
              

              ir_file = os.path.join(ir_dir, '{0}.bin'.format(ir_index))
              ir_data = numpy.fromfile(ir_file, dtype=numpy.int16).reshape(-1, 640)
              saved_ir = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'ir', '{:0>2d}.hdf5'.format(saved_image_index))
              bob.io.base.save(ir_data, saved_ir)
              
              # find the closest depth frame, and save the data 
              depth_index = find_closest_frame_index(color_timestamps[toto], depth_timestamps)
              logger.debug("Closest depth frame is at {0} with index {1} (color is at {2})".format(depth_timestamps[depth_index], depth_index, color_timestamps[toto]))
              
              # uncompress the 7z archive
              
              depth_file = os.path.join(depth_dir, '{0}.bin'.format(depth_index))
              depth_data = numpy.fromfile(depth_file, dtype=numpy.int16).reshape(-1, 640)
              saved_depth = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'depth', '{:0>2d}.hdf5'.format(saved_image_index))
              bob.io.base.save(depth_data, saved_depth)
  
              # plot saved data if asked for
              if bool(args['--plot']):
                from matplotlib import pyplot
                f, axarr = pyplot.subplots(1, 3)
                pyplot.suptitle('frame {0} at time {1} saved'.format(toto, color_timestamps[toto]))
                axarr[0].imshow(numpy.rollaxis(numpy.rollaxis(frame, 2),2))
                axarr[0].set_title("Color")
                axarr[1].imshow(ir_data, cmap='gray')
                axarr[1].set_title("NIR")
                axarr[2].imshow(depth_data)
                axarr[2].set_title("Depth")
                pyplot.show()
              
              saved_image_index += 1
           
            # stop when done saving the number of desired images
            if i > last_frame_index:
              break

  logfile.close()
