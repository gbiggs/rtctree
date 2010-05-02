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

File: tree.py

Objects and functions used to build and store a tree representing a hierarchy
of name servers, directories, managers and components.

'''

__version__ = '$Revision: $'
# $Source$

from omniORB import CORBA
import os
import sys

from rtctree import NAMESERVERS_ENV_VAR, ORB_ARGS_ENV_VAR
from rtctree.exceptions import *
from rtctree.path import BadPathError
from rtctree.node import TreeNode
from rtctree.directory import Directory
from rtctree.nameserver import NameServer
from rtctree.manager import Manager
from rtctree.component import Component


##############################################################################
## API functions

def create_rtctree(servers=None, paths=None, orb=None):
    '''Create an RTCTree object, catching various common errors and outputting
    a suitable error message for them.

    See the documentation for the @ref RTCTree object for an explanation of the
    arguments.

    @returns An instance of RTCTree.

    '''
    try:
        tree = RTCTree(servers=servers, paths=paths, orb=orb)
    except InvalidServiceError, e:
        print >>sys.stderr, '{0}: Cannot access {1}: Invalid \
service.'.format(sys.argv[0], e[0])
        return None
    except FailedToNarrowRootNamingError, e:
        print >>sys.stderr, '{0}: Cannot access {1}: CORBA error narrowing \
root naming context.'.format(sys.argv[0], e)
        return None
    except NonRootPathError, e:
        print >>sys.stderr, '{0}: Cannot access {1}: No such directory or \
object.'.format(sys.argv[0], paths)
        return None
    except RtcTreeError, e:
        print >>sys.stderr, '{0}: Unknown error occured: \
{1}'.format(sys.argv[0], e)
        return None
    return tree


##############################################################################
## Tree object

class RTCTree(object):
    '''Represents a tree of name servers, directories, managers and components.

    This stores the root node. All other nodes branch off from that.

    When creating a tree, you may pass no arguments, or a list of name servers
    to load, or a path or list of paths (as returned by
    rtctree.path.parse_path). If no arguments are given, the tree will load
    name servers from the environment variable specified in
    NAMESERVERS_ENV_VAR. If a list of servers are given, only those servers
    will be loaded.

    If paths are given, and the path is just '/', behaviour is as if no path
    argument were given. If a path starts with '/' and contains an element
    after it, that element will be treated as a name server. Otherwise the path
    is considered to be bad.

    '''
    def __init__(self, servers=None, paths=None, orb=None, *args, **kwargs):
        '''Constructor.

        @param servers A list of servers to parse into the tree.
        @param paths A list of paths from which to get servers to parse into
                     the tree.
        @param orb If not None, the specified ORB will be used. If None, the
                   tree object will create its own ORB. 
        @raises NonRootPathError

        '''
        super(RTCTree, self).__init__()
        self._root = TreeNode('/', None)
        self._create_orb(orb)
        if servers:
            self._parse_name_servers(servers)
        if paths:
            if type(paths[0]) == str:
                if paths[0][0] != '/':
                    raise NonRootPathError(paths[0])
                if len(paths) > 1:
                    self.add_name_server(paths[1])
            else:
                for p in paths:
                    if p[0] != '/':
                        raise NonRootPathError(p)
                    if len(p) > 1:
                        self.add_name_server(p[1])
            self.load_servers_from_env()
        if not servers and not paths:
            self.load_servers_from_env()

    def __del__(self):
        # Destructor to ensure the ORB shuts down correctly.
        if self._orb_is_mine:
            self._orb.shutdown(wait_for_completion=CORBA.FALSE)
            self._orb.destroy()

    def __str__(self):
        # Get a (potentially very large) string describing the tree.
        return str(self._root)

    def add_name_server(self, server):
        '''Parse a name server, adding its contents to the tree.

        @param server The address of the name server, in standard address
                      format. e.g. 'localhost', 'localhost:2809', '59.7.0.1'.

        '''
        self._parse_name_server(server)

    def get_node(self, path):
        '''Get a node by path.

        @param path A list of path elements pointing to a node in the tree.
                    For example, ['/', 'localhost', 'local.host_cxt']. The
                    first element in this path should be the root node's name.

        '''
        return self._root.get_node(path)

    def has_path(self, path):
        '''Check if the tree has a path.

        @param path A list of path elements pointing to a node in the tree.
                    For example, ['/', 'localhost', 'local.host_cxt']. The
                    first element in this path should be the root node's name.

        '''
        return self._root.has_path(path)

    def is_component(self, path):
        '''Is the node pointed to by @ref path a component?'''
        node = self.get_node(path)
        return node.is_component

    def is_directory(self, path):
        '''Is the node pointed to by @ref path a directory (name servers and
        naming contexts)?

        '''
        node = self.get_node(path)
        return node.is_directory

    def is_manager(self, path):
        '''Is the node pointed to by @ref path a manager?'''
        node = self.get_node(path)
        return node.is_manager

    def is_nameserver(self, path):
        '''Is the node pointed to by @ref path a name server (specialisation
        of directory nodes)?

        '''
        node = self.get_node(path)
        return node.is_nameserver

    def iterate(self, func, args=None, filter=[]):
        '''Call a function on the root node, and recursively all its children.

        This is a depth-first iteration.

        @param func The function to call. Its declaration must be
                    'def blag(node, args)', where 'node' is the current node
                    in the iteration and args is the value of @ref args.
        @param args Extra arguments to pass to the function at each iteration.
                    Pass multiple arguments in as a tuple.
        @param filter A list of filters to apply before calling func for each
                      node in the iteration. If the filter is not True,
                      @ref func will not be called for that node. Each filter
                      entry should be a string, representing on of the is_*
                      properties (is_component, etc), or a function object.
        @return The results of the calls to @ref func in a list.

        '''
        return self._root.iterate(func, args, filter)

    def load_servers_from_env(self):
        '''Load the name servers environment variable and parse each server in
        the list.

        '''
        if NAMESERVERS_ENV_VAR in os.environ:
            servers = [s for s in os.environ[NAMESERVERS_ENV_VAR].split(';') \
                         if s]
            self._parse_name_servers(servers)

    def _create_orb(self, orb=None):
        # Create the ORB, optionally checking the environment variable for
        # arguments to pass to the ORB.
        if orb:
            self._orb = orb
            self._orb_is_mine = False
        else:
            if ORB_ARGS_ENV_VAR in os.environ:
                orb_args = os.environ[ORB_ARGS_ENV_VAR].split(';')
            else:
                orb_args = []
            self._orb = CORBA.ORB_init(orb_args)
            self._orb_is_mine = True

    def _parse_name_servers(self, servers):
        # Parse a list of name servers.
        if type(servers) is str:
            self._parse_name_server(servers)
        else:
            for server in servers:
                self._parse_name_server(server)

    def _parse_name_server(self, address):
        # Parse a single name server and add it to the root node.
        new_ns_node = NameServer(self._orb, address, self._root)
        self._root._add_child(new_ns_node)


# vim: tw=79

