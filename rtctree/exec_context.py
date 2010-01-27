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

File: exec_context.py

Object representing an execution context.

'''

__version__ = '$Revision: $'
# $Source$


from rtctree.utils import build_attr_string
import RTC


##############################################################################
## Execution context object

class ExecutionContext(object):
    '''An execution context, within which components may be executing.'''
    def __init__(self, ec_obj, handle=None):
        '''Constructor.

        @param ec_obj The CORBA ExecutionContext object to wrap.
        @param handle The handle of this execution context, which can be used
                      to uniquely identify it.

        '''
        self._obj = ec_obj
        self._handle = handle
        self._parse()

    def activate_component(self, comp_ref):
        '''Activate a component within this context.

        @param comp_ref The CORBA LightweightRTObject to activate.

        '''
        self._obj.activate_component(comp_ref)

    def deactivate_component(self, comp_ref):
        '''Deactivate a component within this context.

        @param comp_ref The CORBA LightweightRTObject to deactivate.

        '''
        self._obj.deactivate_component(comp_ref)

    def reset_component(self, comp_ref):
        '''Reset a component within this context.

        @param comp_ref The CORBA LightweightRTObject to reset.

        '''
        self._obj.reset_component(comp_ref)

    def get_component_state(self, comp):
        '''Get the state of a component within this context.

        @param comp The CORBA LightweightRTObject to get the state of.
        @return The component state, as a LifeCycleState value.

        '''
        return self._obj.get_component_state(comp)

    def kind_as_string(self, add_colour=True):
        '''Get the type of this context as an optionally coloured string.

        @param add_colour If True, ANSI colour codes will be added.
        @return A string describing the kind of execution context this is.

        '''
        if self._kind == self.PERIODIC:
            result = 'Periodic', ['reset']
        elif self._kind == self.EVENT_DRIVEN:
            result = 'Event-driven', ['reset']
        elif self._kind == self.OTHER:
            result = 'Other', ['reset']
        if add_colour:
            return build_attr_string(result[1]) + result[0] + \
                build_attr_string('reset')
        else:
            return result[0]

    def running_as_string(self, add_colour=True):
        '''Get the state of this context as an optionally coloured string.

        @param add_colour If True, ANSI colour codes will be added.
        @return A string describing this context's running state.

        '''
        if self.running:
            result = 'Running', ['bold', 'green']
        else:
            result = 'Stopped', ['reset']
        if add_colour:
            return build_attr_string(result[1]) + result[0] + \
                build_attr_string('reset')
        else:
            return result[0]

    @property
    def handle(self):
        '''The handle of this execution context.'''
        return self._handle

    @property
    def kind(self):
        '''The kind of this execution context.'''
        return self._kind

    @property
    def kind_string(self):
        '''The kind of this execution context as a coloured string.'''
        return self.kind_as_string()

    @property
    def rate(self):
        '''The execution rate of this execution context.'''
        return self._rate

    @property
    def running(self):
        '''Is this execution context running?'''
        return self._running

    @property
    def running_string(self):
        '''The state of this execution context as a coloured string.'''
        return self.running_as_string()

    def _parse(self):
        #Parse the ExecutionContext object.
        if self._obj.is_running():
            self._running = True
        else:
            self._running = False

        self._rate = self._obj.get_rate()

        kind = self._obj.get_kind()
        if kind == RTC.PERIODIC:
            self._kind = self.PERIODIC
        elif kind == RTC.EVENT_DRIVEN:
            self._kind = self.EVENT_DRIVEN
        else:
            self._kind = self.OTHER

    ## Constant for a periodic execution context.
    PERIODIC = 1
    ## Constant for an event driven execution context.
    EVENT_DRIVEN = 2
    ## Constant for an execution context of some other type.
    OTHER = 3


# vim: tw=79

