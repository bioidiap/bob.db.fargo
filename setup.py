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
          'bob_db_fargo_extract_images_frontal.py = bob.db.fargo.scripts.extract_images_frontal:main',
          'extract_poses.py = bob.db.fargo.scripts.extract_poses:main',
          'make_public_lists.py = bob.db.fargo.scripts.make_public_lists:main',
          'make_pose_lists.py = bob.db.fargo.scripts.make_pose_lists:main',
          'bob_db_fargo_extract_eyes_center.py = bob.db.fargo.scripts.extract_eyes_center:main',
          'eyes_center_from_landmarks.py = bob.db.fargo.scripts.eyes_center_from_landmarks:main',
          'convert_ir_and_depth.py = bob.db.fargo.scripts.convert_ir_and_depth:main',
          'reencode_color.py = bob.db.fargo.scripts.reencode_color:main',
          'detect_faces_fargo.py = bob.db.fargo.scripts.detect_faces_fargo:main',
          'detect_faces_fargo_for_pose.py = bob.db.fargo.scripts.detect_faces_fargo_for_pose:main',
          'crop_faces.py = bob.db.fargo.scripts.crop_faces:main',
          'crop_faces_for_article.py = bob.db.fargo.scripts.crop_faces_for_article:main',
          'extract_images_pose_varying.py = bob.db.fargo.scripts.extract_images_pose_varying:main',
          'make_pose_lists_pitch_yaw.py = bob.db.fargo.scripts.make_pose_lists_pitch_yaw:main',
          'detect_faces_fargo_pose_varying.py = bob.db.fargo.scripts.detect_faces_fargo_pose_varying:main',
          'crop_faces_for_article_poses.py = bob.db.fargo.scripts.crop_faces_for_article_poses:main',
        ],
        
        'bob.db': [
          'fargo = bob.db.fargo.driver:Interface',
        ],

      },

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
