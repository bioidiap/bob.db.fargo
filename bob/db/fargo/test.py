#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Fri 23 Dec 09:49:48 CET 2016


"""A few checks on the protocols of the FARGO public database 
"""
from .query import Database
from bob.bio.base.test.test_database_implementations import check_database

#def test_fargo():
#    db = Database() 
#    check_database(db, protocol='mc-rgb', groups=('dev', 'eval'))

def test_query_public_MC_RGB():
  """
  Test some queries for the public MC RGB protocol
  """
  db = Database()
  db.objects(protocol='uo-rgb', groups ='train')


 # assert len(db.client_ids(protocol='public_MC_RGB')) == 75 # 75 client ids for world, dev and eval
 # assert len(db.client_ids(protocol='public_MC_RGB', groups='world')) == 25 # 25 client ids for world
 # assert len(db.client_ids(protocol='public_MC_RGB', groups='dev')) == 25 # 25 client ids for dev
 # assert len(db.client_ids(protocol='public_MC_RGB', groups='eval')) == 25 # 25 client ids for eval

 # assert len(db.model_ids_with_protocol(protocol='public_MC_RGB')) == 75 # 75 model ids for world, dev and eval
 # assert len(db.model_ids_with_protocol(protocol='public_MC_RGB', groups='world')) == 25 # 25 model ids for world
 # assert len(db.model_ids_with_protocol(protocol='public_MC_RGB', groups='dev')) == 25 # 10 model ids for dev
 # assert len(db.model_ids_with_protocol(protocol='public_MC_RGB', groups='eval')) == 25 # 10 model ids for eval

 # assert len(db.objects(protocol='public_MC_RGB', groups='world')) == 1000 # 1000 samples in the world set

 # assert len(db.objects(protocol='public_MC_RGB', groups='dev', purposes='enroll')) == 500 # 500 samples for enrollment in the dev set (25 clients * 10 images * 2 recordings)
 # assert len(db.objects(protocol='public_MC_RGB', groups='dev', purposes='enroll', model_ids='026')) == 20 # 20 samples to enroll model '026' in the dev set
 # assert len(db.objects(protocol='public_MC_RGB', groups='dev', purposes='enroll', model_ids='071')) == 0 # 0 samples to enroll model '071' (it is an eval model)
 # assert len(db.objects(protocol='public_MC_RGB', groups='dev', purposes='probe')) == 500 # 500 samples as probes in the dev set (25 clients * 10 images * 2 recordings)

 # assert len(db.objects(protocol='public_MC_RGB', groups='eval', purposes='enroll')) == 500 # 500 samples for enrollment in the eval set (25 clients * 10 images * 2 recordings)
 # assert len(db.objects(protocol='public_MC_RGB', groups='eval', purposes='enroll', model_ids='058')) == 20 # 20 samples to enroll model '058' in the eval set
 # assert len(db.objects(protocol='public_MC_RGB', groups='eval', purposes='enroll', model_ids='001')) == 0 # 0 samples to enroll model '001' (it is a world model)
 # assert len(db.objects(protocol='public_MC_RGB', groups='eval', purposes='probe')) == 500 # 500 samples as probes in the eval set (25 clients * 10 images * 2 recordings) 

