#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Fri 23 Dec 11:37:33 CET 2016

#!/usr/bin/env python

from bob.db.fargo import Database

fargo_images_directory = "[YOUR_FARGO_DIRECTORY]"

database = Database(
    original_directory=fargo_images_directory,
    original_extension=".png",
)
