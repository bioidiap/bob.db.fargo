.. vim: set fileencoding=utf-8 :
.. @author: Guillaume Heusch <guillaume.heusch@idiap.ch>
.. @date:   Tue Jan 03 16:12:18 CEST 2017

.. _bob.db.fargo:

==================
The FARGO Database
==================

This package contains an interface for the FARGO database, a face database
containing video sequences captured using an Intel RealSense SR-300. 
The database was recorded across a time period of 5 months during the summer of 2016,
across three different sites. 

It contains three different sessions: controlled, dark and outdoor.
For each session, each subject has been captured 4 times: 2 sequences where
the device is mounted on a laptop as a webcam, and 2 sequences where the
device is attached to a mobile phone, mimicking the frontal camera. Each 
sequence contains three data streams: RGB, Near Infrared (NIR) and 
depth maps.

The public data of the FARGO database can be downloaded `here
<http://www.idiap.ch/dataset/fargo>`_.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   guide
   py_api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
