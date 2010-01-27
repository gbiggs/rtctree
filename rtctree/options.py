# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtctree

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

File: options.py

Singleton containing option values.

'''

__version__ = '$Revision: $'
# $Source$

import sys

from rtctree.exceptions import NoSuchOptionError

class Options(object):
    def __new__(cls, *p, **k):
        if not '_the_instance' in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance

    def init_options(self):
        self.options = {'max_bindings': 100}

    def set_option(self, option, value):
        if not hasattr(self, 'options'):
            self.init_options()
        self.options[option] = value

    def get_option(self, option):
        if not hasattr(self, 'options'):
            self.init_options()
        if not option in self.options:
            raise NoSuchOptionError(option)
        return self.options[option]


# vim: tw=79

