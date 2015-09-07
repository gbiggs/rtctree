#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtctree

Copyright (C) 2009-2015
  Geoffrey Biggs
  RT-Synthesis Research Group
  Intelligent Systems Research Institute,
  National Institute of Advanced Industrial Science and Technology (AIST),
  Japan
  All rights reserved.
Licensed under the GNU Lesser General Public License version 3.
http://www.gnu.org/licenses/lgpl-3.0.en.html

rtctree install script.

'''

import os
import os.path
import setuptools
from distutils.command import build
import subprocess
import sys


def gen_idl_name(dir, name):
  '''Generate IDL file name from directory prefix and IDL module name.'''
  return os.path.join(dir, name + '.idl')


class BuildIDL(setuptools.Command):
  '''Implemented the build IDL subcommand.'''

  description = 'Generate Python stubs from IDL files'

  user_options = [('omniidl=', 'i', 'omniidl program used to build stubs'),
          ('idldir=',  'd', 'directory where IDL files reside')
          ]

  def initialize_options(self):
    self.idl_dir  = None
    self.omniidl = None
    self.omniidl_params = ['-bpython']
    self.idl_files = ['BasicDataType', 'ComponentObserver',
        'ExtendedDataTypes', 'InterfaceDataTypes', 'DataPort',
        'Logger', 'Manager', 'OpenRTM', 'RTC', 'SDOPackage']

  def finalize_options(self):
    if not self.omniidl:
      self.omniidl = 'omniidl'
    if not self.idl_dir:
      self.idl_dir = os.path.join(os.getcwd(), 'rtctree', 'rtmidl')

  def compile_idl(self, cmd, params, files):
    log.info('{0} {1} {2}'.format(cmd, ' '.join(params), ' '.join(files)))
    process = subprocess.Popen([cmd] + params + files,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=self.idl_dir)
    stdout, stderr = process.communicate()
    log.info(stdout)
    if process.returncode != 0:
      raise errors.DistutilsExecError('Error compiling IDL \
({0})'.format(process.returncode))

  def run(self):
    util.execute(self.compile_idl,
           (self.omniidl, self.omniidl_params,
             [gen_idl_name(self.idl_dir, idl_file) \
                 for idl_file in self.idl_files]),
           msg='Generating python stubs from IDL files')


class CustomBuild(build.build):
  def has_pure_modules(self):
    return self.distribution.has_pure_modules()

  def has_c_libraries(self):
    return self.distribution.has_c_libraries()

  def has_ext_modules(self):
    return self.distribution.has_ext_modules()

  def has_scripts(self):
    return self.distribution.has_scripts()

  def has_idl_files(self):
    return True

  sub_commands = [('build_idl', has_idl_files),
          ('build_py', has_pure_modules),
          ('build_clib', has_c_libraries),
          ('build_ext', has_ext_modules),
          ('build_scripts', has_scripts)
          ]


setuptools.setup(name='rtctree',
  version='4.2.0',
  description='API for interacting with running RT Components and \
managing RTM-based systems.',
  long_description='API for interacting with running RT Components and \
managing RTM-based systems.',
  author='Geoffrey Biggs',
  author_email='geoffrey.biggs@aist.go.jp',
  url='http://github.com/gbiggs/rtctree',
  license='LGPL3',
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development',
    ],

  packages=['rtctree',
      'rtctree.rtmidl',
      'rtctree.rtmidl.OpenRTM',
      'rtctree.rtmidl.OpenRTM__POA',
      'rtctree.rtmidl.RTC',
      'rtctree.rtmidl.RTC__POA',
      'rtctree.rtmidl.RTM',
      'rtctree.rtmidl.RTM__POA',
      'rtctree.rtmidl.SDOPackage',
      'rtctree.rtmidl.SDOPackage__POA'],

  include_package_data = True,
  cmdclass={'build':CustomBuild, 'build_idl': BuildIDL},
  zip_safe = True
  )

#  vim: set ts=2 sw=2 tw=79 :
