#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 21 Nov 08:25:54 CET 2016

"""Image extractor for the FARGO videos (%(version)s)

Usage:
  %(prog)s [--dbdir=<path>] [--imagesdir=<path>] 
           [--verbose ...] [--plot]

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
import bob.io.video
import bob.io.base


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

  folders = []
  folders.append('yaw_small')
  folders.append('yaw_left')
  folders.append('yaw_right')
  folders.append('pitch_small')
  folders.append('pitch_top')
  folders.append('pitch_bottom')
  for folder in folders:
    if not os.path.isdir(os.path.join(base_path, 'color', folder)):
      return False
  return True


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
  f = open(filename, 'r')
  for line in f:
    line = line.rstrip('\n')
    splitted = line.split(' ')
    timestamps[int(splitted[0])] = int(splitted[1])   
  return timestamps


def retrieve_past_timestamps(ref_timestamp, streams_stamps, prev_timestamp=0):

  closest_previous_index = 0 
  previous_stamps = {}
  diff = sys.maxint
  for index in streams_stamps:
    if (streams_stamps[index] > prev_timestamp) and (streams_stamps[index] <= ref_timestamp):
      previous_stamps[index] = streams_stamps[index]
  return previous_stamps

def write_stat(f, pose_text, pose_cluster, n_total_sequences):
  mean_images = pose_cluster / float(n_total_sequences)
  f.write("mean # of images at {0} = {1} ({2} / {3})\n".format(pose_text, mean_images, pose_cluster, n_total_sequences))

def main(user_input=None):
  """
  
  Main function to extract images from recorded streams.
  Images are clustered according to (estimate of) pose.
  The pose is retrieved thanks to annotated images.

    # annotated frame 0: frontal
    # annotated frame 1: 10 degrees left
    # annotated frame 2: 20 degrees left
    # annotated frame 3: 30 degrees left
    # annotated frame 4: 10 degrees right
    # annotated frame 5: 20 degrees right
    # annotated frame 6: 30 degrees right
    # annotated frame 7: 10 degrees top 
    # annotated frame 8: 20 degrees top 
    # annotated frame 9: 30 degrees top 
    # annotated frame 10: 10 degrees bottom 
    # annotated frame 11: 20 degrees bottom 
    # annotated frame 12: 30 degrees bottom 
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

  # lists for pose cluster
  yaw_small = []
  yaw_left = []
  yaw_right = []
  pitch_small = []
  pitch_top = []
  pitch_bottom = []

  # stats on pose clusters 
  n_sequences = 0
  yaw_small_counter = 0
  yaw_left_counter = 0
  yaw_right_counter = 0
  pitch_small_counter = 0
  pitch_top_counter = 0
  pitch_bottom_counter = 0

  # go through the subjects 
  subjects = []
  subjects_ids = range(26, 27, 1)
  for subject in subjects_ids:
    subjects.append('{:0>3d}'.format(subject))
  for subject in subjects:
  
  #for subject in os.listdir(base_dir):

    sessions = ['controlled', 'dark', 'outdoor']
    # small hack to process FdV subjects ...
    if int(subject) >= 129:
      sessions = ['fdv']

    for session in sessions: 
      for condition in ['SR300-laptop', 'SR300-mobile']:
        for recording in ['0', '1']:
          
          logger.info("===== Subject {0}, session {1}, device {2}, recording {3} ...".format(subject, session, condition, recording))

          # get directories where the data resides (streams and annotation)
          annotation_dir = os.path.join(args['--dbdir'], subject, session, condition, recording, 'annotations')
          stream_dir = os.path.join(args['--dbdir'], subject, session, condition, recording, 'streams')
          
          # create directories to save the extracted data
          if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'color')):
            os.makedirs(os.path.join(args['--imagesdir'], subject, session, condition, recording, 'color'))

          # check if the recording has already been processed, and if so, that everything is ok  
          if check_if_recording_is_ok(args['--imagesdir'], subject, session, condition, recording):
            logger.info("recording already processed and ok")
            continue

          # load the files with the timestamps
          color_annotations_timestamps = load_timestamps(os.path.join(annotation_dir, 'color_timestamps.txt'))
          color_stream_timestamps = load_timestamps(os.path.join(stream_dir, 'color_timestamps.txt'))

          # load the video sequence
          seq = bob.io.video.reader(os.path.join(stream_dir, 'color', 'color.mov'))
          sequence = seq.load()
          n_sequences += 1

          # empty the lists
          del yaw_small[:]
          del yaw_left[:]
          del yaw_right[:]
          del pitch_small[:]
          del pitch_top[:]
          del pitch_bottom[:]

          # loop on the different annotations, defining pose intervals
          indices = range(1,13,1)
          for i in indices :
            
            # the folder where images will be stored depend on the annotation index

            # retrieve the past timestamps  - up to the previous annotated image 
            previous_stamps = retrieve_past_timestamps(color_annotations_timestamps[i], color_stream_timestamps, color_annotations_timestamps[i-1])
            
            # get the frames in the interval
            counter = 0
            for index in sorted(previous_stamps, reverse=True):

              # check the eligibility conditions on this frame 
              if previous_stamps[index] > color_annotations_timestamps[i-1] and counter < 5:
                
                # put this image in the correct list
                if i == 1 or i == 4: yaw_small.append(sequence[index])
                if i == 2 or i == 3: yaw_left.append(sequence[index])
                if i == 5 or i== 6: yaw_right.append(sequence[index])
                if i == 7 or i == 10: pitch_small.append(sequence[index])
                if i == 8 or i == 9: pitch_top.append(sequence[index])
                if i == 11 or i == 12: pitch_bottom.append(sequence[index])
              
              counter += 1

          # save images for this sequence
          folders = ['yaw_small', 'yaw_left', 'yaw_right', 'pitch_small', 'pitch_top', 'pitch_bottom']
          for folder in folders:

            to_save_dir = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'color', folder) 
            if not os.path.isdir(os.path.join(to_save_dir)):
              os.makedirs(to_save_dir)
            
            current_list = []
            if folder == 'yaw_small': current_list = yaw_small
            if folder == 'yaw_left': current_list = yaw_left
            if folder == 'yaw_right': current_list = yaw_right
            if folder == 'pitch_small': current_list = pitch_small
            if folder == 'pitch_top': current_list = pitch_top
            if folder == 'pitch_bottom': current_list = pitch_bottom

            k = 0
            for image in current_list:
              saved_image = os.path.join(to_save_dir, '{:0>2d}.png'.format(k))
              bob.io.base.save(image, saved_image)

              if bool(args['--plot']):
                from matplotlib import pyplot
                pyplot.imshow(numpy.rollaxis(numpy.rollaxis(image, 2),2))
                pyplot.title('image {0} for interval {1}'.format(k, folder))
                pyplot.show()
 
              k += 1
            
          # update stats with this sequence
          yaw_small_counter += len(yaw_small)
          yaw_left_counter += len(yaw_left)
          yaw_right_counter += len(yaw_right)
          pitch_small_counter += len(pitch_small)
          pitch_top_counter += len(pitch_top)
          pitch_bottom_counter += len(pitch_bottom)
          print "yaw_small_counter = {0}".format(yaw_small_counter)


  f = open('stats.txt', 'w')
  f.write("===== YAW =====\n")
  write_stat(f, 'yaw_small', yaw_small_counter, n_sequences)
  write_stat(f, 'yaw_left', yaw_left_counter, n_sequences)
  write_stat(f, 'yaw_right', yaw_right_counter, n_sequences)
  write_stat(f, 'pitch_small', pitch_small_counter, n_sequences)
  write_stat(f, 'pitch_top', pitch_top_counter, n_sequences)
  write_stat(f, 'pitch_bottom', pitch_bottom_counter, n_sequences)
  f.close()

  from matplotlib import pyplot
  
  yaw = (yaw_right_counter, yaw_small_counter, yaw_left_counter)
  pitch = (pitch_bottom_counter, pitch_small_counter, pitch_top_counter)

  n_groups = 3
  index = numpy.arange(n_groups)
  bar_width = 0.5
  opacity = 0.4
  
  pyplot.bar(index, yaw, bar_width, alpha=opacity, color='b', label='Yaw')
  pyplot.xticks(index, ('left', '~frontal', 'right'))
  pyplot.title('Yaw')
  pyplot.savefig('stats-yaw.png')

  pyplot.figure()
  pyplot.bar(index, pitch, bar_width, alpha=opacity, color='b', label='Pitch')
  pyplot.xticks(index, ('top', '~frontal', 'bottom'))
  pyplot.title('Pitch')
  pyplot.savefig('stats-pitch.png')
