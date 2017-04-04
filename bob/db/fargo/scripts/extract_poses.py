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
  folders.append('10degreesleft')
  folders.append('20degreesleft')
  folders.append('30degreesleft')
  folders.append('10degreesright')
  folders.append('20degreesright')
  folders.append('30degreesright')
  folders.append('10degreestop')
  folders.append('20degreestop')
  folders.append('30degreestop')
  folders.append('10degreesbottom')
  folders.append('20degreesbottom')
  folders.append('30degreesbottom')
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

  # stats on pose cluster 
  n_sequences = 0
  ten_degrees_left = 0
  twenty_degrees_left = 0
  thirty_degrees_left = 0
  ten_degrees_right = 0
  twenty_degrees_right = 0
  thirty_degrees_right = 0
  ten_degrees_top = 0
  twenty_degrees_top = 0
  thirty_degrees_top = 0
  ten_degrees_bottom = 0
  twenty_degrees_bottom = 0
  thirty_degrees_bottom = 0

  # go through the subjects 
  #subjects = []
  #subjects_ids = range(1, 2, 1)
  #for subject in subjects_ids:
  #  subjects.append('{:0>3d}'.format(subject))
  #for subject in subjects:
  
  for subject in os.listdir(base_dir):

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

          # loop on the different annotations, defining pose intervals
          indices = range(1,13,1)
          for i in indices :
            
            # the folder where images will be stored depend on the annotation index
            folder = ''
            if i == 1: folder = '10degreesleft'
            if i == 2: folder = '20degreesleft'
            if i == 3: folder = '30degreesleft'
            if i == 4: folder = '10degreesright'
            if i == 5: folder = '20degreesright'
            if i == 6: folder = '30degreesright'
            if i == 7: folder = '10degreestop'
            if i == 8: folder = '20degreestop'
            if i == 9: folder = '30degreestop'
            if i == 10: folder = '10degreesbottom'
            if i == 11: folder = '20degreesbottom'
            if i == 12: folder = '30degreesbottom'

            # retrieve the past timestamps  - up to the previous annotated image 
            previous_stamps = retrieve_past_timestamps(color_annotations_timestamps[i], color_stream_timestamps, color_annotations_timestamps[i-1])
            logger.debug("there are {0} frames in cluster {1}".format(len(previous_stamps), folder))
            
            # get the frames in the interval
            counter = 0
            for index in sorted(previous_stamps, reverse=True):

              # check the eligibility conditions on this frame 
              if previous_stamps[index] > color_annotations_timestamps[i-1] and counter < 5:
                
                # save this image
                to_save_dir = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'color', folder)
                if not os.path.isdir(os.path.join(to_save_dir)):
                  os.makedirs(to_save_dir)
                saved_image = os.path.join(to_save_dir, '{:0>2d}.png'.format(counter))
                bob.io.base.save(sequence[index], saved_image)
             
                # plot stuff if asked for
                if bool(args['--plot']):
                  from matplotlib import pyplot
                  pyplot.imshow(numpy.rollaxis(numpy.rollaxis(sequence[index], 2),2))
                  pyplot.title('image {0} for interval {1}'.format(counter, folder))
                  pyplot.show()

                # save some stats
                if i == 1: ten_degrees_left += 1
                if i == 2: twenty_degrees_left += 1
                if i == 3: thirty_degrees_left += 1
                if i == 4: ten_degrees_right += 1
                if i == 5: twenty_degrees_right += 1
                if i == 6: thirty_degrees_right += 1
                if i == 7: ten_degrees_top += 1
                if i == 8: twenty_degrees_top += 1
                if i == 9: thirty_degrees_top += 1
                if i == 10: ten_degrees_bottom += 1
                if i == 11: twenty_degrees_bottom += 1
                if i == 12: thirty_degrees_bottom += 1

                # increment the counter of saved images
                counter += 1
  
  f = open('stats.txt', 'w')
  f.write("===== YAW =====\n")
  write_stat(f, '10 left', ten_degrees_left, n_sequences)
  write_stat(f, '20 left', twenty_degrees_left, n_sequences)
  write_stat(f, '30 left', thirty_degrees_left, n_sequences)
  write_stat(f, '10 right', ten_degrees_right, n_sequences)
  write_stat(f, '20 right', twenty_degrees_right, n_sequences)
  write_stat(f, '30 right', thirty_degrees_right, n_sequences)
  f.write("===== PITCH =====\n")
  write_stat(f, '10 top', ten_degrees_top, n_sequences)
  write_stat(f, '20 top', twenty_degrees_top, n_sequences)
  write_stat(f, '30 top', thirty_degrees_top, n_sequences)
  write_stat(f, '10 bottom', ten_degrees_bottom, n_sequences)
  write_stat(f, '20 bottom', twenty_degrees_bottom, n_sequences)
  write_stat(f, '30 bottom', thirty_degrees_bottom, n_sequences)
  f.close()

  from matplotlib import pyplot
  
  yaw = (thirty_degrees_right, twenty_degrees_right, ten_degrees_right, ten_degrees_left, twenty_degrees_left, thirty_degrees_left)
  pitch = (thirty_degrees_top, twenty_degrees_top, ten_degrees_top, ten_degrees_bottom, twenty_degrees_bottom, thirty_degrees_bottom)

  n_groups = 6
  index = numpy.arange(n_groups)
  bar_width = 0.5
  opacity = 0.4
  
  pyplot.bar(index, yaw, bar_width, alpha=opacity, color='b', label='Yaw')
  pyplot.xticks(index, ('-30', '-20', '-10', '10', '20', '30'))
  pyplot.title('Yaw')
  pyplot.savefig('stats-yaw.png')

  pyplot.figure()
  pyplot.bar(index, pitch, bar_width, alpha=opacity, color='b', label='Pitch')
  pyplot.xticks(index, ('-30', '-20', '-10', '10', '20', '30'))
  pyplot.title('Pitch')
  pyplot.savefig('stats-pitch.png')
