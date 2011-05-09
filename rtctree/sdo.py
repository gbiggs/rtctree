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
            print 'COMPONENT_PROFILE', hint
        elif kind == 'RTC_STATUS':
            status, ec_id = hint.split(':')
            print status, ec_id
            if status == 'INACTIVE':
                status = self._tgt.INACTIVE
            elif status == 'ACTIVE':
                status = self._tgt.ACTIVE
            elif status == 'ERROR':
                status = self._tgt.ERROR
            self._tgt._set_ec_state(int(ec_id), status)
        elif kind == 'EC_STATUS':
            print 'EC_STATUS', hint
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

