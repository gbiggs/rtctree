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

File: directory.py

Object representing a directory node in the tree.

'''

__version__ = '$Revision: $'
# $Source$


import CosNaming
from omniORB import URI, CORBA, TRANSIENT_ConnectFailed
import sys

from rtctree.component import Component
from rtctree.manager import Manager
from rtctree.node import TreeNode
from rtctree.options import Options
import RTC
import RTM


##############################################################################
## Directory node object

class Directory(TreeNode):
    '''Node representing a naming context on a name server.

    Name servers contain contexts (including the root context) and objects. For
    us, contexts are directories and objects are managers and components. A
    directory context may specialise as a name server context, in which case
    it represents the root context of a name server.

    '''
    def __init__(self, name, parent, children=None):
        '''Constructor. Calls the TreeNode constructor.'''
        super(Directory, self).__init__(name, parent, children)

    @property
    def is_directory(self):
        '''Is this node a directory?'''
        return True

    def _parse_context(self, context, orb):
        # Parse a naming context to fill in the children.
        self._context = context
        # Get the list of bindings from the context
        bindings, bindings_it = context.list(Options().\
                                    get_option('max_bindings'))
        for binding in bindings:
            # Process the bindings that are within max_bindings
            self._process_binding(binding, orb)
        if bindings_it:
            # Handle the iterator containing the remaining bindings
            remaining, bindings = bindings_it[1].next_n(Options().\
                                        get_option('max_bindings'))
            while remaining:
                for binding in bindings:
                    self._process_binding(binding, orb)
                remaining, binding = bindings_it[1].next_n(Options().\
                                            get_option('max_bindings'))
            bindings_it.destroy()

    def _process_binding(self, binding, orb):
        # Process a binding, creating the correct child type for it and adding
        # that child to this node's children.
        if binding.binding_type == CosNaming.nobject:
            # This is a leaf node; either a component or a manager.
            # The specific type can be determined from the binding name kind.
            if binding.binding_name[0].kind == 'mgr':
                name = URI.nameToString(binding.binding_name)
                obj = self._context.resolve(binding.binding_name)
                obj = obj._narrow(RTM.Manager)
                try:
                    leaf = Manager(name, self, obj)
                except CORBA.OBJECT_NOT_EXIST:
                    # Manager zombie
                    print >>sys.stderr, '{0}: Warning: zombie component \
found: {1}'.format(sys.argv[0], name)
                    return
                self._add_child(leaf)
            else:
                # Assume it's a component
                name = URI.nameToString(binding.binding_name)
                obj = self._context.resolve(binding.binding_name)
                try:
                    obj = obj._narrow(RTC.RTObject)
                except CORBA.TRANSIENT, e:
                    if e.args[0] == TRANSIENT_ConnectFailed:
                        print >>sys.stderr, '{0}: Warning: zombie component \
{1} found under {2}'.format(sys.argv[0], name, self.name)
                        return
                    else:
                        raise
                try:
                    leaf = Component(name, self, obj)
                except CORBA.OBJECT_NOT_EXIST:
                    # Component zombie
                    print >>sys.stderr, '{0}: Warning: zombie component \
{1} found under {2}'.format(sys.argv[0], name, self.name)
                    return
                self._add_child(leaf)
        else:
            # This is a context, and therefore a subdirectory.
            subdir_name = URI.nameToString(binding.binding_name)
            subdir = Directory(subdir_name, self)
            subdir_context = self._context.resolve(binding.binding_name)
            subdir_context = subdir_context._narrow(CosNaming.NamingContext)
            subdir._parse_context(subdir_context, orb)
            self._add_child(subdir)


# vim: tw=79

