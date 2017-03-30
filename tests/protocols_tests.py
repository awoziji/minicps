"""
protocols_test.
"""

import os
import subprocess
import sys
import shlex
import time

import pymodbus
import cpppo

from minicps.protocols import Protocol, EnipProtocol, ModbusProtocol

from nose.tools import eq_
from nose.plugins.skip import SkipTest

# TODO: add new server keys
SERVER = {
    'address': 'localhost:44818',
    'tags': (('SENSOR1', 1, 'INT'), ('ACTUATOR1', 'INT')),
}
CLIENT_SERVER_PROTOCOL = {
    'name': 'enip',
    'mode': 1,
    'server': SERVER,
}

CLIENT_PROTOCOL = {
    'name': 'enip',
    'mode': 0,
    'server': '',
}

# TestProtocol {{{1
class TestProtocol():

    def test_init(self):

        enip = Protocol(
            protocol=CLIENT_SERVER_PROTOCOL)
        eq_(enip._name, 'enip')
        eq_(enip._mode, 1)
        eq_(enip._server['address'], 'localhost:44818')
        eq_(
            enip._server['tags'],
            (('SENSOR1', 1, 'INT'), ('ACTUATOR1', 'INT')))
        del enip

        enip = Protocol(
            protocol=CLIENT_PROTOCOL)
        eq_(enip._name, 'enip')
        eq_(enip._mode, 0)
        eq_(enip._server, {})  # pass an empty server dict

# }}}

# TestEniptProtocol {{{1
class TestEnipProtocol():

    # NOTE: second tuple element is the process id
    TAGS = (
        ('SENSOR1', 1, 'INT'),
        ('SENSOR1', 2, 'INT'),
        ('ACTUATOR1', 'INT'))
    SERVER = {
        'address': 'localhost:44818',
        'tags': TAGS
    }
    CLIENT_SERVER_PROTOCOL = {
        'name': 'enip',
        'mode': 1,
        'server': SERVER,
    }
    CLIENT_PROTOCOL = {
        'name': 'enip',
        'mode': 0,
        'server': '',
    }
    if sys.platform.startswith('linux'):
        SHELL = '/bin/bash -c '
        CLIENT_LOG = '--log logs/protocols_tests_enip_client '
    else:
        raise OSError

    @SkipTest
    def test_init(self):

        # TODO: add _stop_server
        enip = EnipProtocol(
            protocol=TestEnipProtocol.CLIENT_PROTOCOL)
        eq_(enip._name, 'enip')
        del enip
        enip = EnipProtocol(
            protocol=TestEnipProtocol.CLIENT_SERVER_PROTOCOL)
        eq_(enip._name, 'enip')

    def test_server_stop(self):

        cmd = EnipProtocol._start_server_cmd()
        try:
            server = subprocess.Popen(cmd, shell=False)
            EnipProtocol._stop_server(server)

        except Exception as error:
            print 'ERROR test_server_stop: ', error

    @SkipTest
    def test_server_start(self):

        ADDRESS = 'localhost:44818'  # TEST port
        TAGS = (('SENSOR1', 'INT'), ('ACTUATOR1', 'INT'))
        try:
            print "TEST: client has to kill the cpppo process."
            EnipProtocol._start_server(ADDRESS, TAGS)
            # TODO: add _stop_server
        except Exception as error:
            print 'ERROR test_server_start: ', error

    def test_server_multikey(self):

        TAGS = (('SENSOR1', 1, 'INT'), ('ACTUATOR1', 'INT'))
        cmd = EnipProtocol._start_server_cmd(tags=TAGS)
        try:
            server = subprocess.Popen(cmd, shell=False)
            EnipProtocol._stop_server(server)
        except Exception as error:
            print 'ERROR test_server_multikey: ', error

    def test_server_udp(self):

        pass

    def test_send_multikey(self):

        enip = EnipProtocol(
            protocol=CLIENT_PROTOCOL)

        TAGS = (('SENSOR1', 1, 'INT'), ('ACTUATOR1', 'INT'))
        cmd = EnipProtocol._start_server_cmd(tags=TAGS)
        try:
            server = subprocess.Popen(cmd, shell=False)

            # write a multikey
            what = ('SENSOR1', 1)
            address = 'localhost:44818'
            for value in range(5):
                enip._send(what, value, address)

            # write a single key
            what = ('ACTUATOR1',)
            address = 'localhost:44818'
            for value in range(5):
                enip._send(what, value, address)

            EnipProtocol._stop_server(server)

        except Exception as error:
            EnipProtocol._stop_server(server)
            print 'ERROR test_client: ', error

    def test_receive_multikey(self):

        enip = EnipProtocol(
            protocol=CLIENT_PROTOCOL)

        TAGS = (('SENSOR1', 1, 'INT'), ('ACTUATOR1', 'INT'))
        cmd = EnipProtocol._start_server_cmd(tags=TAGS)
        try:
            server = subprocess.Popen(cmd, shell=False)

            # read a multikey
            what = ('SENSOR1', 1)
            address = 'localhost:44818'
            enip._receive(what, address)

            # read a single key
            what = ('ACTUATOR1',)
            address = 'localhost:44818'
            enip._receive(what, address)

            EnipProtocol._stop_server(server)

        except Exception as error:
            EnipProtocol._stop_server(server)
            print 'ERROR test_client: ', error

    def test_client_server(self):

        try:
            enip = EnipProtocol(
                protocol=CLIENT_SERVER_PROTOCOL)

            # read a multikey
            what = ('SENSOR1', 1)
            address = 'localhost:44818'
            enip._receive(what, address)

            # read a single key
            what = ('ACTUATOR1',)
            address = 'localhost:44818'
            enip._receive(what, address)

            # write a multikey
            what = ('SENSOR1', 1)
            address = 'localhost:44818'
            for value in range(5):
                enip._send(what, value, address)

            # write a single key
            what = ('ACTUATOR1',)
            address = 'localhost:44818'
            for value in range(5):
                enip._send(what, value, address)

            EnipProtocol._stop_server(enip._server_subprocess)

        except Exception as error:
            EnipProtocol._stop_server(enip._server_subprocess)
            print 'ERROR test_client_server: ', error

