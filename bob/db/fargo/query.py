#!/usr/bin/env python
# encoding: utf-8

import os
from bob.db.base import utils
from .models import *

#from .driver import Interface
#INFO = Interface()
#SQLITE_FILE = INFO.files()[0]

import bob.db.base

class Database(bob.db.base.SQLiteDatabase):

  def __init__(self, 
               original_directory=None, 
               original_extension=None,
               annotation_directory=None,
               annotation_extension=None):
    
    # call base class constructor
    # File -> from models.py
    super(Database, self).__init__(SQLITE_FILE, File, original_directory, original_extension)

    self.annotation_directory = annotation_directory
    self.annotation_extension = annotation_extension

  def objects(self, protocol='mc-rgb', groups=None, modality='rgb'):
    """ Return a set of file

    Parameters
    ----------
      protocol: py:obj:str
        One of the protocols
      groups: py:ojg:str or py:obj:tuple of py:obj:str
        One of the groups ('world', 'dev', 'eval') or several of them

    Returns
    -------
      py:obj:list
        A list of File

    Raises
    ------

    """
    
    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocols())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    
    retval = []

    # training set: all images for the client id 1 to 25, controlled conditions, all device, all recordings 
    if 'train' in groups:
      q = self.query(Client).join(File)
      q = q.filter(Client.set.in_(groups))
      retval += list(q)
