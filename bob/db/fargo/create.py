#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
from .models import *

from bob.db.base.driver import Interface as BaseInterface


import bob.core
logger = bob.core.log.setup('bob.db.fargo')


def add_clients(session, imagesdir):
  """Add clients

  This function add clients to the database. 

  Parameters
  ----------
  imagesdir : :py:obj:str
    The directory where the images have been extracted
  verbose : bool
    Print some information

  """
  for d in os.listdir(imagesdir):
    client_id = int(d)
    if client_id <= 25:
      group = 'train'
    elif client_id <= 50:
      group = 'dev'
    else:
      group = 'eval'
    logger.info("Adding client {} in group {}".format(client_id, group))
    session.add(Client(client_id, group))

def add_files(session, imagesdir, extension='.png'):
  """ Add face images files

  """
  id_file = 1

  for root, dirs, files in os.walk(imagesdir, topdown=False):
    for name in files:
      image_filename = os.path.join(root, name)

      # just to make sure that nothing weird will be added
      if os.path.splitext(image_filename)[1] == extension:

        # get all the info, base on the file path
        image_info = image_filename.replace(imagesdir, '')
        infos = image_info.split('/')
        
        client_id = int(infos[0])
        light = infos[1]
        device = infos[2].replace('SR300-', '')
        recording = infos[3]
        stream = infos[4]
        if stream == 'color': modality = 'rgb'
        if stream == 'ir': modality = 'nir'
        if stream == 'depth': modality = 'depth'
        
        # default pose is frontal
        pose = 'frontal'
        if 'yaw' in image_filename:
          pose = 'yaw'
        if 'pitch' in image_filename:
          pose = 'pitch'
        
        shot = int(os.path.splitext(os.path.split(image_info)[1])[0])
        stem = image_info[0:-len(extension)]
        
        logger.info("Adding file {}: ID={}, light={}, device={}, pose={}, mod={}, rec={}, image #{}".format(stem, client_id, light, device, pose, modality, recording, shot))
        o = File(id_file=id_file, client_id=client_id, path=stem, light=light, device=device, pose=pose, modality=modality, recording=recording)
        session.add(o)
        id_file +=1


def create_tables(args):
    """Creates all necessary tables (only to be used at the first time)"""

    from bob.db.base.utils import create_engine_try_nolock
    engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
    Base.metadata.create_all(engine)


# Driver API
# ==========

def create(args):
  """Creates or re-creates this database"""

  from bob.db.base.utils import session_try_nolock

  print(args)
  dbfile = args.files[0]

  if args.recreate:
    if args.verbose and os.path.exists(dbfile):
      print(('unlinking %s...' % dbfile))
    if os.path.exists(dbfile):
      os.unlink(dbfile)

  if not os.path.exists(os.path.dirname(dbfile)):
    os.makedirs(os.path.dirname(dbfile))

  bob.core.log.set_verbosity_level(logger, args.verbose)

  # the real work...
  create_tables(args)
  s = session_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2))
  add_clients(s, args.imagesdir)
  add_files(s, args.imagesdir)
  s.commit()
  s.close()

  return 0


def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', default=False,
                      help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', default=0,
                      help="Do SQL operations in a verbose way")
  parser.add_argument('-i', '--imagesdir', action='store',
                      default='/idiap/temp/heusch/bob.project.fargo/images/',
                      metavar='DIR',
                      help="Change the path to the extracted images of the FARGO database (defaults to %(default)s)")

  parser.set_defaults(func=create)  # action
