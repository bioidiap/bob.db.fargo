#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 21 Nov 08:25:54 CET 2016

"""Image extractor for the FARGO videos (%(version)s)

Usage:
  %(prog)s [--dbdir=<path>] [--imagesdir=<path>] [--mod=<string>] 
           [--verbose ...] [--plot]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -d, --dbdir=<path>        The path to the database on your disk.
  -i, --imagesdir=<path>    Where to store saved images.
  -m, --mod=<int>           The used modality (RGB, NIR, depth) [default: RGB].
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


def check_if_recording_is_ok(images_dir, subject, session, condition, recording, channel):
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

    ``channel`` (string):
      The channel (color or ir or depth)

  **Returns**

    ``[True, False]`` (bool)
  """
  base_path = os.path.join(images_dir, subject, session, condition, recording)

  folders = []
  folders.append('yaw')
  folders.append('pitch')
  for folder in folders:
    if not os.path.isdir(os.path.join(base_path, channel, folder)):
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
  diff = sys.maxsize
  for index in streams_stamps:
    if (streams_stamps[index] > prev_timestamp) and (streams_stamps[index] <= ref_timestamp):
      previous_stamps[index] = streams_stamps[index]
  return previous_stamps

def write_stat(f, pose_text, pose_cluster, n_total_sequences):
  mean_images = pose_cluster / float(n_total_sequences)
  f.write("mean # of images at {0} = {1} ({2} / {3})\n".format(pose_text, mean_images, pose_cluster, n_total_sequences))


