#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.base

import bob.core

logger = bob.core.log.setup('bob.db.fargo')
Base = declarative_base()

# association table between File and ProtocolPurpose
protocolPurpose_file_association = Table('protocolPurpose_file_association', Base.metadata,
  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
  Column('file_id',  Integer, ForeignKey('file.id')))


class Client(Base):
  """Database clients, marked by an integer identifier and the set they belong
  to"""

  __tablename__ = 'client'
  
  id = Column(Integer, primary_key=True)
  
  # Possible groups to which clients may belong to
  group_choices = ('world', 'dev', 'eval')

  # Group to which this client belongs to"""
  group = Column(Enum(*group_choices))

  def __init__(self, id, group):
    self.id = id
    self.group = group

  def __repr__(self):
    return "Client('%s', '%s')" % (self.id, self.group)


class File(Base, bob.db.base.File):
  """Generic file container"""

  __tablename__ = 'file'

  # key id for files
  id = Column(Integer, primary_key=True)

  # client id of this file
  client_id = Column(Integer, ForeignKey('client.id'))  
  # A direct link to the client object that this file belongs to
  client = relationship(Client, backref=backref('files', order_by=id))

  # illumination conditions
  light_choices = ('controlled', 'dark', 'outdoor')
  light = Column(Enum(*light_choices))

  # mounted devices
  device_choices = ('laptop', 'mobile')
  device = Column(Enum(*device_choices))
  
  # recordings
  recording_choices = ('0', '1')
  recording = Column(Enum(*recording_choices))

  # modality
  modality_choices = ('rgb', 'nir', 'depth')
  modality = Column(Enum(*modality_choices))

  # pose
  pose_choices = ('frontal', 'yaw', 'pitch')
  pose = Column(Enum(*pose_choices))

  # path of this file in the database
  path = Column(String(100), unique=True)

  def __init__(self, client_id, path, light, device, pose, modality, recording):
    bob.db.base.File.__init__(self, path=path)
    self.client_id = client_id
    self.light = light
    self.device = device
    self.recording = recording
    self.modality = modality
    self.pose = pose

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

class Protocol(Base):
  """FARGO protocols
  
  """

  __tablename__ = 'protocol'

  id = Column(Integer, primary_key=True)
  name = Column(String(20), unique=True)

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Protocol('%s')" % (self.name,)


class ProtocolPurpose(Base):
  """FARGO protocol purposes"""

  __tablename__ = 'protocolPurpose'

  id = Column(Integer, primary_key=True)
  
  protocol_id = Column(Integer, ForeignKey('protocol.id'))
  group_choices = ('world', 'dev', 'eval')
  group = Column(Enum(*group_choices))
  purpose_choices = ('train', 'enroll', 'probe')
  purpose = Column(Enum(*purpose_choices))

  # protocol: a protocol have 1 to many purpose
  protocol = relationship("Protocol", backref=backref("purposes", order_by=id))
  
  # files: many to many relationship
  files = relationship("File", secondary=protocolPurpose_file_association, backref=backref("protocolPurposes", order_by=id))

  def __init__(self, protocol_id, group, purpose):
    self.protocol_id = protocol_id
    self.group = group
    self.purpose = purpose

  def __repr__(self):
    return "ProtocolPurpose('%s', '%s', '%s')" % (self.protocol.name, self.group, self.purpose)


