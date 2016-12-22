#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Thu 22 Dec 16:20:02 CET 2016

import bob.db.bio_filelist

class Database(bob.db.bio_filelist.Database):
  """Wrapper class for the FARGO database for face verification
  """

  def __init__(self, original_directory = None, original_extension = None):
    # call base class constructor
    from pkg_resources import resource_filename
    lists = resource_filename(__name__, 'lists')
    bob.db.bio_filelist.Database.__init__(self, lists, original_directory = original_directory, original_extension = original_extension)