# }}}

# TestModbusProtocol {{{1
class TestModbusProtocol():

    # NOTE: second tuple element is the process id
    TAGS = (
        ('CO1', 1, 'CO'),
        ('CO1', 2, 'CO'),
        ('DI1', 1, 'DI'),
        ('DI1', 2, 'DI'),
        ('HR1', 1, 'HR'),
        ('HR2', 2, 'HR'),
        ('IR1', 1, 'IR'),
        ('IR2', 4, 'IR'))
    SERVER = {
        'address': 'localhost:502',
        'tags': TAGS
    }
    CLIENT_SERVER_PROTOCOL = {
        'name': 'modbus',
        'mode': 1,
        'server': SERVER,
    }
    CLIENT_PROTOCOL = {
        'name': 'modbus',
        'mode': 0,
        'server': '',
    }
    if sys.platform.startswith('linux'):
        SHELL = '/bin/bash -c '
        CLIENT_LOG = '--log logs/protocols_tests_modbus_client '
    else:
        raise OSError

    # TODO
    @SkipTest
    def test_init(self):

        # TODO: add _stop_server
        modbus = ModbusProtocol(
            protocol=TestModbusProtocol.CLIENT_PROTOCOL)
        eq_(modbus._name, 'modbustcp')
        del modbus
        modbus = ModbusProtocol(
            protocol=TestModbusProtocol.CLIENT_SERVER_PROTOCOL)
        eq_(modbus._name, 'modbustcp')

    @SkipTest
    def test_server_stop(self):

        cmd = ModbusProtocol._start_server_cmd()
        try:
            server = subprocess.Popen(cmd, shell=False)
            ModbusProtocol._stop_server(server)

        except Exception as error:
            print 'ERROR test_server_stop: ', error

    # TODO
    @SkipTest
    def test_server_start(self):

        ADDRESS = 'localhost:44818'  # TEST port
        TAGS = (('SENSOR1', 'INT'), ('ACTUATOR1', 'INT'))
        try:
            print "TEST: client has to kill the cpppo process."
            ModbusProtocol._start_server(ADDRESS, TAGS)
            # TODO: add _stop_server
        except Exception as error:
            print 'ERROR test_server_start: ', error

    def test_server_start_stop(self):

        cmd = ModbusProtocol._start_server_cmd(tags=self.TAGS)
        try:
            server = subprocess.Popen(cmd, shell=False)
            ModbusProtocol._stop_server(server)
        except Exception as error:
            print 'ERROR test_server_start_stop: ', error

    # TODO
    @SkipTest
    def test_server_udp(self):

        pass

    # TODO
    @SkipTest
    def test_send_multikey(self):

        enip = ModbusProtocol(
            protocol=CLIENT_PROTOCOL)

        TAGS = (('SENSOR1', 1, 'INT'), ('ACTUATOR1', 'INT'))
        cmd = ModbusProtocol._start_server_cmd(tags=TAGS)
        try:
            server = subprocess.Popen(cmd, shell=False)

            # write a multikey
            what = ('SENSOR1', 1)
            address = 'localhost:44818'
            for value in range(5):
                enip._send(what, value, address)

            # write a single key
            what = ('ACTUATOR1',)
            address = 'localhost:44818'
            for value in range(5):
                enip._send(what, value, address)

            ModbusProtocol._stop_server(server)

        except Exception as error:
            ModbusProtocol._stop_server(server)
            print 'ERROR test_client: ', error

    # TODO
    @SkipTest
    def test_receive_multikey(self):

        enip = ModbusProtocol(
            protocol=CLIENT_PROTOCOL)

        TAGS = (('SENSOR1', 1, 'INT'), ('ACTUATOR1', 'INT'))
        cmd = ModbusProtocol._start_server_cmd(tags=TAGS)
        try:
            server = subprocess.Popen(cmd, shell=False)

            # read a multikey
            what = ('SENSOR1', 1)
            address = 'localhost:44818'
            enip._receive(what, address)

            # read a single key
            what = ('ACTUATOR1',)
            address = 'localhost:44818'
            enip._receive(what, address)

            ModbusProtocol._stop_server(server)

        except Exception as error:
            ModbusProtocol._stop_server(server)
            print 'ERROR test_client: ', error

    # TODO
    @SkipTest
    def test_client_server(self):

        try:
            enip = ModbusProtocol(
                protocol=CLIENT_SERVER_PROTOCOL)

            # read a multikey
            what = ('SENSOR1', 1)
            address = 'localhost:44818'
            enip._receive(what, address)

            # read a single key
            what = ('ACTUATOR1',)
            address = 'localhost:44818'
            enip._receive(what, address)

            # write a multikey
            what = ('SENSOR1', 1)
            address = 'localhost:44818'
            for value in range(5):
                enip._send(what, value, address)

            # write a single key
            what = ('ACTUATOR1',)
            address = 'localhost:44818'
            for value in range(5):
                enip._send(what, value, address)

            ModbusProtocol._stop_server(enip._server_subprocess)

        except Exception as error:
            ModbusProtocol._stop_server(enip._server_subprocess)
            print 'ERROR test_client_server: ', error

# }}}
