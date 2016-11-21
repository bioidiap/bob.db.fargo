.. vim: set fileencoding=utf-8 :
.. Guillaume Heusch <guillaume.heusch@idiap.ch>
.. Mon 21 Nov 2016 08:14:00 CEST

====================================
 FARGO Database Interface for Bob
====================================

This package contains an interface for the FARGO database, a face database
containing video sequences captured using an Intel RealSense SR-300. 
The database was recorded across a time period of 5 months in three different
sessions: controlled, dark and outdoor.

For each session, each subject has been captured 4 times: 2 sequences where
the device is mounted on a laptop as a webcam, and 2 sequences where the
device is attached to a mobile phone, mimicking the frontal camera. Each 
sequence contains three data streams: RGB, Near Infrared (NIR) and 
depth maps.

If you decide to use this package, please consider citing `Bob`_, as a software
development environment and the authors of the dataset::

  @article{soleymani-2012,
    author={Soleymani, M. and Lichtenauer, J. and Pun, T. and Pantic, M.},
    journal={Affective Computing, IEEE Transactions on},
    title={A Multimodal Database for Affect Recognition and Implicit Tagging},
    year={2012},
    volume={3},
    number={1},
    pages={42-55},
    doi={10.1109/T-AFFC.2011.25},
    month=Jan,
    }


Installation
------------

To install this package -- alone or together with other `Packages of Bob
<https://github.com/idiap/bob/wiki/Packages>`_ -- please read the `Installation
Instructions <https://github.com/idiap/bob/wiki/Installation>`_.  For Bob_ to
be able to work properly, some dependent packages are required to be installed.
Please make sure that you have read the `Dependencies
<https://github.com/idiap/bob/wiki/Dependencies>`_ for your operating system.


Dependencies
============


Usage
-----


Annotations
===========


.. Your references go here

.. _bob: https://www.idiap.ch/software/bob
.. _mahnob hci-tagging dataset: http://mahnob-db.eu/hci-tagging/
.. _bob.ip.facedetect: https://pypi.python.org/pypi/bob.ip.facedetect
.. _mne: https://pypi.python.org/pypi/mne