def pre_process_depth(depth_data):
  """pre_process_depth(depth_data) -> new_depth_data
  This function preprocess depth data and return an image

  **Parameters**

    ``depth_data`` (numpy array):
      The data coming from the depth channel 

  **Returns**

    ``new_depth_data`` (numpy array)
      The preprocessed depth data, ready to be saved as an image
  """
  # get background / foreground (i.e. zero-valued pixels are considered as background)
  background = numpy.where(depth_data <= 0)
  foreground = numpy.where(depth_data > 0)

  # sometimes there is no foreground ...
  if foreground[0].size == 0:
    new_depth_data = numpy.zeros(depth_data.shape, depth_data.dtype)
  else:
    # trick such that the highest value is the closest to the sensor
    depth_data = depth_data * (-1)
    max_significant = numpy.max(depth_data[foreground])
    min_significant = numpy.min(depth_data[foreground])

    # normalize to 0-255 and set background to zero
    new_depth_data = 255 * ((depth_data - min_significant) / float(max_significant -  min_significant))
    new_depth_data[background] = 0

  return new_depth_data


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

  if not (args['--mod'] == 'RGB' or args['--mod'] == 'NIR' or args['--mod'] == 'depth'): 
    logger.warning("Please provide a valid modality, {0} is not !".format(args['--mod']))
    sys.exit()
  
  # get the modality and the channel
  if args['--mod'] == 'RGB':
    modality = 'RGB'
    channel = 'color'
  if args['--mod'] == 'NIR':
    modality = 'NIR'
    channel = 'ir'
  if args['--mod'] == 'depth':
    modality = 'depth'
    channel = 'depth'
  
  # lists for pose cluster
  yaw = []
  pitch = []

  # stats on pose clusters 
  n_sequences = 0
  yaw_counter = 0
  pitch_counter = 0

  for subject in os.listdir(base_dir):

    #sessions = ['controlled', 'dark', 'outdoor']
    sessions = ['controlled']
    # small hack to process FdV subjects ...
    
    if int(subject) < 26:
      logger.warning("Skipping subject {}".format(subject))
      continue
    
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
          if not os.path.isdir(os.path.join(args['--imagesdir'], subject, session, condition, recording, channel)):
            os.makedirs(os.path.join(args['--imagesdir'], subject, session, condition, recording, channel))

          # check if the recording has already been processed, and if so, that everything is ok  
          if check_if_recording_is_ok(args['--imagesdir'], subject, session, condition, recording, channel):
            logger.info("recording already processed and ok")
            continue

          # load the files with the timestamps
          annotations_timestamps = load_timestamps(os.path.join(annotation_dir, channel + '_timestamps.txt'))
          stream_timestamps = load_timestamps(os.path.join(stream_dir, channel + '_timestamps.txt'))

          # load the video sequence
          if channel == 'color':
            seq = bob.io.video.reader(os.path.join(stream_dir, 'color', 'color.mov'))
            sequence = seq.load()
          if channel == 'ir':
            # uncompress the 7z archive - ir - if needed
            ir_dir = os.path.join(stream_dir, 'ir')
            if (len(os.listdir(ir_dir))) == 1 and ('ir.7z' in os.listdir(ir_dir)):
              logger.debug("uncompressing NIR")
              ir_compressed = os.path.join(ir_dir, 'ir.7z')
              command = "7z x -y -o" + ir_dir + ' ' + ir_compressed
              try:
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdoutdata, stderrdata = p.communicate()
              except:
                pass
          if channel == 'depth':
            # uncompress the 7z archive - depth - if needed
            depth_dir = os.path.join(stream_dir, 'depth')
            if (len(os.listdir(depth_dir))) == 1 and ('depth.7z' in os.listdir(depth_dir)):
              logger.debug("uncompressing depth")
              depth_compressed = os.path.join(depth_dir, 'depth.7z')
              command = "7z x -y -o" + depth_dir + ' ' + depth_compressed
              try:
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdoutdata, stderrdata = p.communicate()
              except:
                pass

          
          n_sequences += 1

          # empty the lists
          del yaw[:]
          del pitch[:]

          # loop on the different annotations, defining pose intervals
          indices = range(1,13,1)
          for i in indices :
            
            # the folder where images will be stored depend on the annotation index

            # retrieve the past timestamps  - up to the previous annotated image 
            previous_stamps = retrieve_past_timestamps(annotations_timestamps[i], stream_timestamps, annotations_timestamps[i-1])
            
            # get the frames in the interval
            counter = 0
            for index in sorted(previous_stamps, reverse=True):

              # check the eligibility conditions on this frame 
              if previous_stamps[index] > annotations_timestamps[i-1] and counter < 5:
                
                # put this image in the correct list

                # yaw small
                #if i == 1 or i == 4: 
                #  if channel == 'color':
                #    yaw_small.append(sequence[index])
                #  if channel == 'ir':
                #    ir_file = os.path.join(ir_dir, '{0}.bin'.format(index))
                #    ir_data = numpy.fromfile(ir_file, dtype=numpy.int16).reshape(-1, 640)
                #    ir_image = ir_data / 4.0 
                #    yaw_small.append(ir_image)
                #  if channel == 'depth':
                #    depth_file = os.path.join(depth_dir, '{0}.bin'.format(index))
                #    depth_data = numpy.fromfile(depth_file, dtype=numpy.int16).reshape(-1, 640)
                #    depth_image = pre_process_depth(depth_data)
                #    yaw_small.append(depth_image)
                
                # yaw left
                if i == 2 or i == 3: 
                  if channel == 'color':
                    yaw.append(sequence[index])
                  #if channel == 'ir':
                  #  ir_file = os.path.join(ir_dir, '{0}.bin'.format(index))
                  #  ir_data = numpy.fromfile(ir_file, dtype=numpy.int16).reshape(-1, 640)
                  #  ir_image = ir_data / 4.0 
                  #  yaw_left.append(ir_image)
                  #if channel == 'depth':
                  #  depth_file = os.path.join(depth_dir, '{0}.bin'.format(index))
                  #  depth_data = numpy.fromfile(depth_file, dtype=numpy.int16).reshape(-1, 640)
                  #  depth_image = pre_process_depth(depth_data)
                  #  yaw_left.append(depth_image)
                
                # yaw right
                if i == 5 or i== 6: 
                  if channel == 'color':
                    yaw.append(sequence[index])
                  #if channel == 'ir':
                  #  ir_file = os.path.join(ir_dir, '{0}.bin'.format(index))
                  #  ir_data = numpy.fromfile(ir_file, dtype=numpy.int16).reshape(-1, 640)
                  #  ir_image = ir_data / 4.0 
                  #  yaw_right.append(ir_image)
                  #if channel == 'depth':
                  #  depth_file = os.path.join(depth_dir, '{0}.bin'.format(index))
                  #  depth_data = numpy.fromfile(depth_file, dtype=numpy.int16).reshape(-1, 640)
                  #  depth_image = pre_process_depth(depth_data)
                  #  yaw_right.append(depth_image)
                
                # pitch small
                #if i == 7 or i == 10: 
                #  if channel == 'color':
                #    pitch_small.append(sequence[index])
                #  if channel == 'ir':
                #    ir_file = os.path.join(ir_dir, '{0}.bin'.format(index))
                #    ir_data = numpy.fromfile(ir_file, dtype=numpy.int16).reshape(-1, 640)
                #    ir_image = ir_data / 4.0 
                #    pitch_small.append(ir_image)
                #  if channel == 'depth':
                #    depth_file = os.path.join(depth_dir, '{0}.bin'.format(index))
                #    depth_data = numpy.fromfile(depth_file, dtype=numpy.int16).reshape(-1, 640)
                #    depth_image = pre_process_depth(depth_data)
                #    pitch_small.append(depth_image)
                
                # pitch top
                if i == 8 or i == 9: 
                  if channel == 'color':
                    pitch.append(sequence[index])
                  #if channel == 'ir':
                  #  ir_file = os.path.join(ir_dir, '{0}.bin'.format(index))
                  #  ir_data = numpy.fromfile(ir_file, dtype=numpy.int16).reshape(-1, 640)
                  #  ir_image = ir_data / 4.0 
                  #  pitch_top.append(ir_image)
                  #if channel == 'depth':
                  #  depth_file = os.path.join(depth_dir, '{0}.bin'.format(index))
                  #  depth_data = numpy.fromfile(depth_file, dtype=numpy.int16).reshape(-1, 640)
                  #  depth_image = pre_process_depth(depth_data)
                  #  pitch_top.append(depth_image)
                
                # pitch bottom
                if i == 11 or i == 12: 
                  if channel == 'color':
                    pitch.append(sequence[index])
                  #if channel == 'ir':
                  #  ir_file = os.path.join(ir_dir, '{0}.bin'.format(index))
                  #  ir_data = numpy.fromfile(ir_file, dtype=numpy.int16).reshape(-1, 640)
                  #  ir_image = ir_data / 4.0 
                  #  pitch_bottom.append(ir_image)
                  #if channel == 'depth':
                  #  depth_file = os.path.join(depth_dir, '{0}.bin'.format(index))
                  #  depth_data = numpy.fromfile(depth_file, dtype=numpy.int16).reshape(-1, 640)
                  #  depth_image = pre_process_depth(depth_data)
                  #  pitch_bottom.append(depth_image)
                
              
              counter += 1

          # save images for this sequence
          folders = ['yaw', 'pitch']
          for folder in folders:

            to_save_dir = os.path.join(args['--imagesdir'], subject, session, condition, recording, channel, folder) 
            if not os.path.isdir(os.path.join(to_save_dir)):
              os.makedirs(to_save_dir)
            
            current_list = []
            if folder == 'yaw': current_list = yaw
            if folder == 'pitch': current_list = pitch

            k = 0
            for image in current_list:
              saved_image = os.path.join(to_save_dir, '{:0>2d}.png'.format(k))
              if channel == 'color':
                bob.io.base.save(image, saved_image)
              else:
                bob.io.base.save(image.astype('uint8'), saved_image)

              if bool(args['--plot']):
                from matplotlib import pyplot
                if channel == 'color':
                  pyplot.imshow(numpy.rollaxis(numpy.rollaxis(image, 2),2))
                else:
                  pyplot.imshow(image, cmap='gray')
                pyplot.title('image {0} for interval {1}'.format(k, folder))
                pyplot.show()
 
              k += 1
            
          # update stats with this sequence
          yaw_counter += len(yaw)
          pitch_counter += len(pitch)


  f = open('stats.txt', 'w')
  write_stat(f, 'yaw', yaw_counter, n_sequences)
  write_stat(f, 'pitch', pitch_counter, n_sequences)
  f.close()

  #from matplotlib import pyplot
  #
  #yaw = (yaw_right_counter, yaw_small_counter, yaw_left_counter)
  #pitch = (pitch_bottom_counter, pitch_small_counter, pitch_top_counter)

  #n_groups = 3
  #index = numpy.arange(n_groups)
  #bar_width = 0.5
  #opacity = 0.4
  #
  #pyplot.bar(index, yaw, bar_width, alpha=opacity, color='b', label='Yaw')
  #pyplot.xticks(index, ('left', '~frontal', 'right'))
  #pyplot.title('Yaw')
  #pyplot.savefig('stats-yaw.png')

  #pyplot.figure()
  #pyplot.bar(index, pitch, bar_width, alpha=opacity, color='b', label='Pitch')
  #pyplot.xticks(index, ('top', '~frontal', 'bottom'))
  #pyplot.title('Pitch')
  #pyplot.savefig('stats-pitch.png')
