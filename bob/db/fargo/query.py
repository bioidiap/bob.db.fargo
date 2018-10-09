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

  def groups(self, protocol=None):     
    """Returns the names of all registered groups"""   

    return ProtocolPurpose.group_choices


  def clients(self, protocol=None, groups=None):
    """Returns a set of clients for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored since the clients are identical for all protocols.

    groups
      The groups to which the clients belong ('world', 'dev', 'eval').

    Returns: A list containing all the clients which have the given properties.
    """

    groups = self.check_parameters_for_validity(groups, "group", self.groups())

    retval = []
    # List of the clients
    if "world" in groups:
      q = self.query(Client).filter(Client.group == 'world')
      retval += list(q)
    if 'dev' in groups:
      q = self.query(Client).filter(Client.group == 'dev')
      retval += list(q)
    if 'eval' in groups:
      q = self.query(Client).filter(Client.group == 'eval')
      retval += list(q)

    return retval

  def models(self, protocol=None, groups=None):
    """Returns a set of models for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored since the models are identical for all protocols.

    groups
      The groups to which the subjects attached to the models belong

    Returns: A list containing all the models which have the given properties.
    """
    return self.clients(protocol, groups)

  def model_ids(self, protocol=None, groups=None):
    """Returns a set of models ids for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored since the models are identical for all protocols.

    groups
      The groups to which the subjects attached to the models belong ('g1', 'g2', 'world')
      Note that 'dev' is an alias to 'g1' and 'eval' an alias to 'g2'

    Returns: A list containing all the models ids which have the given properties.
    """
    return [model.id for model in self.models(protocol, groups)]

  def client(self, id):
    """Returns the client object in the database given a certain id. Raises
    an error if that does not exist."""

    return self.query(Client).filter(Client.id == id).one()
 

  def protocol_names(self):
    """Returns all registered protocol names"""

    l = self.protocols()
    retval = [str(k.name) for k in l]
    return retval

  def protocols(self):
    """Returns all registered protocols"""

    return list(self.query(Protocol))
 
  def purposes(self):
    return ProtocolPurpose.purpose_choices

  def objects(self, protocol=None, purposes=None, model_ids=None, groups=None):
    """Returns a set of Files for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the FARGO protocols.

    purposes
      The purposes required to be retrieved ('enroll', 'probe', 'train') or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. This field is
      ignored for the data from the "world" group.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      One of the groups ('dev', 'eval', 'world') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    Returns: A list of files which have the given properties.
    """

    #print("Protocol = {}, purpose = {}, model_ids = {}, groups = {}".format(protocol, purposes, model_ids, groups))
    from sqlalchemy import and_

    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids, collections.Iterable)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    if 'world' in groups:
      q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol)
      q = q.filter(Client.group == 'world').filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.group == 'world'))
      if model_ids:
        q = q.filter(Client.id.in_(model_ids))
      q = q.order_by(File.client_id)
      retval += list(q)

    if ('dev' in groups or 'eval' in groups):

      if('enroll' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.group.in_(groups), ProtocolPurpose.purpose == 'enroll'))
        if model_ids:
          q = q.filter(Client.id.in_(model_ids))
        q = q.order_by(File.client_id)
        retval += list(q)

      # dense probing -> don't filter by model_ids
      if('probe' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.group.in_(groups), ProtocolPurpose.purpose == 'probe'))
        q = q.order_by(File.client_id)
        retval += list(q)

    return list(set(retval))  # To remove duplicates

