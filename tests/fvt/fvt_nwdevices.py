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
NWDEVICES_SECTION = 'Network I/O Devices'
CONFIGURED_DEVICE_OPT = 'configured_device'
UNCONFIGURED_DEVICE_OPT = 'unconfigured_device'
UNCONFIGURED_OSA_DEVICE_OPT = 'unconfigure_device_osaport'

# variable to skip updation of osaport based on success/failure
# of configuring unconfigured_osa_device
skip_osaport_update = True


class TestNwdevices(TestBase):
    """
    Represents test case that could help in testing the REST API
    supported for network i/o devices

    Attributes:
        \param TestBase
         config file which contains all configuration
            information with sections
    """
    # Response json of network i/o device looks like
    # {"name":"enccw0.0.1530",
    #   "driver":"qeth",
    #   "card_type":"OSD_10GIG",
    #   "chpid":"03",
    #   "state":"online",
    #   "device_ids":[
    #     "0.0.1530",
    #     "0.0.1531",
    #     "0.0.1532"
    #   ],
    #   "type":"1731/01"
    # }
    nwdevice_schema = {"type": "object",
                       "properties": {"name": {"type": "string"},
                                      "driver": {"type": "string"},
                                      "card_type": {"type": "string"},
                                      "state": {"type": "string"},
                                      "device_ids": {"type": "array"},
                                      "type": {"type": "string"},
                                      "osa_portno": {"type": ["string", "integer"]}
                                      }
                       }
    # POST action configure/unconfigure api returns a task resource
    task_schema = {"type": "object",
                   "properties": {"status": {"type": "string"},
                                  "message": {"type": "string"},
                                  "id": {"type": "string"},
                                  "target_uri": {"type": "string"},
                                  }
                   }
    uri_nwdevices = '/plugins/gingers390x/nwdevices'
    uri_task = '/plugins/gingers390x/tasks'
    configured_device = None
    unconfigured_device = None
    unconfigured_osa_device = None

    @classmethod
    def setUpClass(self):
        super(TestNwdevices, self).setUpClass()
        self.logging.info('--> TestNwdevices.setUpClass()')
        self.logging.debug(
            'Reading network i/o devices information from config file')
        self.configured_device = utils.readconfig(
            self.session, CONFIGFILE, NWDEVICES_SECTION,
            CONFIGURED_DEVICE_OPT)
        self.unconfigured_device = utils.readconfig(
            self.session, CONFIGFILE, NWDEVICES_SECTION,
            UNCONFIGURED_DEVICE_OPT)
        self.unconfigured_osa_device = utils.readconfig(
            self.session, CONFIGFILE, NWDEVICES_SECTION,
            UNCONFIGURED_OSA_DEVICE_OPT)
        self.logging.debug(
            'Successfully read network i/o devices information from config'
            ' file. Configured Device: %s, Un-Configured Device: %s'
            % (self.configured_device, self.unconfigured_device))
        self.logging.debug('prepare network device using utils')
        if utils.configure_nwdevice(self.session, self.configured_device):
            #if failed to configure network device, make it None
            self.configured_device = None
        else:
            # if successfully configured, use first device id of triplet
            self.configured_device = 'enccw' + self.configured_device.split(',')[0]
        if self.unconfigured_device:
            self.unconfigured_device = self.unconfigured_device.split(',')[0]
        self.logging.info('<-- TestNwdevices.setUpClass()')

    def test_S001_nwdevices_collection(self):
        """
        Retrieve summarized list of all defined Network I/O devices of type
        OSA /nwdevices information. It should return collection of resources
        """
        self.logging.info(
            '--> TestNwdevices.test_S001_nwdevices_collection()')
        try:
            self.logging.debug(
                'Retrieving summarized list of all defined Network I/O '
                'devices of type OSA, using URI %s' % self.uri_nwdevices)
            resp = self.session.request_get_json(
                self.uri_nwdevices, expected_status_values=[200])
            if resp:
                self.logging.debug(
                    'return json of network devices: %s' % resp)
                for nwdevice_josn in resp:
                    self.validator.validate_json(
                        nwdevice_josn, self.nwdevice_schema)
            else:
                self.logging.info(
                    'Network I/O Devices response is None/Empty')

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_S001_nwdevices_collection()')

    def test_S002_get_configured_nwdevices(self):
        """
        Retrieve summarized list configured Network I/O devices information
        of type OSA using filter _configured=True.
        It will return collection of resources
        """
        self.logging.info(
            '--> TestNwdevices.test_S002_get_configured_nwdevices()')
        uri_configured = self.uri_nwdevices + '?_configured=True'
        try:
            self.logging.debug(
                'Retrieving configured Network I/O devices of type OSA, '
                'using URI %s' % uri_configured)
            resp = self.session.request_get_json(
                uri_configured, expected_status_values=[200])
            if resp:
                self.logging.debug(
                    'return json of configured network devices: %s' % resp)
                for nwdevice_josn in resp:
                    self.validator.validate_json(
                        nwdevice_josn, self.nwdevice_schema)
            else:
                self.logging.info(
                    'Configured Network I/O Devices response is None/Empty')

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_S002_get_configured_nwdevices()')

    def test_S003_get_unconfigured_nwdevices(self):
        """
        Retrieve summarized list un-configured Network I/O devices
        information of type OSA using filter _configured=False. It
        will return collection of resources
        """
        self.logging.info(
            '--> TestNwdevices.test_S003_get_unconfigured_nwdevices()')
        uri_unconfigured = self.uri_nwdevices + '?_configured=False'
        try:
            self.logging.debug(
                'Retrieving un-configured Network I/O devices of type OSA, '
                'using URI %s' % uri_unconfigured)
            resp = self.session.request_get_json(
                uri_unconfigured, expected_status_values=[200])
            if resp:
                self.logging.debug(
                    'return json of un-configured network devices: %s' % resp)
                for nwdevice_josn in resp:
                    self.validator.validate_json(
                        nwdevice_josn, self.nwdevice_schema)
            else:
                self.logging.debug('Un-Configured Network I/O Devices '
                                   'response is None/Empty')

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_S003_get_unconfigured_nwdevices()')

    def test_F004_invalid_configured_filter(self):
        """
        Negative test case to validate _configured filter of /nwdevices api
        with invalid configured filter. It should return status code 400
        """
        self.logging.info(
            '--> TestNwdevices.test_F004_invalid_configured_filter()')
        uri_invalid_configured = self.uri_nwdevices + '?_configured=Invalid'
        try:
            self.logging.debug(
                'Retrieving network i/o devices with invalid _configured '
                'filter using URI %s' % uri_invalid_configured)
            resp = self.session.request_get_json(
                uri_invalid_configured, expected_status_values=[400])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.info('As expected, received 400 status code')
            else:
                self.logging.error(
                    'Received None/Empty response instead of 400 status '
                    'code for an invalid _configured filter')
                self.fail(
                    'Received None/Empty response instead of 400 status '
                    'code for an invalid _configured filter')
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_F004_invalid_configured_filter()')

    def test_S005_nwdevice_resource(self):
        """
        Retrieve detailed information of a single network i/o device.
        """
        self.logging.info('--> TestNwdevices.test_S005_nwdevice_resource()')

        self.logging.debug(
            'Retrieving summarized list of all defined Network I/O devices '
            'of type OSA, using URI %s' % self.uri_nwdevices)
        resp = self.session.request_get_json(
            self.uri_nwdevices, expected_status_values=[200])
        if resp:
            self.logging.debug('return json of network devices: %s' % resp)
            for nwdevice_josn in resp:
                self.validator.validate_json(
                    nwdevice_josn, self.nwdevice_schema)
            nwdevice = resp[0]['name']
            device_uri = self.uri_nwdevices + '/' + nwdevice
            try:
                self.logging.debug(
                    'Retrieving detailed information of network i/o device '
                    '%s using uri %s' % (nwdevice, device_uri))
                device_resp = self.session.request_get_json(
                    device_uri, expected_status_values=[200])
                if device_resp:
                    self.logging.debug(
                        'return json of network device %s: '
                        '%s' % (nwdevice, device_resp))
                    self.validator.validate_json(
                        device_resp, self.nwdevice_schema)
                else:
                    self.logging.error(
                        'Failed to fetch details of network i/o device %s. '
                        'Received None/Empty response' % nwdevice)
                    self.fail(
                        'Failed to fetch details of network i/o device %s. '
                        'Received None/Empty response' % nwdevice)
            except APIRequestError as error:
                self.logging.error(error.__str__())
                raise Exception(error)
        else:
            self.logging.info('Network I/O Devices response is None/Empty')
            raise unittest.SkipTest("No network i/o device found")
        self.logging.info('<-- TestNwdevices.test_S005_nwdevice_resource()')

    def test_S006_get_configured_nwdevice(self):
        """
        Retrieve detailed information of the configured network i/o device.
        """
        self.logging.info(
            '--> TestNwdevices.test_S006_get_configured_nwdevice()')
        if not self.configured_device:
            raise unittest.SkipTest(
                'Skipping test_S006_get_configured_nwdevice() since '
                'configured device is not specified in config file')
        uri_configured_device = \
            self.uri_nwdevices + '/' + self.configured_device
        try:
            self.logging.debug(
                'Retrieving detailed information of configured network '
                'device %s using uri %s' %
                (self.configured_device, uri_configured_device))
            resp = self.session.request_get_json(
                uri_configured_device, expected_status_values=[200])
            if resp:
                self.logging.debug(
                    'return json of configured network device %s: '
                    '%s' % (self.configured_device, resp))
                self.validator.validate_json(resp, self.nwdevice_schema)
            else:
                self.logging.error(
                    'Failed to fetch details of configured network i/o '
                    'device %s. Received None/Empty response'
                    % self.configured_device)
                self.fail(
                    'Failed to fetch details of configured network i/o '
                    'device %s. Received None/Empty response'
                    % self.configured_device)

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_S006_get_configured_nwdevice()')

    def test_S007_get_unconfigured_nwdevice(self):
        """
        Retrieve detailed information of the un-configured network i/o device.
        """
        self.logging.info(
            '--> TestNwdevices.test_S007_get_unconfigured_nwdevice()')
        if not self.unconfigured_device:
            raise unittest.SkipTest(
                'Skipping test_S007_get_unconfigured_nwdevice() since '
                'un-configured device is not specified in config file')
        uri_unconfigured_device = \
            self.uri_nwdevices + '/' + self.unconfigured_device
        try:
            self.logging.debug(
                'Retrieving detailed information of un-configured network '
                'device %s using uri %s' % (self.unconfigured_device,
                                            uri_unconfigured_device))
            resp = self.session.request_get_json(
                uri_unconfigured_device, expected_status_values=[200])
            if resp:
                self.logging.debug(
                    'return json of un-configured network device %s: '
                    '%s' % (self.unconfigured_device, resp))
                self.validator.validate_json(resp, self.nwdevice_schema)
            else:
                self.logging.error(
                    'Failed to fetch details of un-configured network i/o '
                    'device %s. Received None/Empty response'
                    % self.unconfigured_device)
                self.fail(
                    'Failed to fetch details of un-configured network i/o '
                    'device %s. Received None/Empty response'
                    % self.unconfigured_device)

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_S007_get_unconfigured_nwdevice()')

    def test_F008_get_invalid_nwdevice(self):
        """
        Negative test case to retrieve detailed information of an
        invalid network i/o device. It should return 400 status code
        """
        self.logging.info(
            '--> TestNwdevices.test_F008_get_invalid_nwdevice()')
        device_id = 'invalid_device'
        device_uri = self.uri_nwdevices + '/' + device_id
        try:
            self.logging.debug(
                'Retrieving detailed information of an invalid network i/o '
                'device %s using URI %s' % (device_id, device_uri))
            resp = self.session.request_get_json(
                device_uri, expected_status_values=[400])
            if resp:
                self.logging.debug('Response received: %s' % resp)
                self.logging.info('As expected, received 400 status code')
            else:
                self.logging.error(
                    'Received None/Empty response instead of 400 status '
                    'code for an invalid device id')
                self.fail(
                    'Received None/Empty response instead of 400 status '
                    'code for an invalid device id')
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_F008_get_invalid_nwdevice()')

    def test_S009_configure_valid_nwdevice(self):
        """
        method to test "configure" action of /nwdevices api to
        configure valid network i/o device
        """
        self.logging.info(
            '--> TestNwdevices.test_S009_configure_valid_nwdevice()')
        if not self.unconfigured_device:
            raise unittest.SkipTest(
                'Skipping test_S009_configure_valid_nwdevice() since '
                'un-configured device is not specified in config file')
        uri_configure_device = \
            self.uri_nwdevices + '/' + self.unconfigured_device + '/configure'
        try:
            self.logging.debug(
                'Configuring un-configured network i/o device %s using uri'
                ' %s' % (self.unconfigured_device, uri_configure_device))
            resp = self.session.request_post_json(
                uri_configure_device, expected_status_values=[200, 202])
            if resp:
                self.logging.debug(
                    'task json returned from configure network i/o '
                    'device: %s' % resp)
                self.validator.validate_json(resp, self.task_schema)
                task_id = resp['id']
                task_resp = utils.wait_task_status_change(
                    self.session, task_id, task_final_status='finished')
                self.validator.validate_json(task_resp, self.task_schema)
                assert (task_resp['status'] == 'finished'),\
                    "configure task failed. task json response: " \
                    "%s" % task_resp
                self.logging.info('Retrieving device information '
                                  'after configure action')
                conf_device = self.session.request_get_json(
                    self.uri_nwdevices + '/enccw' +
                    self.unconfigured_device, expected_status_values=[200])
                self.validator.validate_json(
                    conf_device, self.nwdevice_schema)
                if conf_device['state'] == 'Unconfigured':
                    self.fail(
                        'Device is not configured through configure action. '
                        'Device details after configure action: %s'
                        % conf_device)
                self.session.logging.debug(
                    'Device %s is configured successfully. Device details '
                    '%s' % (self.unconfigured_device, conf_device))
            else:
                self.logging.info(
                    'configure action on network i/o device %s returned '
                    'None/Empty response instead of task json'
                    % self.unconfigured_device)
                self.fail(
                    'configure action on network i/o device %s returned '
                    'None/Empty response instead of task json'
                    % self.unconfigured_device)

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_S009_configure_valid_nwdevice()')

    def test_F010_configure_invalid_nwdevice(self):
        """
        method to test "configure" action of /nwdevices api to
        configure invalid network i/o device
        """
        self.logging.info(
            '--> TestNwdevices.test_F010_configure_invalid_nwdevice()')
        nwdevice_id = 'invalid_device'
        uri_configure_device = \
            self.uri_nwdevices + '/' + nwdevice_id + '/configure'
        try:
            self.logging.debug(
                'Configuring invalid network i/o device %s using uri'
                ' %s' % (nwdevice_id, uri_configure_device))
            resp = self.session.request_post_json(
                uri_configure_device, expected_status_values=[400])
            if resp:
                self.logging.debug(
                    'As expected, failed to configure invalid device. '
                    'Response: %s' % resp)
            else:
                self.logging.info(
                    'configure action on network i/o device %s returned '
                    'None/Empty response' % nwdevice_id)
                self.fail(
                    'configure action on network i/o device %s returned '
                    'None/Empty response' % nwdevice_id)
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_F010_configure_invalid_nwdevice()')

    def test_S011_unconfigure_valid_nwdevice(self):
        """
        method to test "unconfigure" action of /nwdevices api to
        un-configure valid network i/o device
        """
        self.logging.info(
            '--> TestNwdevices.test_S011_unconfigure_valid_nwdevice()')
        if not self.configured_device:
            raise unittest.SkipTest(
                'Skipping test_S011_unconfigure_valid_nwdevice() since '
                'configured device is not specified in config file')
        uri_unconfigure_device = \
            self.uri_nwdevices + '/' + self.configured_device + '/unconfigure'
        try:
            self.logging.debug(
                'Un-Configuring configured network i/o device %s using uri'
                ' %s' % (self.configured_device, uri_unconfigure_device))
            resp = self.session.request_post_json(
                uri_unconfigure_device, expected_status_values=[200, 202])
            if resp:
                self.logging.debug(
                    'task json returned from unconfigure network i/o '
                    'device: %s' % resp)
                self.validator.validate_json(resp, self.task_schema)
                task_id = resp['id']
                task_resp = utils.wait_task_status_change(
                    self.session, task_id, task_final_status='finished')
                self.validator.validate_json(task_resp, self.task_schema)
                assert (task_resp['status'] == 'finished'),\
                    "unconfigure task failed. task json response: " \
                    "%s" % task_resp
                self.logging.info('Retrieving device information '
                                  'after unconfigure action')
                unconf_device = self.session.request_get_json(
                    self.uri_nwdevices + '/' +
                    self.configured_device.strip('enccw'),
                    expected_status_values=[200])
                self.validator.validate_json(
                    unconf_device, self.nwdevice_schema)
                if unconf_device['state'] != 'Unconfigured':
                    self.fail(
                        'Device is not un-configured through unconfigure '
                        'action. Device details after unconfigure action: '
                        '%s' % unconf_device)
                self.session.logging.debug(
                    'Device %s is un-configured successfully. Device details'
                    ' %s' % (self.configured_device, unconf_device))
            else:
                self.logging.info(
                    'unconfigure action on network i/o device %s returned '
                    'None/Empty response instead of task json'
                    % self.configured_device)
                self.fail(
                    'unconfigure action on network i/o device %s returned '
                    'None/Empty response instead of task json'
                    % self.configured_device)

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_S011_unconfigure_valid_nwdevice()')

    def test_F012_unconfigure_invalid_nwdevice(self):
        """
        method to test "unconfigure" action of /nwdevices api to
        un-configure invalid network i/o device
        """
        self.logging.info(
            '--> TestNwdevices.test_F012_unconfigure_invalid_nwdevice()')
        nwdevice_id = 'invalid_device'
        uri_unconfigure_device = \
            self.uri_nwdevices + '/' + nwdevice_id + '/unconfigure'
        try:
            self.logging.debug(
                'Un-Configuring invalid network i/o device %s using uri'
                ' %s' % (nwdevice_id, uri_unconfigure_device))
            resp = self.session.request_post_json(
                uri_unconfigure_device, expected_status_values=[400])
            if resp:
                self.logging.debug(
                    'As expected, failed to un-configure invalid device. '
                    'Response: %s' % resp)
            else:
                self.logging.info(
                    'unconfigure action on network i/o device %s returned '
                    'None/Empty response' % nwdevice_id)
                self.fail(
                    'unconfigure action on network i/o device %s returned '
                    'None/Empty response' % nwdevice_id)
        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_F012_unconfigure_invalid_nwdevice()')

    def test_S013_configure_nwdevice_with_osaport(self):
        """
        method to test "configure" action of /nwdevices/<device> api to
        configure valid network i/o device with osa port 1
        """
        self.logging.info(
            '--> TestNwdevices.test_S013_configure_nwdevice_with_osaport()')
        global skip_osaport_update
        if not self.unconfigured_osa_device:
            raise unittest.SkipTest(
                'Skipping test_S013_configure_nwdevice_with_osaport() since '
                'un-configured device which can be used for osa port test is'
                ' not specified in config file')
        uri_configure_device = self.uri_nwdevices + '/' +\
                               self.unconfigured_osa_device + '/configure'
        input_json = {'osa_portno': 1}
        try:
            self.logging.debug(
                'Configuring un-configured network i/o device %s using uri'
                ' %s with osa port 1' % (self.unconfigured_osa_device,
                                         uri_configure_device))
            resp = self.session.request_post_json(
                uri_configure_device, body=input_json,
                expected_status_values=[200, 202])
            if resp:
                self.logging.debug(
                    'task json returned from configure network i/o '
                    'device: %s' % resp)
                self.validator.validate_json(resp, self.task_schema)
                task_id = resp['id']
                task_resp = utils.wait_task_status_change(
                    self.session, task_id, task_final_status='finished')
                self.validator.validate_json(task_resp, self.task_schema)
                assert (task_resp['status'] == 'finished'),\
                    "configure task failed. task json response: " \
                    "%s" % task_resp
                self.logging.info('Retrieving device information '
                                  'after configure action')
                conf_device = self.session.request_get_json(
                    self.uri_nwdevices + '/enccw' +
                    self.unconfigured_osa_device, expected_status_values=[200])
                self.validator.validate_json(
                    conf_device, self.nwdevice_schema)
                if conf_device['state'] == 'Unconfigured':
                    self.fail(
                        'Device is not configured through configure action. '
                        'Device details after configure action: %s'
                        % conf_device)
                skip_osaport_update = False  # execute osa port update tests
                self.session.logging.debug(
                    'Device %s is configured successfully. Device details '
                    '%s' % (self.unconfigured_osa_device, conf_device))

            else:
                self.logging.info(
                    'configure action with osa port 1 on network i/o device '
                    '%s returned None/Empty response instead of task json'
                    % self.unconfigured_osa_device)
                self.fail(
                    'configure action with osa port 1 on network i/o device '
                    '%s returned None/Empty response instead of task json'
                    % self.unconfigured_osa_device)

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_S013_configure_nwdevice_with_osaport()')

    @unittest.skipIf(skip_osaport_update,
                     'since osa express network card is not configured. '
                     'test_S013_configure_nwdevice_with_osaport() failed')
    def test_S014_update_nwdevice_with_osaport0(self):
        """
        method to test "update" option of /nwdevices/<device> api to
        update osa port number as 0
        """
        self.logging.info(
            '--> TestNwdevices.test_S014_update_nwdevice_with_osaport0()')
        if not self.unconfigured_osa_device:
            raise unittest.SkipTest(
                'Skipping test_S014_update_nwdevice_with_osaport0() since '
                'un-configured device which can be used for osa port test is'
                ' not specified in config file')
        # after configuring unconfigured network i/o device in test case
        # test_S013_configure_nwdevice_with_osaport
        # interface name changes to 'enccw' + unconfigured_device_id
        interface_name = 'enccw' + self.unconfigured_osa_device
        uri_update_device = self.uri_nwdevices + '/' + interface_name
        input_json = {'osa_portno': 0}
        try:
            self.logging.debug(
                'Updating network i/o device %s with osa port 0 using uri'
                ' %s with osa port 0' % (interface_name,
                                         uri_update_device))
            resp = self.session.request_put_json(
                uri_update_device, body=input_json,
                expected_status_values=[200])
            if resp:
                self.logging.debug(
                    'validating response json %s with default schema of '
                    'network i/o device %s' % (resp, self.nwdevice_schema))
                self.validator.validate_json(
                    resp, self.nwdevice_schema)
                if resp['osa_portno'] != 0:
                    self.fail(
                        'OSA port number is not updated to zero through '
                        'update api. Device details after update action: %s'
                        % resp)
                self.session.logging.debug(
                    'Device %s is successfully updated with osa_port number '
                    '0. Device details %s' % (interface_name, resp))
            else:
                self.logging.info(
                    'update action with osa port 0 on network i/o device '
                    '%s returned None/Empty response' % interface_name)
                self.fail(
                    'update action with osa port 0 on network i/o device '
                    '%s returned None/Empty response' % interface_name)

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_S014_update_nwdevice_with_osaport0()')

    @unittest.skipIf(skip_osaport_update,
                     'since osa express network card is not configured. '
                     'test_S013_configure_nwdevice_with_osaport() failed')
    def test_S015_update_nwdevice_with_osaport1(self):
        """
        method to test "update" option of /nwdevices/<device> api to
        update osa port number as 1
        """
        self.logging.info(
            '--> TestNwdevices.test_S015_update_nwdevice_with_osaport1()')
        if not self.unconfigured_osa_device:
            raise unittest.SkipTest(
                'Skipping test_S015_update_nwdevice_with_osaport1() since '
                'un-configured device which can be used for osa port test is'
                ' not specified in config file')
        # after configuring unconfigured network i/o device in test case
        # test_S013_configure_nwdevice_with_osaport
        # interface name changes to 'enccw' + unconfigured_device_id
        interface_name = 'enccw' + self.unconfigured_osa_device
        uri_update_device = self.uri_nwdevices + '/' + interface_name
        input_json = {'osa_portno': 1}
        try:
            self.logging.debug(
                'Updating network i/o device %s with osa port 0 using uri'
                ' %s with osa port 1' % (interface_name,
                                         uri_update_device))
            resp = self.session.request_put_json(
                uri_update_device, body=input_json,
                expected_status_values=[200])
            if resp:
                self.logging.debug(
                    'validating response json %s with default schema of '
                    'network i/o device %s' % (resp, self.nwdevice_schema))
                self.validator.validate_json(
                    resp, self.nwdevice_schema)
                if resp['osa_portno'] != 1:
                    self.fail(
                        'OSA port number is not updated to 1, through '
                        'update api. Device details after update action: %s'
                        % resp)
                self.session.logging.debug(
                    'Device %s is successfully updated with osa_port number '
                    '1. Device details %s' % (interface_name, resp))
            else:
                self.logging.info(
                    'update action with osa port 1 on network i/o device '
                    '%s returned None/Empty response' % interface_name)
                self.fail(
                    'update action with osa port 1 on network i/o device '
                    '%s returned None/Empty response' % interface_name)

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_S015_update_nwdevice_with_osaport1()')

    @unittest.skipIf(skip_osaport_update,
                     'since osa express network card is not configured. '
                     'test_S013_configure_nwdevice_with_osaport() failed')
    def test_S016_update_nwdevice_with_invalid_osaport(self):
        """
        negative scenario to test "update" option of /nwdevices/<device> api
        to update osa port number other than 0/1
        this test should be called after test case -
        test_S013_configure_nwdevice_with_osaport,,, so keeping S016 in name
        """
        self.logging.info(
            '--> TestNwdevices.test_S016_update_nwdevice_with_invalid_osaport()')
        if not self.unconfigured_osa_device:
            raise unittest.SkipTest(
                'Skipping test_S016_update_nwdevice_with_invalid_osaport() since '
                'un-configured device which can be used for osa port test is'
                ' not specified in config file')
        # after configuring unconfigured network i/o device in test case
        # test_S013_configure_nwdevice_with_osaport
        # interface name changes to 'enccw' + unconfigured_device_id
        interface_name = 'enccw' + self.unconfigured_osa_device
        uri_update_device = self.uri_nwdevices + '/' + interface_name
        input_json = {'osa_portno': 4}
        # osa port 4 is not available on any OSA Express card
        try:
            self.logging.debug(
                'Negative test case - updating network i/o device %s with osa'
                ' port 4 using uri %s with osa port 1'
                % (interface_name, uri_update_device))
            resp = self.session.request_put_json(
                uri_update_device, body=input_json,
                expected_status_values=[400])
            if not resp:
                self.logging.info(
                    'update action with osa port 4 on network i/o device '
                    '%s returned None/Empty response' % interface_name)
                self.fail(
                    'update action with osa port 1 on network i/o device '
                    '%s returned None/Empty response' % interface_name)

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestNwdevices.test_S016_update_nwdevice_with_invalid_osaport()')

    @classmethod
    def tearDownClass(self):
        """
        clean up
        :return:
        """
        self.logging.info('--> TestNwdevices.tearDownClass()')
        self.logging.debug('unconfigure network device')
        if self.configured_device:
            # strip enccw since  enccw is appended in setUpClass
            utils.unconfigure_nwdevice(self.session, self.configured_device.lstrip('enccw'))
        if self.unconfigured_device:
            utils.unconfigure_nwdevice(self.session, self.unconfigured_device)
        if self.unconfigured_osa_device:
            utils.unconfigure_nwdevice(self.session, self.unconfigured_osa_device)
        self.logging.info('<-- TestNwdevices.tearDownClass()')
