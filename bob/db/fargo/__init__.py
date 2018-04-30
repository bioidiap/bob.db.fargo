#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Thu 22 Dec 16:16:15 CET 2016


from .query import Database
import bob.io.image
#from bob.bio.base.database.filelist.models import FileListFile, Client
from bob.bio.base.database.filelist.models import FileListFile

def get_config():
  """Returns a string containing the configuration information.
  """
  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
