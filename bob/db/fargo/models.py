#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base
import numpy
import bob.io.base
import bob.io.image
import bob.core

logger = bob.core.log.setup('bob.db.fargo')
Base = declarative_base()

# this should be ok
class Client(Base):
  """Database clients, marked by an integer identifier and the set they belong
  to"""

  __tablename__ = 'client'

  set_choices = ('train', 'devel', 'test')
  """Possible groups to which clients may belong to"""

  id = Column(Integer, primary_key=True)
  """Key identifier for clients"""

  set = Column(Enum(*set_choices))
  """Set to which this client belongs to"""

  def __init__(self, id, set):
    self.id = id
    self.set = set

  def __repr__(self):
    return "Client('%s', '%s')" % (self.id, self.set)


class File(Base):
  """Generic file container"""

  __tablename__ = 'file'

  # illumination conditions
  light_choices = ('controlled', 'dark', 'outdoor')
  light = Column(Enum(*light_choices))

  # mounted devices
  device_choices = ('laptop', 'mobile')
  device = Column(Enum(*device_choices))

  # pose
  pose_choices = ('frontal', 'yaw', 'pitch')
  pose = Column(Enum(*pose_choices))

  # modality
  modality_choices = ('rgb', 'nir', 'depth')
  modality = Column(Enum(*modality_choices))

  # shot (i.e. images extracted from the video sequence)
  # TODO: How to handle that with varying number of poses ? - Guillaume HEUSCH, 02-10-2018
  shot_choices = tuple(['{:0>2d}'.format(s) for s in range(10)])
  shot = Column(Enum(*shot_choices))
  
  # key id for files
  id = Column(Integer, primary_key=True)
  """Key identifier for files"""

  # client id of this file
  client_id = Column(Integer, ForeignKey('client.id'))  # for SQL

  # path of this file in the database
  path = Column(String(100), unique=True)

  # for Python
  client = relationship(Client, backref=backref('files', order_by=id))
  """A direct link to the client object that this file belongs to"""

  def __init__(self, client, path, light, device):
    self.client = client
    self.path = path
    self.light = light
    self.device = device
    self.pose = pose
    self.modality = modality
    self.shot = shot

  def __repr__(self):
    return "File('%s')" % self.path

  def make_path(self, directory=None, extension=None):
    """Wraps the current path so that a complete path is formed

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    extension
      An optional extension that will be suffixed to the returned filename. The
      extension normally includes the leading ``.`` character as in ``.jpg`` or
      ``.hdf5``.

    Returns a string containing the newly generated file path.
    """

    if not directory:
      directory = ''
    if not extension:
      extension = ''

    return str(os.path.join(directory, self.path + extension))

