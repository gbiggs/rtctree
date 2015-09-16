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

Singleton containing option values.

'''


import sys

from rtctree import exceptions


##############################################################################
## Options object

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
            raise exceptions.NoSuchOptionError(option)
        return self.options[option]


# vim: set expandtab tabstop=8 shiftwidth=4 softtabstop=4 textwidth=79
