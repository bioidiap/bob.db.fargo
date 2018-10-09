#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Fri 23 Dec 09:49:48 CET 2016


"""A few checks on the protocols of the FARGO public database 
"""
import os, sys
import bob.db.fargo

def db_available(test):
  """Decorator for detecting if the database file is available"""
  from bob.io.base.test_utils import datafile
  from nose.plugins.skip import SkipTest
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):
    dbfile = datafile("db.sql3", __name__, None)
    if os.path.exists(dbfile):
      return test(*args, **kwargs)
    else:
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'fargo'))

  return wrapper


@db_available
def test_clients():

  # test whether the correct number of clients is returned
  db = bob.db.fargo.Database()
  assert len(db.groups()) == 3
  assert len(db.clients()) == 75
  assert len(db.clients(groups='world')) == 25
  assert len(db.clients(groups='dev')) == 25
  assert len(db.clients(groups='eval')) == 25


@db_available
def test_objects():
#  # tests if the right number of File objects is returned
  
  db = bob.db.fargo.Database()

  assert len(db.objects(protocol='mc-rgb', groups='world')) == 1000
  assert len(db.objects(protocol='mc-rgb', groups='dev', purposes='enroll')) == 500
  assert len(db.objects(protocol='mc-rgb', groups='dev', purposes='enroll', model_ids=26)) == 20
  assert len(db.objects(protocol='mc-rgb', groups='dev', purposes='probe')) == 500
  assert len(db.objects(protocol='mc-rgb', groups='dev', purposes='probe', model_ids=26)) == 500 # dense probing
  assert len(db.objects(protocol='mc-rgb', groups='eval', purposes='enroll')) == 500
  assert len(db.objects(protocol='mc-rgb', groups='eval', purposes='enroll', model_ids=51)) == 20
  assert len(db.objects(protocol='mc-rgb', groups='eval', purposes='probe')) == 500
  assert len(db.objects(protocol='mc-rgb', groups='eval', purposes='probe', model_ids=51)) == 500 # dense probing

  assert len(db.objects(protocol='ud-nir', groups='world')) == 1000
  assert len(db.objects(protocol='ud-nir', groups='dev', purposes='enroll')) == 500
  assert len(db.objects(protocol='ud-nir', groups='dev', purposes='enroll', model_ids=26)) == 20
  assert len(db.objects(protocol='ud-nir', groups='dev', purposes='probe')) == 1000
  assert len(db.objects(protocol='ud-nir', groups='dev', purposes='probe', model_ids=26)) == 1000 # dense probing
  assert len(db.objects(protocol='ud-nir', groups='eval', purposes='enroll')) == 500
  assert len(db.objects(protocol='ud-nir', groups='eval', purposes='enroll', model_ids=51)) == 20
  assert len(db.objects(protocol='ud-nir', groups='eval', purposes='probe')) == 1000
  assert len(db.objects(protocol='ud-nir', groups='eval', purposes='probe', model_ids=51)) == 1000 # dense probing

  assert len(db.objects(protocol='uo-depth', groups='world')) == 1000
  assert len(db.objects(protocol='uo-depth', groups='dev', purposes='enroll')) == 500
  assert len(db.objects(protocol='uo-depth', groups='dev', purposes='enroll', model_ids=26)) == 20
  assert len(db.objects(protocol='uo-depth', groups='dev', purposes='probe')) == 1000
  assert len(db.objects(protocol='uo-depth', groups='dev', purposes='probe', model_ids=26)) == 1000 # dense probing
  assert len(db.objects(protocol='uo-depth', groups='eval', purposes='enroll')) == 500
  assert len(db.objects(protocol='uo-depth', groups='eval', purposes='enroll', model_ids=51)) == 20
  assert len(db.objects(protocol='uo-depth', groups='eval', purposes='probe')) == 1000
  assert len(db.objects(protocol='uo-depth', groups='eval', purposes='probe', model_ids=51)) == 1000 # dense probing
