#!/usr/bin/env python
# encoding: utf-8

import bob.bio.base
from bob.bio.face.database import FaceBioFile

class Database(bob.bio.base.database.FileListBioDatabase):
  """Wrapper class for the FARGO database for face verification
  """

  def __init__(self, original_directory=None, original_extension=None, **kwargs):
    # call base class constructor
    from pkg_resources import resource_filename
    folder = resource_filename(__name__, 'lists')
    super(Database, self).__init__(folder, 'fargo', bio_file_class=FaceBioFile,
                                   original_directory=original_directory,
                                   original_extension=original_extension, **kwargs)

