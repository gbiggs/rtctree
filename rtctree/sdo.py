# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtctree

Copyright (C) 2009-2011
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

SDO client objects.

'''


import OpenRTM__POA
import RTC
import SDOPackage


class RTCObserver(OpenRTM__POA.ComponentObserver):
    def __init__(self, target):
        self._tgt = target

    def update_status(self, kind, hint):
        kind = str(kind)
        if kind == 'COMPONENT_PROFILE':
            self._tgt._profile_update([x.strip() for x in hint.split(',')])
        elif kind == 'RTC_STATUS':
            status, ec_id = hint.split(':')
            if status == 'INACTIVE':
                status = self._tgt.INACTIVE
            elif status == 'ACTIVE':
                status = self._tgt.ACTIVE
            elif status == 'ERROR':
                status = self._tgt.ERROR
            self._tgt._set_state_in_ec(int(ec_id), status)
        elif kind == 'EC_STATUS':
            event, ec_id = hint.split(':')
            if event == 'ATTACHED':
                event = self._tgt.ATTACHED
            elif event == 'DETACHED':
                event = self._tgt.DETACHED
            elif event == 'RATE_CHANGED':
                event = self._tgt.RATE_CHANGED
            elif event == 'STARTUP':
                event = self._tgt.STARTUP
            elif event == 'SHUTDOWN':
                event = self._tgt.SHUTDOWN
            self._tgt._ec_event(int(ec_id), event)
        elif kind == 'PORT_PROFILE':
            print 'PORT_PROFILE', hint
        elif kind == 'CONFIGURATION':
            print 'CONFIGURATION', hint
        elif kind == 'HEARTBEAT':
            self._tgt._heartbeat()


class RTCLogger(OpenRTM__POA.Logger):
    def __init__(self, target, callback):
        self._tgt = target
        self._cb = callback

    def publish(self, record):
        ts = record.time.sec + record.time.nsec / 1e9
        self._cb(self._tgt.name, ts, loggername, level, message)


# vim: tw=79

