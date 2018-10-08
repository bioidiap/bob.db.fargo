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
               annotation_extension=None,
               protocol='mc-rgb'):
    
    super(Database, self).__init__(SQLITE_FILE, File, original_directory, original_extension)

    self.annotation_directory = annotation_directory
    self.annotation_extension = annotation_extension
    self.protocol = protocol

  def objects(self, protocol=None, groups=None, purposes=None, model_ids=None):
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
    if '-rgb' in self.protocol:
      q = q.filter(File.modality == 'rgb')
    if '-nir' in self.protocol:
      q = q.filter(File.modality == 'nir')
    if '-depth' in self.protocol:
      q = q.filter(File.modality == 'depth')
   
    # filter the training set: regardless of the protocol, this is client 1 to 25, controlled and frontal
    q_train = q.filter(and_(File.client_id <= 25, File.light == 'controlled', File.pose == 'frontal'))

    list_train = list(q_train)
    #for i in list_train:
    #  print(i)
    #print("number of training images for protocol {} -> {}".format(self.protocol, len(list_train)))

    # now get enrollment images for both dev and test
    q_enroll = q.filter(and_(File.client_id > 25, File.purpose == 'enroll'))
    list_enroll = list(q_enroll)
    #for i in list_enroll:
    #  print(i)
    #print(len(list_enroll))
    #print("number of enrollment images for protocol {} -> {}".format(self.protocol, len(list_enroll)))

    # now get the probes ...
    q_probe = q.filter(and_(File.client_id > 25, File.purpose == 'probe'))

    if 'mc' in self.protocol:
      q_probe = q_probe.filter(and_(File.light == 'controlled', File.pose == 'frontal'))
      list_probe = list(q_probe)
    if 'ud' in self.protocol:
      q_probe = q_probe.filter(and_(File.light == 'dark', File.pose == 'frontal'))
      list_probe = list(q_probe)
    if 'uo' in self.protocol:
      q_probe = q_probe.filter(and_(File.light == 'outdoor', File.pose == 'frontal'))
      list_probe = list(q_probe)

    #for i in list_probe:
    #  print(i)
    #print("number of probe images for protocol {} -> {}".format(self.protocol, len(list_probe)))
    
    
    final_list = []
    if 'train' in groups:
      final_list += list_train
    
    # development set: ids 26 to 50, enroll and probe
    if 'dev' in groups:
      q_dev_enroll = q_enroll.filter(File.client_id <= 50)
      q_dev_probe = q_probe.filter(File.client_id <= 50)
      list_dev = list(q_dev_enroll) + list(q_dev_probe)
      if purposes is not None and 'enroll' in purposes:
        list_dev = list(q_dev_enroll) 
      if purposes is not None and 'probe' in purposes:
        list_dev = list(q_dev_probe)
      final_list += list_dev

    # evaluation set: ids 51 to 75, enroll and probe
    if 'eval' in groups:
      q_eval_enroll = q_enroll.filter(File.client_id > 50)
      q_eval_probe = q_probe.filter(File.client_id > 50)
      list_eval = list(q_eval_enroll) + list(q_eval_probe)
      if purposes is not None and 'enroll' in purposes:
        list_eval = list(q_eval_enroll) 
      if purposes is not None and 'probe' in purposes:
        list_eval =  list(q_eval_probe)
      final_list += list_eval

    return final_list


  def model_ids(self, groups=None, protocol=None, **kwargs): 
    
    ids = []
    if 'train' in groups:
      ids += list(range(26))
    if 'dev' in groups:
      ids += list(range(26, 51))
    if 'eval' in groups:
      ids += list(range(51, 76))

    return ids