#def test_query_public_UD_RGB():
#  """
#  Test some queries for the public UD RGB protocol
#  """
#  db = Database()
#  
#  assert len(db.client_ids(protocol='public_UD_RGB')) == 75 # 75 client ids for world, dev and eval
#  assert len(db.client_ids(protocol='public_UD_RGB', groups='world')) == 25 # 25 client ids for world
#  assert len(db.client_ids(protocol='public_UD_RGB', groups='dev')) == 25 # 25 client ids for dev
#  assert len(db.client_ids(protocol='public_UD_RGB', groups='eval')) == 25 # 25 client ids for eval
#
#  assert len(db.model_ids_with_protocol(protocol='public_UD_RGB')) == 75 # 75 model ids for world, dev and eval
#  assert len(db.model_ids_with_protocol(protocol='public_UD_RGB', groups='world')) == 25 # 25 model ids for world
#  assert len(db.model_ids_with_protocol(protocol='public_UD_RGB', groups='dev')) == 25 # 10 model ids for dev
#  assert len(db.model_ids_with_protocol(protocol='public_UD_RGB', groups='eval')) == 25 # 10 model ids for eval
#
#  assert len(db.objects(protocol='public_UD_RGB', groups='world')) == 1000 # 1000 samples in the world set
#
#  assert len(db.objects(protocol='public_UD_RGB', groups='dev', purposes='enroll')) == 500 # 500 samples for enrollment in the dev set (25 clients * 10 images * 2 recordings)
#  assert len(db.objects(protocol='public_UD_RGB', groups='dev', purposes='enroll', model_ids='026')) == 20 # 20 samples to enroll model '026' in the dev set
#  assert len(db.objects(protocol='public_UD_RGB', groups='dev', purposes='enroll', model_ids='071')) == 0 # 0 samples to enroll model '071' (it is an eval model)
#  assert len(db.objects(protocol='public_UD_RGB', groups='dev', purposes='probe')) == 1000 # 1000 samples as probes in the dev set (25 clients * 10 images * 4 recordings)
#
#  assert len(db.objects(protocol='public_UD_RGB', groups='eval', purposes='enroll')) == 500 # 500 samples for enrollment in the eval set (25 clients * 10 images * 2 recordings)
#  assert len(db.objects(protocol='public_UD_RGB', groups='eval', purposes='enroll', model_ids='058')) == 20 # 20 samples to enroll model '058' in the eval set
#  assert len(db.objects(protocol='public_UD_RGB', groups='eval', purposes='enroll', model_ids='001')) == 0 # 0 samples to enroll model '001' (it is a world model)
#  assert len(db.objects(protocol='public_UD_RGB', groups='eval', purposes='probe')) == 1000 # 500 samples as probes in the eval set (25 clients * 10 images * 4 recordings)
#
#def test_query_public_UO_RGB():
#  """
#  Test some queries for the public UO RGB protocol
#  """
#  db = Database()
#  
#  assert len(db.client_ids(protocol='public_UO_RGB')) == 75 # 75 client ids for world, dev and eval
#  assert len(db.client_ids(protocol='public_UO_RGB', groups='world')) == 25 # 25 client ids for world
#  assert len(db.client_ids(protocol='public_UO_RGB', groups='dev')) == 25 # 25 client ids for dev
#  assert len(db.client_ids(protocol='public_UO_RGB', groups='eval')) == 25 # 25 client ids for eval
#
#  assert len(db.model_ids_with_protocol(protocol='public_UO_RGB')) == 75 # 75 model ids for world, dev and eval
#  assert len(db.model_ids_with_protocol(protocol='public_UO_RGB', groups='world')) == 25 # 25 model ids for world
#  assert len(db.model_ids_with_protocol(protocol='public_UO_RGB', groups='dev')) == 25 # 10 model ids for dev
#  assert len(db.model_ids_with_protocol(protocol='public_UO_RGB', groups='eval')) == 25 # 10 model ids for eval
#
#  assert len(db.objects(protocol='public_UO_RGB', groups='world')) == 1000 # 1000 samples in the world set
#
#  assert len(db.objects(protocol='public_UO_RGB', groups='dev', purposes='enroll')) == 500 # 500 samples for enrollment in the dev set (25 clients * 10 images * 2 recordings)
#  assert len(db.objects(protocol='public_UO_RGB', groups='dev', purposes='enroll', model_ids='026')) == 20 # 20 samples to enroll model '026' in the dev set
#  assert len(db.objects(protocol='public_UO_RGB', groups='dev', purposes='enroll', model_ids='071')) == 0 # 0 samples to enroll model '071' (it is an eval model)
#  assert len(db.objects(protocol='public_UO_RGB', groups='dev', purposes='probe')) == 1000 # 1000 samples as probes in the dev set (25 clients * 10 images * 4 recordings)
#
#  assert len(db.objects(protocol='public_UO_RGB', groups='eval', purposes='enroll')) == 500 # 500 samples for enrollment in the eval set (25 clients * 10 images * 2 recordings)
#  assert len(db.objects(protocol='public_UO_RGB', groups='eval', purposes='enroll', model_ids='058')) == 20 # 20 samples to enroll model '058' in the eval set
#  assert len(db.objects(protocol='public_UO_RGB', groups='eval', purposes='enroll', model_ids='001')) == 0 # 0 samples to enroll model '001' (it is a world model)
#  assert len(db.objects(protocol='public_UO_RGB', groups='eval', purposes='probe')) == 1000 # 500 samples as probes in the eval set (25 clients * 10 images * 4 recordings)
#
#def test_query_public_NIR():
#  """
#  Test some queries for the public NIR protocols
#  """
#  db = Database()
#  
#  assert len(db.client_ids(protocol='public_MC_NIR')) == 75 # 75 client ids for world, dev and eval
#  assert len(db.client_ids(protocol='public_MC_NIR', groups='dev')) == 25 # 25 client ids for dev
#  assert len(db.model_ids_with_protocol(protocol='public_UD_NIR', groups='eval')) == 25 # 10 model ids for eval
#  assert len(db.objects(protocol='public_UO_NIR', groups='world')) == 1000 # 1000 samples in the world set
#  
#  assert len(db.objects(protocol='public_UO_NIR', groups='dev', purposes='enroll')) == 500 # 500 samples for enrollment in the dev set (25 clients * 10 images * 2 recordings)
#  assert len(db.objects(protocol='public_UD_NIR', groups='dev', purposes='enroll', model_ids='034')) == 20 # 20 samples to enroll model '034' in the dev set
#  assert len(db.objects(protocol='public_UO_NIR', groups='dev', purposes='enroll', model_ids='062')) == 0 # 0 samples to enroll model '062' (it is an eval model)
#  assert len(db.objects(protocol='public_MC_NIR', groups='dev', purposes='probe')) == 500 # MC Protocol -> 500 samples as probes in the dev set (25 clients * 10 images * 2 recordings)
#  assert len(db.objects(protocol='public_UD_NIR', groups='dev', purposes='probe')) == 1000 # UO protocol -> 1000 samples as probes in the dev set (25 clients * 10 images * 4 recordings)
#
#  assert len(db.objects(protocol='public_UO_NIR', groups='eval', purposes='enroll')) == 500 # 500 samples for enrollment in the eval set (25 clients * 10 images * 2 recordings)
#  assert len(db.objects(protocol='public_UD_NIR', groups='eval', purposes='enroll', model_ids='058')) == 20 # 20 samples to enroll model '058' in the eval set
#  assert len(db.objects(protocol='public_UO_NIR', groups='eval', purposes='enroll', model_ids='001')) == 0 # 0 samples to enroll model '001' (it is a world model)
#  assert len(db.objects(protocol='public_MC_NIR', groups='eval', purposes='probe')) == 500 # MC Protocol -> 500 samples as probes in the dev set (25 clients * 10 images * 4 recordings)
#  assert len(db.objects(protocol='public_UD_NIR', groups='eval', purposes='probe')) == 1000 # 500 samples as probes in the eval set (25 clients * 10 images * 4 recordings)
#  
#def test_query_public_depth():
#  """
#  Test some queries for the public depth protocols
#  """
#  db = Database()
#  
#  assert len(db.client_ids(protocol='public_MC_depth')) == 75 # 75 client ids for world, dev and eval
#  assert len(db.client_ids(protocol='public_MC_depth', groups='dev')) == 25 # 25 client ids for dev
#  assert len(db.model_ids_with_protocol(protocol='public_UD_depth', groups='eval')) == 25 # 10 model ids for eval
#  assert len(db.objects(protocol='public_UO_depth', groups='world')) == 1000 # 1000 samples in the world set
#  
#  assert len(db.objects(protocol='public_UO_depth', groups='dev', purposes='enroll')) == 500 # 500 samples for enrollment in the dev set (25 clients * 10 images * 2 recordings)
#  assert len(db.objects(protocol='public_UD_depth', groups='dev', purposes='enroll', model_ids='034')) == 20 # 20 samples to enroll model '034' in the dev set
#  assert len(db.objects(protocol='public_UO_depth', groups='dev', purposes='enroll', model_ids='062')) == 0 # 0 samples to enroll model '062' (it is an eval model)
#  assert len(db.objects(protocol='public_MC_depth', groups='dev', purposes='probe')) == 500 # MC Protocol -> 500 samples as probes in the dev set (25 clients * 10 images * 4 recordings)
#  assert len(db.objects(protocol='public_UD_depth', groups='dev', purposes='probe')) == 1000 # UO protocol -> 1000 samples as probes in the dev set (25 clients * 10 images * 4 recordings)
#
#  assert len(db.objects(protocol='public_UO_depth', groups='eval', purposes='enroll')) == 500 # 500 samples for enrollment in the eval set (25 clients * 10 images * 2 recordings)
#  assert len(db.objects(protocol='public_UD_depth', groups='eval', purposes='enroll', model_ids='058')) == 20 # 20 samples to enroll model '058' in the eval set
#  assert len(db.objects(protocol='public_UO_depth', groups='eval', purposes='enroll', model_ids='001')) == 0 # 0 samples to enroll model '001' (it is a world model)
#  assert len(db.objects(protocol='public_MC_depth', groups='eval', purposes='probe')) == 500 # MC Protocol -> 500 samples as probes in the dev set (25 clients * 10 images * 4 recordings)
#  #assert len(db.objects(protocol='public_UD_depth', groups='eval', purposes='probe')) == 1000 # 500 samples as probes in the eval set (25 clients * 10 images * 4 recordings)
