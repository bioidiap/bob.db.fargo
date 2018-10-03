#!/usr/bin/env python
# encoding: utf-8

import os
from bob.db.base import utils
from .models import *

from .driver import Interface
INFO = Interface()
SQLITE_FILE = INFO.files()[0]

import bob.db.base

class Database(bob.db.base.SQLiteDatabase):

  def __init__(self, 
               original_directory=None, 
               original_extension=None,
               annotation_directory=None,
               annotation_extension=None):
    
    super(Database, self).__init__(SQLITE_FILE, File, original_directory, original_extension)

    self.annotation_directory = annotation_directory
    self.annotation_extension = annotation_extension

  def objects(self, protocol='mc-rgb', groups=None, purpose=None):
    """ Return a set of file

    Parameters
    ----------
      protocol: py:obj:str
        One of the protocols
      groups: py:obj:str or py:obj:tuple of py:obj:str
        One of the groups ('train', 'dev', 'eval') or several of them
      purpose: py:obj:str or py:obj:tuple of py:obj:str
        One of the groups ('train', 'enroll', 'probe') or several of them

    Returns
    -------
      py:obj:list
        A list of File

    Raises
    ------

    """
    # protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocols())
    # groups = self.check_parameters_for_validity(groups, "group", self.groups())

    from sqlalchemy import and_
    
    # get all files
    q = self.query(File)

    # filter the modality, based on the protocol (hetereogeneous case will be addressed later)
    if '-rgb' in protocol:
      q = q.filter(File.modality == 'rgb')
    if '-nir' in protocol:
      q = q.filter(File.modality == 'nir')
    if '-depth' in protocol:
      q = q.filter(File.modality == 'depth')
   
    # filter the training set: regardless of the protocol, this is client 1 to 25, controlled and frontal
    q_train = q.filter(and_(File.client_id <= 25, File.light == 'controlled', File.pose == 'frontal'))

    list_train = list(q_train)
    #for i in list_train:
    #  print(i)
    print("number of training images for protocol {} -> {}".format(protocol, len(list_train)))

    # now get enrollment images for both dev and test
    q_enroll = q.filter(and_(File.client_id > 25, File.purpose == 'enroll'))
    list_enroll = list(q_enroll)
    #for i in list_enroll:
    #  print(i)
    #print(len(list_enroll))
    print("number of enrollment images for protocol {} -> {}".format(protocol, len(list_enroll)))

    # now get the probes ...
    q_probe = q.filter(and_(File.client_id > 25, File.purpose == 'probe'))

    if 'mc' in protocol:
      q_probe = q_probe.filter(and_(File.light == 'controlled', File.pose == 'frontal'))
      list_probe = list(q_probe)
    if 'ud' in protocol:
      q_probe = q_probe.filter(and_(File.light == 'dark', File.pose == 'frontal'))
      list_probe = list(q_probe)
    if 'uo' in protocol:
      q_probe = q_probe.filter(and_(File.light == 'outdoor', File.pose == 'frontal'))
      list_probe = list(q_probe)

    
    for i in list_probe:
      print(i)
    print("number of probe images for protocol {} -> {}".format(protocol, len(list_probe)))

