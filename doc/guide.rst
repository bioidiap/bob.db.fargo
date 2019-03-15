.. vim: set fileencoding=utf-8 :
.. Tue 03 Jan 2017 16:36:40 CEST

User's Guide
==============

This package contains the access API and descriptions for the `FARGO
Database`_. It only contains the Bob_ accessor methods to use the DB directly
from python, with our certified protocols. The actual raw data for the dataset
should be downloaded from the original URL.


Extracting images from the original data
----------------------------------------
Since this package contains protocols to load different set of images
in different modalities, you should first extract images from the
raw data (i.e. recorded video sequences). You can do so by using the
provided scripts:

.. code-block:: bash

  > bob_db_fargo_extract_images_frontal.py path/to/data -i ./images
  > bob_db_fargo_extract_images_pos_varying_images.py path/to/data -i ./images


where ``path/to/data/`` is the location of the ``subjects`` folder of the database.
This will extract all the images you need in the ``./images`` directory.


.. Place your references here
.. _bob: http://www.idiap.ch/software/bob
.. _FARGO database: https://www.idiap.ch/dataset/fargo
