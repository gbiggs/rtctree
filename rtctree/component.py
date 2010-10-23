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

Object representing a component node in the tree.

'''


from rtctree.config_set import ConfigurationSet
from rtctree.exceptions import *
from rtctree.exec_context import ExecutionContext
from rtctree.node import TreeNode
from rtctree.ports import parse_port
from rtctree.utils import build_attr_string, nvlist_to_dict
import RTC
import SDOPackage


##############################################################################
## Component node object

class Component(TreeNode):
    '''Node representing a component on a name server.

    Component nodes can occur below name server and directory nodes. They
    cannot contain any children.

    Component nodes store all the properties of a component, as well as
    references to the actual objects and object types used in the component.

    '''
    def __init__(self, name=None, parent=None, obj=None, *args, **kwargs):
        '''Constructor.

        @param name Name of this component (i.e. its entry in the path).
        @param parent The parent node of this node, if any.
        @param obj The CORBA LightweightRTObject object to wrap.

        '''
        super(Component, self).__init__(name=name, parent=parent,
                                        *args, **kwargs)
        self._reset_data()
        self._obj = obj
        self._parse_profile()

    def reparse(self):
        '''Reparse the component's information.

        This will cause a delayed reparse of most information. This means that
        a piece of information, such as the list of ports, will be cleared and
        remain empty until it is next requested, at which point a fresh list
        will be retrieved from the component.

        If you only want to reparse a specific piece of information, use one of
        the reparse_X() methods.

        '''
        self._reset_data()
        self._parse_profile()

    def reparse_conf_sets(self):
        '''Reparse configuration sets.'''
        self._reset_conf_sets()

    def reparse_ecs(self):
        '''Reparse all execution contexts.'''
        self.reparse_owned_ecs()
        self.reparse_participating_ecs()

    def reparse_owned_ecs(self):
        '''Reparse only owned execution contexts.'''
        self._reset_owned_ecs()

    def reparse_participating_ecs(self):
        '''Reparse only participating execution contexts.'''
        self._reset_participating_ecs()

    def reparse_ports(self):
        '''Reparse ports.'''
        self._reset_ports()

    def reparse_profile(self):
        '''Reparse the component's profile.'''
        self._parse_profile()

    ###########################################################################
    # Component information

    @property
    def category(self):
        '''The category in which the component belongs.'''
        with self._mutex:
            return self._category

    @property
    def description(self):
        '''The component's description.'''
        with self._mutex:
            return self._description

    @property
    def instance_name(self):
        '''Instance name of the component.'''
        with self._mutex:
            return self._instance_name

    @property
    def parent_object(self):
        '''The name of the component's parent object (typically another
        component), if it has one.

        '''
        with self._mutex:
            return self._parent_obj

    @property
    def properties(self):
        '''The component's extra properties dictionary.'''
        with self._mutex:
            return self._properties

    @property
    def type_name(self):
        '''Type name of the component.'''
        with self._mutex:
            return self._type_name

    @property
    def vendor(self):
        '''The component's vendor.'''
        with self._mutex:
            return self._vendor

    @property
    def version(self):
        '''The component's version.'''
        with self._mutex:
            return self._version

    ###########################################################################
    # State management

    def activate_in_ec(self, ec_index):
        '''Activate this component in an execution context.

        @param ec_index The index of the execution context to activate in.
                        This index is into the total array of contexts, that
                        is both owned and participating contexts. If the value
                        of ec_index is greater than the length of
                        @ref owned_ecs, that length is subtracted from
                        ec_index and the result used as an index into
                        @ref participating_ecs.

        '''
        with self._mutex:
            if ec_index >= len(self.owned_ecs):
                ec_index -= len(self.owned_ecs)
                if ec_index >= len(self.participating_ecs):
                    raise BadECIndexError(ec_index)
                ec = self.participating_ecs[ec_index]
            else:
                ec = self.owned_ecs[ec_index]
            ec.activate_component(self._obj)

    def deactivate_in_ec(self, ec_index):
        '''Deactivate this component in an execution context.

        @param ec_index The index of the execution context to deactivate in.
                        This index is into the total array of contexts, that
                        is both owned and participating contexts. If the value
                        of ec_index is greater than the length of
                        @ref owned_ecs, that length is subtracted from
                        ec_index and the result used as an index into
                        @ref participating_ecs.

        '''
        with self._mutex:
            if ec_index >= len(self.owned_ecs):
                ec_index -= len(self.owned_ecs)
                if ec_index >= len(self.participating_ecs):
                    raise BadECIndexError(ec_index)
                ec = self.participating_ecs[ec_index]
            else:
                ec = self.owned_ecs[ec_index]
            ec.deactivate_component(self._obj)

    def exit(self):
        '''Make a component exit.

        This function will make the component exit, shutting down its CORBA
        object in the process. It will not remove the node from the tree; a
        reparse is necessary to do that.

        '''
        self._obj.exit()

    def get_ec_index(self, ec_handle):
        '''Get the index of the execution context with the given handle.

        @param ec_handle The handle of the execution context to look for.
        @type ec_handle str
        @return The index into the owned + participated arrays, suitable for
        use in methods such as @ref activate_in_ec, or -1 if the EC was not
        found.

        '''
        with self._mutex:
            for ii, ec in enumerate(self.owned_ecs):
                if ec.handle == ec_handle:
                    return ii
            for ii, ec in enumerate(self.participating_ecs):
                if ec.handle == ec_handle:
                    return ii + len(self.owned_ecs)
            return -1

    def get_state_string(self, add_colour=True):
        '''Get the state of this component as an optionally-coloured string.

        @param add_colour If True, ANSI colour codes will be added to the
                          string.
        @return A string describing the state of this component.

        '''
        with self._mutex:
            if self.state == self.INACTIVE:
                result = 'Inactive', ['bold', 'blue']
            elif self.state == self.ACTIVE:
                result = 'Active', ['bold', 'green']
            elif self.state == self.ERROR:
                result = 'Error', ['bold', 'white', 'bgred']
            elif self.state == self.UNKNOWN:
                result = 'Unknown', ['bold', 'red']
            elif self.state == self.CREATED:
                result = 'Created', ['reset']
        if add_colour:
            return build_attr_string(result[1], supported=add_colour) + \
                    result[0] + build_attr_string('reset', supported=add_colour)
        else:
            return result[0]

    def reset_in_ec(self, ec_index):
        '''Reset this component in an execution context.

        @param ec_index The index of the execution context to reset in. This
                        index is into the total array of contexts, that is both
                        owned and participating contexts. If the value of
                        ec_index is greater than the length of @ref owned_ecs,
                        that length is subtracted from ec_index and the result
                        used as an index into @ref participating_ecs.

        '''
        with self._mutex:
            if ec_index >= len(self.owned_ecs):
                ec_index -= len(self.owned_ecs)
                if ec_index >= len(self.participating_ecs):
                    raise BadECIndexError(ec_index)
                ec = self.participating_ecs[ec_index]
            else:
                ec = self.owned_ecs[ec_index]
            ec.reset_component(self._obj)

    def state_in_ec(self, ec_index):
        '''Get the state of the component in an execution context.

        @param ec_index The index of the execution context to check the state
                        in. This index is into the total array of contexts,
                        that is both owned and participating contexts. If the
                        value of ec_index is greater than the length of @ref
                        owned_ecs, that length is subtracted from ec_index and
                        the result used as an index into @ref
                        participating_ecs.

        '''
        with self._mutex:
            if ec_index >= len(self.owned_ecs):
                ec_index -= len(self.owned_ecs)
                if ec_index >= len(self.participating_ecs):
                    raise BadECIndexError(ec_index)
                return self.participating_ec_states[ec_index]
            else:
                return self.owned_ec_states[ec_index]

    def refresh_state_in_ec(self, ec_index):
        '''Get the up-to-date state of the component in an execution context.

        This function will update the state, rather than using the cached
        value. This may take time, if the component is executing on a remote
        node.

        @param ec_index The index of the execution context to check the state
                        in. This index is into the total array of contexts,
                        that is both owned and participating contexts. If the
                        value of ec_index is greater than the length of @ref
                        owned_ecs, that length is subtracted from ec_index and
                        the result used as an index into @ref
                        participating_ecs.

        '''
        with self._mutex:
            if ec_index >= len(self.owned_ecs):
                ec_index -= len(self.owned_ecs)
                if ec_index >= len(self.participating_ecs):
                    raise BadECIndexError(ec_index)
                state = self._get_ec_state(self.participating_ecs[ec_index])
                self.participating_ec_states[ec_index] = state
            else:
                state = self._get_ec_state(self.owned_ecs[ec_index])
                self.owned_ec_states[ec_index] = state
            return state

    @property
    def alive(self):
        '''Is this component alive?'''
        with self._mutex:
            if self.exec_contexts:
                for ec in self.exec_contexts:
                    if self._obj.is_alive(ec):
                        return True
        return False

    @property
    def owned_ec_states(self):
        '''The state of each execution context this component owns.'''
        with self._mutex:
            if not self._owned_ec_states:
                if self.owned_ecs:
                    states = []
                    for ec in self.owned_ecs:
                        states.append(self._get_ec_state(ec))
                    self._owned_ec_states = states
                else:
                    self._owned_ec_states = []
        return self._owned_ec_states

    @property
    def owned_ecs(self):
        '''A list of the execution contexts owned by this component.'''
        with self._mutex:
            if not self._owned_ecs:
                self._owned_ecs = [ExecutionContext(ec,
                    self._obj.get_context_handle(ec)) \
                    for ec in self._obj.get_owned_contexts()]
        return self._owned_ecs

    @property
    def participating_ec_states(self):
        '''The state of each execution context this component is participating
        in.

        '''
        with self._mutex:
            if not self._participating_ec_states:
                if self.participating_ecs:
                    states = []
                    for ec in self.participating_ecs:
                        states.append(self._get_ec_state(ec))
                    self._participating_ec_states = states
                else:
                    self._participating_ec_states = []
        return self._participating_ec_states

    @property
    def participating_ecs(self):
        '''A list of the execution contexts this component is participating in.

        '''
        with self._mutex:
            if not self._participating_ecs:
                self._participating_ecs = [ExecutionContext(ec,
                                    self._obj.get_context_handle(ec)) \
                             for ec in self._obj.get_participating_contexts()]
        return self._participating_ecs

    @property
    def plain_state_string(self):
        '''The state of this component as a string without colour.'''
        return self.get_state_string(add_colour=False)

    @property
    def state(self):
        '''The merged state of all the execution context states, which can be
        used as the overall state of this component.

        The order of precedence is:
            Error > Active > Inactive > Created > Unknown

        '''
        def merge_state(current, new):
            if new == self.ERROR:
                return self.ERROR
            elif new == self.ACTIVE and current != self.ERROR:
                return self.ACTIVE
            elif new == self.INACTIVE and \
                    current not in [self.ACTIVE, self.ERROR]:
                return self.INACTIVE
            elif new == self.CREATED and \
                    current not in [self.ACTIVE, self.ERROR, self.INACTIVE]:
                return self.CREATED
            elif current not in [self.ACTIVE, self.ERROR, self.INACTIVE,
                                 self.CREATED]:
                return self.UNKNOWN
            return current

        with self._mutex:
            if not self.owned_ec_states and not self.participating_ec_states:
                return self.UNKNOWN
            merged_state = self.CREATED
            if self.owned_ec_states:
                for ec_state in self.owned_ec_states:
                    merged_state = merge_state(merged_state, ec_state)
            if self.participating_ec_states:
                for ec_state in self.participating_ec_states:
                    merged_state = merge_state(merged_state, ec_state)
            return merged_state

    @property
    def state_string(self):
        '''The state of this component as a colourised string.'''
        return self.get_state_string()

    ###########################################################################
    # Port management

    def disconnect_all(self):
        '''Disconnect all connections to all ports of this component.'''
        with self._mutex:
            for p in self.ports:
                p.disconnect_all()

    def get_port_by_name(self, port_name):
        '''Get a port of this component by name.'''
        with self._mutex:
            for p in self.ports:
                if p.name == port_name:
                    return p
            return None

    def get_port_by_ref(self, port_ref):
        '''Get a port of this component by reference to a CORBA PortService
        object.

        '''
        with self._mutex:
            for p in self.ports:
                if p.object._is_equivalent(port_ref):
                    return p
            return None

    def has_port_by_name(self, port_name):
        '''Check if this component has a port by the given name.'''
        with self._mutex:
            if self.get_port_by_name(port_name):
                return True
            return False

    def has_port_by_ref(self, port_ref):
        '''Check if this component has a port by the given reference to a CORBA
        PortService object.

        '''
        with self._mutex:
            if self.get_port_by_ref(self, port_ref):
                return True
            return False

    @property
    def connected_inports(self):
        '''The list of all input ports belonging to this component that are
        connected to one or more other ports.

        '''
        return [p for p in self.ports \
                if p.__class__.__name__ == 'DataInPort' and p.is_connected]

    @property
    def connected_outports(self):
        '''The list of all output ports belonging to this component that are
        connected to one or more other ports.

        '''
        return [p for p in self.ports \
                    if p.__class__.__name__ == 'DataOutPort' \
                    and p.is_connected]

    @property
    def connected_ports(self):
        '''The list of all ports belonging to this component that are connected
        to one or more other ports.

        '''
        return [p for p in self.ports if p.is_connected]

    @property
    def connected_svcports(self):
        '''The list of all service ports belonging to this component that are
        connected to one or more other ports.

        '''
        return [p for p in self.ports \
                if p.__class__.__name__ == 'CorbaPort' and p.is_connected]

    @property
    def inports(self):
        '''The list of all input ports belonging to this component.'''
        return [p for p in self.ports if p.__class__.__name__ == 'DataInPort']

    @property
    def outports(self):
        '''The list of all output ports belonging to this component.'''
        return [p for p in self.ports if p.__class__.__name__ == 'DataOutPort']

    @property
    def ports(self):
        '''The list of all ports belonging to this component.'''
        with self._mutex:
            if not self._ports:
                self._ports = [parse_port(port, self) \
                               for port in self._obj.get_ports()]
        return self._ports

    @property
    def svcports(self):
        '''The list of all service ports belonging to this component.'''
        return [p for p in self.ports if p.__class__.__name__ == 'CorbaPort']

    ###########################################################################
    # Node functionality

    @property
    def is_component(self):
        '''Is this node a component?'''
        return True

    @property
    def object(self):
        '''The LightweightRTObject this object wraps.'''
        with self._mutex:
            return self._obj

    ###########################################################################
    # Configuration set management

    def activate_conf_set(self, set_name):
        '''Activate a configuration set by name.

        @raises NoSuchConfSetError

        '''
        with self._mutex:
            if not set_name in self.conf_sets:
                raise NoSuchConfSetError(set_name)
            self._conf.activate_configuration_set(set_name)

    def set_conf_set_value(self, set_name, param, value):
        '''Set a configuration set parameter value.

        @param set_name The name of the configuration set the destination
                        parameter is in.
        @param param The name of the parameter to set.
        @param value The new value for the parameter.
        @raises NoSuchConfSetError, NoSuchConfParamError

        '''
        with self._mutex:
            if not set_name in self.conf_sets:
                raise NoSuchConfSetError(set_name)
            if not self.conf_sets[set_name].has_param(param):
                raise NoSuchConfParamError(param)
            self.conf_sets[set_name].set_param(param, value)
            self._conf.set_configuration_set_values(\
                    self.conf_sets[set_name].object)

    @property
    def active_conf_set(self):
        '''The currently-active configuration set.'''
        with self._mutex:
            if not self.conf_sets:
                return None
            if not self._active_conf_set:
                return None
            return self.conf_sets[self._active_conf_set]

    @property
    def active_conf_set_name(self):
        '''The name of the currently-active configuration set.'''
        with self._mutex:
            if not self.conf_sets:
                return ''
            if not self._active_conf_set:
                return ''
            return self._active_conf_set

    @property
    def conf_sets(self):
        '''The dictionary of configuration sets in this component, if any.'''
        with self._mutex:
            if not self._conf_sets:
                self._parse_configuration()
        return self._conf_sets

    ###########################################################################
    # Internal API

    def _add_child(self):
        # Components cannot contain children.
        raise CannotHoldChildrenError

    def _get_ec_state(self, ec):
        # Get the state of this component in an EC and return the enum value.
        if self._obj.is_alive(ec._obj):
            ec_state = ec.get_component_state(self._obj)
            if ec_state == RTC.ACTIVE_STATE:
                return self.ACTIVE
            elif ec_state == RTC.ERROR_STATE:
                return self.ERROR
            elif ec_state == RTC.INACTIVE_STATE:
                return self.INACTIVE
            else:
                return self.UNKNOWN
        else:
            return self.CREATED

    def _parse_configuration(self):
        # Parse the component's configuration sets
        with self._mutex:
            self._conf = self.object.get_configuration()
            self._conf_sets = {}
            for cs in self._conf.get_configuration_sets():
                self._conf_sets[cs.id] = ConfigurationSet(self, cs, cs.description,
                        nvlist_to_dict(cs.configuration_data))
            try:
                self._active_conf_set = self._conf.get_active_configuration_set().id
            except SDOPackage.NotAvailable:
                self._active_conf_set = ''

    def _parse_profile(self):
        # Parse the component's profile
        with self._mutex:
            profile = self._obj.get_component_profile()
            self._instance_name = profile.instance_name
            self._type_name = profile.type_name
            self._description = profile.description
            self._version = profile.version
            self._vendor = profile.vendor
            self._category = profile.category
            if profile.parent:
                self._parent_obj = \
                        profile.parent.get_component_profile().instance_name
            else:
                self._parent_obj = ''
            self._properties = nvlist_to_dict(profile.properties)

    def _reset_conf_sets(self):
        with self._mutex:
            self._conf_sets = None
            self._active_conf_set = None

    def _reset_data(self):
        self._reset_owned_ecs()
        self._reset_participating_ecs()
        self._reset_ports()
        self._reset_conf_sets()

    def _reset_owned_ecs(self):
        with self._mutex:
            self._owned_ecs = None
            self._owned_ec_states = None

    def _reset_owned_ec_states(self):
        with self._mutex:
            self._owned_ec_states = None

    def _reset_participating_ecs(self):
        with self._mutex:
            self._participating_ecs = None
            self._participating_ec_states = None

    def _reset_participating_ec_states(self):
        with self._mutex:
            self._participating_ec_states = None

    def _reset_ports(self):
        with self._mutex:
            self._ports = None

    ## Constant for a component in the inactive state
    INACTIVE = 1
    ## Constant for a component in the active state
    ACTIVE = 2
    ## Constant for a component in the error state
    ERROR = 3
    ## Constant for a component in an unknown state
    UNKNOWN = 4
    ## Constant for a component in the created state
    CREATED = 5


# vim: tw=79

