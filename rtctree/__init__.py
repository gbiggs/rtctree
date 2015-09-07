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

Library for easy access to name servers running components, the components
themselves, and managers.

'''


# Add the IDL path to the Python path
import sys
import os
_openrtm_idl_path = os.path.join(os.path.dirname(__file__), 'rtmidl')
if _openrtm_idl_path not in sys.path:
    sys.path.insert(1, _openrtm_idl_path)
del _openrtm_idl_path
del os
del sys


RTCTREE_VERSION = '4.1.0'
NAMESERVERS_ENV_VAR = 'RTCTREE_NAMESERVERS'
ORB_ARGS_ENV_VAR = 'RTCTREE_ORB_ARGS'


# vim: tw=79

