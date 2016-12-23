#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 21 Nov 08:21:19 CET 2016

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements
install_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

setup(
    name='bob.db.fargo',
    version=version,
    description="Bob Database interface for the FARGO database",
    keywords=['bob', 'database', 'fargo'],
    url='http://gitlab.idiap.ch/heusch/bob.db.fargo',
    license='BSD',
    author='Guillaume Heusch',
    author_email='guillaume.heusch@idiap.ch',

    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=install_requires,

    entry_points = {
        'console_scripts': [
          'extract_images.py = bob.db.fargo.scripts.extract_images:main',
          'make_public_lists.py = bob.db.fargo.scripts.make_public_lists:main'
        ],
        
        'bob.db': [
          'fargo = bob.db.fargo.driver:Interface',
        ],

        'bob.bio.database' : [
          'fargo = bob.db.fargo.config:database',
        ],

      },

    install_requires=[
      'setuptools',
      'bob.db.base',
      ],

    classifiers=[
      'Framework :: Bob',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Topic :: Software Development :: Libraries :: Python Modules',
      ],

    )
