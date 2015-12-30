#
# Project Ginger S390x
#
# Copyright IBM, Corp. 2015
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import unittest

import utils
from tests.fvt.fvt_base import TestBase
from tests.fvt.restapilib import APIRequestError


CONFIGFILE = 'config'
STORAGE_DEVICES_SECTION = 'Storage I/O Devices'
DASD_ECKD = 'dasd-eckd'
ZFCP = 'zfcp'
ONLINE_DASDECKD_OPT = 'online_dasdeckd_device'
OFFLINE_DASDECKD_OPT = 'offline_dasdeckd_device'
ONLINE_ZFCP_OPT = 'online_zfcp_device'
OFFLINE_ZFCP_OPT = 'offline_zfcp_device'


class TestStorageIODevices(TestBase):
    """
    Represents test case that could help in testing the REST
    API supported for storage i/o devices.
    Attributes:
        \param TestBase
         config file which contains all configuration
            information with sections
    """
    uri_storagedevices = '/plugins/gingers390x/storagedevices'
    storagedevices_schema = {"type": "object",
                             "properties": {"status": {"type": "string"},
                                            "cu_type": {"type": "string"},
                                            "pim": {"type": "string"},
                                            "chipid": {"type": "string"},
                                            "pom": {"type": "string"},
                                            "device_type": {"type": "string"},
                                            "sub_channel": {"type": "string"},
                                            "device": {"type": "string"},
                                            "pam": {"type": "string"}
                                            }
                             }

    online_dasdeckd_device = None
    offline_dasdeckd_device = None
    online_zfcp_device = None
    offline_zfcp_device = None

    @classmethod
    def setUpClass(self):
        super(TestStorageIODevices, self).setUpClass()
        self.logging.info('--> TestStorageIODevices.setUpClass()')
        self.logging.debug(
            'Reading storage i/o devices information from config file')
        self.online_dasdeckd_device = utils.readconfig(
            self.session, CONFIGFILE, STORAGE_DEVICES_SECTION,
            ONLINE_DASDECKD_OPT)
        self.offline_dasdeckd_device = utils.readconfig(
            self.session, CONFIGFILE, STORAGE_DEVICES_SECTION,
            OFFLINE_DASDECKD_OPT)
        self.online_zfcp_device = utils.readconfig(
            self.session, CONFIGFILE, STORAGE_DEVICES_SECTION,
            ONLINE_ZFCP_OPT)
        self.offline_zfcp_device = utils.readconfig(
            self.session, CONFIGFILE, STORAGE_DEVICES_SECTION,
            OFFLINE_ZFCP_OPT)
        self.logging.debug(
            'Successfully read storage i/o devices information from config '
            'file. Online dasd-eckd device: %s, offline dasd-eckd device: '
            '%s, online zfcp device: %s, offline zfcp device: %s'
            % (self.online_dasdeckd_device, self.offline_dasdeckd_device,
               self.online_zfcp_device, self.offline_zfcp_device))
        self.logging.info('<-- TestStorageIODevices.setUpClass()()')

    def test_S001_retrieve_all_storagedevices(self):
        """
        Retrieve summarized list of defined storage I/O devices of
        type DASD_ECKD and ZFCP. It should return collection of resources
        """
        self.logging.info(
            '-->TestStorageIODevices.test_S001_retrieve_all_storagedevices()')
        try:
            self.logging.debug(
                'Retrieving summarized list of all storage i/o devices of '
                'type %s and %s using URI %s' %
                (DASD_ECKD, ZFCP, self.uri_storagedevices))
            resp = self.session.request_get_json(
                self.uri_storagedevices, expected_status_values=[200])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                for each_json in resp:
                    self.logging.debug(
                        'validating json %s against default json schema '
                        'of storage i/o device' % each_json)
                    self.validator.validate_json(
                        each_json, self.storagedevices_schema)
            else:
                self.logging.debug('Response is None/Empty')
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestStorageIODevices.test_S001_'
                'retrieve_all_storagedevices()')

    def test_S002_retrieve_dasdeckd_storagedevices(self):
        """
        Retrieve summarized list of defined storage I/O devices of
        type DASD_ECKD. It should return collection of resources
        """
        self.logging.info(
            '-->TestStorageIODevices.test_S002_retrieve'
            '_dasdeckd_storagedevices()')
        try:
            uri_dasdeckd = self.uri_storagedevices + '?_type=' + DASD_ECKD
            self.logging.debug(
                'Retrieving summarized list of all storage i/o devices of'
                ' type %s using URI %s' % (DASD_ECKD, uri_dasdeckd))
            resp = self.session.request_get_json(
                uri_dasdeckd, expected_status_values=[200])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                for each_json in resp:
                    self.logging.debug(
                        'validating json %s against default json schema of'
                        ' storage i/o device' % each_json)
                    self.validator.validate_json(
                        each_json, self.storagedevices_schema)
            else:
                self.logging.debug('Response is None/Empty')
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestStorageIODevices.test_S002_retrieve'
                '_dasdeckd_storagedevices()')

    def test_S003_retrieve_zfcp_storagedevices(self):
        """
        Retrieve summarized list of defined storage I/O devices of
        type ZFCP. It should return collection of resources
        """
        self.logging.info(
            '-->TestStorageIODevices.test_S003_retrieve_'
            'zfcp_storagedevices()')
        try:
            uri_zfcp = self.uri_storagedevices + '?_type=' + ZFCP
            self.logging.debug(
                'Retrieving summarized list of all storage i/o devices of'
                ' type %s using URI %s' % (ZFCP, uri_zfcp))
            resp = self.session.request_get_json(
                uri_zfcp, expected_status_values=[200])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                for each_json in resp:
                    self.logging.debug(
                        'validating json %s against default json schema of '
                        'storage i/o device' % each_json)
                    self.validator.validate_json(
                        each_json, self.storagedevices_schema)
            else:
                self.logging.debug('Response is None/Empty')
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestStorageIODevices.test_S003_'
                'retrieve_zfcp_storagedevices()')

    def test_F004_retrieve_storagedevices_invalidtype(self):
        """
        Negative test case to validate _type filter of /storagedevice api
        with invalid type filter. It should return status code 400
        """
        self.logging.info(
            '-->TestStorageIODevices.test_F004_retrieve_'
            'storagedevices_invalidtype()')
        try:
            uri_invalid_type = self.uri_storagedevices + '?_type=invalid_type'
            self.logging.debug(
                'Retrieving storage i/o devices with invalid _type filter'
                ' using URI %s' % uri_invalid_type)
            resp = self.session.request_get_json(
                uri_invalid_type, expected_status_values=[400])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.info('As expected, received 400 status code')
            else:
                self.logging.debug(
                    'Received None/Empty json response instead'
                    ' of 400 status code')
                self.fail(
                    'Received None/Empty json response instead of 400 status'
                    ' code for URI %s' % uri_invalid_type)
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestStorageIODevices.test_F004_retrieve_'
                'storagedevices_invalidtype()')

    def test_S005_get_storagedevice(self):
        """
        Retrieve detailed information of a single storage i/o device
        """
        self.logging.info(
            '-->TestStorageIODevices.test_S005_get_storagedevice()')
        self.logging.debug(
            'Retrieving summarized list of all storage i/o devices of '
            'type %s and %s using URI %s' %
            (DASD_ECKD, ZFCP, self.uri_storagedevices))
        resp = self.session.request_get_json(
            self.uri_storagedevices, expected_status_values=[200])
        if resp:
            self.logging.debug('Response received: %s' % resp)
            for each_json in resp:
                self.logging.debug(
                    'validating json %s against default json schema of '
                    'storage i/o device' % each_json)
                self.validator.validate_json(
                    each_json, self.storagedevices_schema)
            storage_device = resp[0]['device']
            device_uri = self.uri_storagedevices + '/' + storage_device
            try:
                self.logging.debug(
                    'Retrieving detailed information of storage i/o '
                    'device %s using uri %s' % (storage_device, device_uri))
                device_resp = self.session.request_get_json(
                    device_uri, expected_status_values=[200])
                if device_resp:
                    self.logging.debug('Response received: %s' % device_resp)
                    self.validator.validate_json(
                        device_resp, self.storagedevices_schema)
                else:
                    self.logging.error(
                        'Failed to fetch details of storage i/o device %s. '
                        'Received None/Empty response' % storage_device)
                    self.fail(
                        'Failed to fetch details of storage i/o device %s. '
                        'Received None/Empty response' % storage_device)
            except APIRequestError as error:
                self.logging.error(error.__str__())
                raise Exception(error)
        else:
            self.logging.info('Storage I/O Devices response is None/Empty')
            raise unittest.SkipTest("No storage i/o device found")
        self.logging.info(
            '<--TestStorageIODevices.test_S005_get_storagedevice()')

    def test_S006_get_dasdeckd_device(self):
        """
        Retrieve detailed information of a storage
        i/o device of type dasd-eckd
        """
        self.logging.info(
            '-->TestStorageIODevices.test_S006_get_dasdeckd_device()')
        if self.online_dasdeckd_device:
            dasdeckd_device = self.online_dasdeckd_device
        elif self.offline_dasdeckd_device:
            dasdeckd_device = self.offline_dasdeckd_device
        else:
            raise unittest.SkipTest(
                'Skipping test_S005_get_dasdeckd_device() since '
                'no dasd-eckd device is specified in config file')
        device_uri = self.uri_storagedevices + '/' + dasdeckd_device
        try:
            self.logging.debug(
                'Retrieving detailed information of a dasd-eckd storage '
                'i/o device %s using URI %s'
                % (dasdeckd_device, device_uri))
            resp = self.session.request_get_json(
                device_uri, expected_status_values=[200])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.debug(
                    'validating json %s against default json schema of '
                    'storage i/o device' % resp)
                self.validator.validate_json(
                    resp, self.storagedevices_schema)
            else:
                self.logging.error(
                    'Failed to fetch details of dasd-eckd storage i/o device'
                    ' %s. Received None/Empty response' % dasdeckd_device)
                self.fail(
                    'Failed to fetch details of dasd-eckd storage i/o device '
                    '%s. Received None/Empty response' % dasdeckd_device)
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)

        finally:
            self.logging.info(
                '<--TestStorageIODevices.test_S006_get_dasdeckd_device()')

    def test_S007_get_zfcp_device(self):
        """
        Retrieve detailed information of a storage
        i/o device of type zfcp
        """
        self.logging.info(
            '-->TestStorageIODevices.test_S007_get_zfcp_device()')
        if self.online_zfcp_device:
            zfcp_device = self.online_zfcp_device
        elif self.offline_zfcp_device:
            zfcp_device = self.offline_zfcp_device
        else:
            raise unittest.SkipTest(
                'Skipping test_S007_get_zfcp_device() since '
                'no zfcp device is specified in config file')
        device_uri = self.uri_storagedevices + '/' + zfcp_device
        try:
            self.logging.debug(
                'Retrieving detailed information of a zfcp storage i/o '
                'device %s using URI %s' % (zfcp_device, device_uri))
            resp = self.session.request_get_json(
                device_uri, expected_status_values=[200])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.debug(
                    'validating json %s against default json schema of '
                    'storage i/o device' % resp)
                self.validator.validate_json(
                    resp, self.storagedevices_schema)
            else:
                self.logging.error(
                    'Failed to fetch details of zfcp storage i/o device %s.'
                    ' Received None/Empty response' % zfcp_device)
                self.fail(
                    'Failed to fetch details of zfcp storage i/o device %s.'
                    ' Received None/Empty response' % zfcp_device)
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)

        finally:
            self.logging.info(
                '<--TestStorageIODevices.test_S007_get_zfcp_device()')

    def test_F008_get_invalid_device(self):
        """
        Negative test case to retrieve detailed information of
        invalid storage i/o device. It should return 400 status code
        """
        self.logging.info(
            '-->TestStorageIODevices.test_F008_get_invalid_device()')
        device_id = 'invalid_device'
        device_uri = self.uri_storagedevices + '/' + device_id
        try:
            self.logging.debug(
                'Retrieving detailed information of an invalid storage i/o '
                'device %s using URI %s' % (device_id, device_uri))
            resp = self.session.request_get_json(
                device_uri, expected_status_values=[400])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.info('As expected, received 400 status code')
            else:
                self.logging.error(
                    'Received None/Empty response instead of 400 status code'
                    ' for an invalid device id')
                self.fail(
                    'Received None/Empty response instead of 400 status code'
                    ' for an invalid device id')
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)

        finally:
            self.logging.info(
                '<--TestStorageIODevices.test_F008_get_invalid_device()')

    def test_S009_dasdeckd_online_valid(self):
        """
        method to test 'online' action on dasd-eckd storage i/o
        device(/storagedevices api) to bring valid dasd-eckd device online
        """
        self.logging.info(
            '-->TestStorageIODevices.test_S009_dasdeckd_online_valid()')
        if not self.offline_dasdeckd_device:
            raise unittest.SkipTest(
                'Skipping test_S009_dasdeckd_online_valid() since no offline'
                ' dasd-eckd storage i/o device is specified in config file')
        device_uri = \
            self.uri_storagedevices + '/' + \
            self.offline_dasdeckd_device + '/online'
        try:
            self.logging.debug(
                'Bringing dasd-eckd storage i/o device %s online using URI '
                '%s' % (self.offline_dasdeckd_device, device_uri))
            resp = self.session.request_post_json(
                device_uri, expected_status_values=[200])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.debug(
                    'validating json %s against default json schema of '
                    'storage i/o device' % resp)
                if not resp['status'] == 'online':
                    self.fail(
                        'Failed to bring dasd-eckd storage i/o device %s'
                        ' online' % self.offline_dasdeckd_device)
                self.logging.debug(
                    'online action on dasd-eckd storage i/o device %s'
                    ' using URI %s to bring it online is successful'
                    % (self.offline_dasdeckd_device, device_uri))
            else:
                self.logging.error(
                    'Received None/Empty response for online action on '
                    'dasd-eckd storage i/o device %s using URI %s'
                    % (self.offline_dasdeckd_device, device_uri))
                self.fail(
                    'Received None/Empty response for online action on '
                    'dasd-eckd storage i/o device %s using URI %s'
                    % (self.offline_dasdeckd_device, device_uri))
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)

        finally:
            self.logging.info(
                '<--TestStorageIODevices.test_S009_dasdeckd_online_valid()')

    def test_S010_dasdeckd_offline_valid(self):
        """
        method to test 'offline' action on dasd-eckd storage i/o
        device(/storagedevices api) to bring valid dasd-eckd device offline
        """
        self.logging.info(
            '-->TestStorageIODevices.test_S010_dasdeckd_offline_valid()')
        if not self.online_dasdeckd_device:
            raise unittest.SkipTest(
                'Skipping test_S010_dasdeckd_offline_valid() since no online'
                ' dasd-eckd storage i/o device is specified in config file')
        device_uri = \
            self.uri_storagedevices + '/' +  \
            self.online_dasdeckd_device + '/offline'
        try:
            self.logging.debug(
                'Bringing dasd-eckd storage i/o device %s offline using URI '
                '%s' % (self.online_dasdeckd_device, device_uri))
            resp = self.session.request_post_json(
                device_uri, expected_status_values=[200])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.debug(
                    'validating json %s against default json schema of '
                    'storage i/o device' % resp)
                if not resp['status'] == 'offline':
                    self.fail(
                        'Failed to bring dasd-eckd storage i/o device %s'
                        ' offline' % self.online_dasdeckd_device)
                self.logging.debug(
                    'offline action on dasd-eckd storage i/o device %s'
                    ' using URI %s to bring it offline is successful'
                    % (self.online_dasdeckd_device, device_uri))
            else:
                self.logging.error(
                    'Received None/Empty response for offline action on '
                    'dasd-eckd storage i/o device %s using URI %s'
                    % (self.online_dasdeckd_device, device_uri))
                self.fail(
                    'Received None/Empty response for offline action on '
                    'dasd-eckd storage i/o device %s using URI %s'
                    % (self.online_dasdeckd_device, device_uri))
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)

        finally:
            self.logging.info(
                '<--TestStorageIODevices.test_S010_dasdeckd_offline_valid()')

    def test_S011_zfcp_online_valid(self):
        """
        method to test 'online' action on zfcp storage i/o
        device(/storagedevices api) to bring valid zfcp device online
        """
        self.logging.info(
            '-->TestStorageIODevices.test_S011_zfcp_online_valid()')
        if not self.offline_zfcp_device:
            raise unittest.SkipTest(
                'Skipping test_S011_zfcp_online_valid() since no offline'
                ' zfcp storage i/o device is specified in config file')
        device_uri = \
            self.uri_storagedevices + '/' + \
            self.offline_zfcp_device + '/online'
        try:
            self.logging.debug(
                'Bringing zfcp storage i/o device %s online using URI '
                '%s' % (self.offline_zfcp_device, device_uri))
            resp = self.session.request_post_json(
                device_uri, expected_status_values=[200])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.debug(
                    'validating json %s against default json schema of '
                    'storage i/o device' % resp)
                if not resp['status'] == 'online':
                    self.fail(
                        'Failed to bring zfcp storage i/o device %s'
                        ' online' % self.offline_zfcp_device)
                self.logging.debug(
                    'online action on zfcp storage i/o device %s'
                    ' using URI %s to bring it online is successful'
                    % (self.offline_zfcp_device, device_uri))
            else:
                self.logging.error(
                    'Received None/Empty response for online action on '
                    'zfcp storage i/o device %s using URI %s'
                    % (self.offline_zfcp_device, device_uri))
                self.fail(
                    'Received None/Empty response for online action on '
                    'zfcp storage i/o device %s using URI %s'
                    % (self.offline_zfcp_device, device_uri))
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)

        finally:
            self.logging.info(
                '<--TestStorageIODevices.test_S011_zfcp_online_valid()')

    def test_S012_zfcp_offline_valid(self):
        """
        method to test 'offline' action on zfcp storage i/o
        device(/storagedevices api) to bring valid zfcp device offline
        """
        self.logging.info(
            '-->TestStorageIODevices.test_S012_zfcp_offline_valid()')
        if not self.online_zfcp_device:
            raise unittest.SkipTest(
                'Skipping test_S012_zfcp_offline_valid() since no online'
                ' zfcp storage i/o device is specified in config file')
        device_uri = \
            self.uri_storagedevices + '/' + \
            self.online_zfcp_device + '/offline'
        try:
            self.logging.debug(
                'Bringing zfcp storage i/o device %s offline using URI '
                '%s' % (self.online_zfcp_device, device_uri))
            resp = self.session.request_post_json(
                device_uri, expected_status_values=[200])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.debug(
                    'validating json %s against default json schema of '
                    'storage i/o device' % resp)
                if not resp['status'] == 'offline':
                    self.fail(
                        'Failed to bring zfcp storage i/o device %s'
                        ' offline' % self.online_zfcp_device)
                self.logging.debug(
                    'offline action on zfcp storage i/o device %s'
                    ' using URI %s to bring it offline is successful'
                    % (self.online_zfcp_device, device_uri))
            else:
                self.logging.error(
                    'Received None/Empty response for offline action on '
                    'zfcp storage i/o device %s using URI %s'
                    % (self.online_zfcp_device, device_uri))
                self.fail(
                    'Received None/Empty response for offline action on '
                    'zfcp storage i/o device %s using URI %s'
                    % (self.online_zfcp_device, device_uri))
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)

        finally:
            self.logging.info(
                '<--TestStorageIODevices.test_S012_zfcp_offline_valid()')

    def test_F013_invalid_online(self):
        """
        method to test 'online' action on an invalid storage i/o
        device(/storagedevices api) to bring it online
        """
        self.logging.info(
            '-->TestStorageIODevices.test_F013_invalid_online()')
        invalid_device = 'invalid_device'
        device_uri = \
            self.uri_storagedevices + '/' + \
            invalid_device + '/online'
        try:
            self.logging.debug(
                'Bringing invalid storage i/o device %s online using URI '
                '%s' % (invalid_device, device_uri))
            resp = self.session.request_post_json(
                device_uri, expected_status_values=[400])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.debug(
                    'As expected, failed to bring an invalid storage i/o'
                    ' device %s online using URI %s'
                    % (invalid_device, device_uri))
            else:
                self.logging.error(
                    'Received None/Empty response for online action on an '
                    'invalid storage i/o device %s using URI %s instead of'
                    ' 400 status code'
                    % (invalid_device, device_uri))
                self.fail(
                    'Received None/Empty response for online action on an '
                    'invalid storage i/o device %s using URI %s instead of'
                    ' 400 status code'
                    % (invalid_device, device_uri))
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)

        finally:
            self.logging.info(
                '<--TestStorageIODevices.test_F013_invalid_online()')

    def test_F014_invalid_offline(self):
        """
        method to test 'offline' action on an invalid storage i/o
        device(/storagedevices api) to bring it offline
        """
        self.logging.info(
            '-->TestStorageIODevices.test_F014_invalid_offline()')
        invalid_device = 'invalid_device'
        device_uri = \
            self.uri_storagedevices + '/' + \
            invalid_device + '/offline'
        try:
            self.logging.debug(
                'Bringing invalid storage i/o device %s offline using URI '
                '%s' % (invalid_device, device_uri))
            resp = self.session.request_post_json(
                device_uri, expected_status_values=[400])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.debug(
                    'As expected, failed to bring an invalid storage i/o'
                    ' device %s offline using URI %s'
                    % (invalid_device, device_uri))
            else:
                self.logging.error(
                    'Received None/Empty response for offline action on an '
                    'invalid storage i/o device %s using URI %s instead of'
                    ' 400 status code'
                    % (invalid_device, device_uri))
                self.fail(
                    'Received None/Empty response for offline action on an '
                    'invalid storage i/o device %s using URI %s instead of'
                    ' 400 status code'
                    % (invalid_device, device_uri))
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)

        finally:
            self.logging.info(
                '<--TestStorageIODevices.test_F014_invalid_offline()')
