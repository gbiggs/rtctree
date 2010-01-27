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

File: exceptions.py

General exception classes.

'''

__version__ = '$Revision: $'
# $Source$


import rtctree
import RTC


##############################################################################
## Exceptions

class RtcTreeError(Exception):
    '''Base error class.

    Used for undefined errors that are not core Python errors.

    '''
    pass


class ReturnCodeError(RtcTreeError):
    '''Generic error using a value of ReturnCode_t to set the message.'''
    def __init__(self, return_code):
        '''Constructor.

        @param return_code The type of return code. Must be on of the return
        codes defined in the RTC IDL.

        '''
        if return_code == RTC.RTC_ERROR:
            RtcTreeError.__init__(self, 'General error')
        elif return_code == RTC.BAD_PARAMETER:
            RtcTreeError.__init__(self, 'Bad parameter')
        elif return_code == RTC.UNSUPPORTED:
            RtcTreeError.__init__(self, 'Unsupported')
        elif return_code == RTC.OUT_OF_RESOURCES:
            RtcTreeError.__init__(self, 'Out of resources')
        elif return_code == RTC.PRECONDITION_NOT_MET:
            RtcTreeError.__init__(self, 'Precondition not met')


class InvalidServiceError(RtcTreeError):
    '''Could not connect to a CORBA service at an address.'''
    pass


class FailedToNarrowRootNamingError(RtcTreeError):
    '''Failed to narrow the root naming context of a name server.'''
    pass


class NonRootPathError(RtcTreeError):
    '''A path did not begin with '/'.'''
    pass

class CannotHoldChildrenError(RtcTreeError):
    '''Tried to add a child to a node that cannot hold children.'''
    pass


class BadECIndexError(RtcTreeError):
    '''Given the index of an execution context beyond the number of owned/
    participating contexts.

    '''
    pass


class WrongPortTypeError(RtcTreeError):
    '''Tried to connect two ports of incompatible type.'''
    pass


class IncompatibleDataPortConnectionPropsError(RtcTreeError):
    '''Given incompatible properties for a connection between two data
    ports.

    '''
    pass


class FailedToConnectError(ReturnCodeError):
    '''Failed to make a connection between two ports.'''
    pass


class MismatchedInterfacesError(RtcTreeError):
    '''Interfaces between two service ports do not match type.'''
    pass


class MismatchedPolarityError(RtcTreeError):
    '''Interfaces between two service ports do not match polarity.'''
    pass


class NotConnectedError(RtcTreeError):
    '''A connection is not connected.'''
    pass


class NoSuchConfSetError(RtcTreeError):
    '''Attempted to access a configuration set that doesn't exist.'''
    pass


class NoSuchConfParamError(RtcTreeError):
    '''Attempted to access a configuration parameter that doesn't exist.'''
    pass


class NoSuchOptionError(RtcTreeError):
    '''The requested option has not been set.'''
    pass


class BadPathError(RtcTreeError):
    '''Error indicating an invalid path.'''
    pass

class ManagerError(RtcTreeError):
    '''Base error type for errors involving managers.'''

class FailedToLoadModuleError(ManagerError):
    '''Error loading a shared library into a manager.'''
    pass

class FailedToUnloadModuleError(ManagerError):
    '''Error unloading a shared library from a manager.'''
    pass

class FailedToCreateComponentError(ManagerError):
    '''Error creating a component out of a shared library in a manager.'''
    pass

class FailedToDeleteComponentError(ManagerError):
    '''Error deleting a component from a manager.'''
    pass

class FailedToSetConfigurationError(ManagerError):
    '''Error setting a manager configuration parameter.'''
    pass

class FailedToAddMasterManagerError(ManagerError):
    '''Error when adding a master manager to another manager.'''
    pass

class FailedToRemoveMasterManagerError(ManagerError):
    '''Error when removing a master manager.'''
    pass

class FailedToAddSlaveManagerError(ManagerError):
    '''Error when adding a slave manager to another manager.'''
    pass

class FailedToRemoveSlaveManagerError(ManagerError):
    '''Error when removing a slave manager.'''
    pass

class NotRelatedError(RtcTreeError):
    '''Tried to manupulate the relationship between two nodes that are not
    parent and child.'''
    pass


# vim: tw=79

