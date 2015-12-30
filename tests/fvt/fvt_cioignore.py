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

import ast
import unittest

import utils
from tests.fvt.fvt_base import TestBase
from tests.fvt.restapilib import APIRequestError


CONFIGFILE = 'config'
CIO_IGNORE_SECTION = 'CIO_IGNORE'
DEVICES_OPT = 'devices'


class TestCioIgnoreList(TestBase):
    """
    Represents test case that could help in testing the REST API
    supported for cio_ignore list

    Attributes:
        \param TestBase
         config file which contains all configuration
            information with sections
    """
    # Response json of cio_ignore looks like
    # {"ignored_devices":
    # ["0.0.0016-0.0.001f","0.0.0021-0.0.ffff","0.1.0000-0.1.ffff"]}
    cioignore_schema = {"type": "object",
                        "properties": {"ignored_devices": {"type": "array"}
                                       }
                        }
    # POST action remove api returns a task resource
    task_schema = {"type": "object",
                   "properties": {"status": {"type": "string"},
                                  "message": {"type": "string"},
                                  "id": {"type": "string"},
                                  "target_uri": {"type": "string"},
                                  }
                   }
    uri_cio_ignore = '/plugins/gingers390x/cio_ignore'
    uri_task = '/plugins/gingers390x/tasks'
    remove_devices = None

    @classmethod
    def setUpClass(self):
        super(TestCioIgnoreList, self).setUpClass()
        self.logging.info('--> TestCioIgnoreList.setUpClass()')
        self.logging.debug('Reading removable devices(from ignore list)'
                           ' information from config file')
        self.remove_devices = utils.readconfig(
            self.session, CONFIGFILE, CIO_IGNORE_SECTION, DEVICES_OPT)
        self.logging.debug(
            'Reading removable devices(from ignore list) information from'
            ' config file. Devices: %s' % self.remove_devices)
        self.logging.info('<-- TestCioIgnoreList.setUpClass()')

    def test_S001_cio_ignore_list(self):
        """
        Retrieve Ignore list information
        """
        self.logging.info('--> TestCioIgnoreList.test_S001_cio_ignore_list()')
        try:
            self.logging.debug('Retrieving cio_ignore list information')
            resp = self.session.request_get_json(
                self.uri_cio_ignore, expected_status_values=[200])
            if resp:
                self.logging.debug('cio_ignore list retrived : %s' % resp)
                self.validator.validate_json(resp, self.cioignore_schema)
            else:
                self.logging.info('Failed to retrieve ignore list.'
                                  ' Response is None/Empty')
                self.fail(
                    'Failed to retrieve ignore list. Response is None/Empty')

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestCioIgnoreList.test_S001_cio_ignore_list()')

    def test_S002_remove_valid_devices(self):
        """
        method to test remove action in cio_ignore api call with valid devices
        """
        self.logging.info(
            '--> TestCioIgnoreList.test_S002_remove_valid_devices()')

        uri_cio_ignore_remove = self.uri_cio_ignore + '/remove'
        self.logging.debug('Reading devices information from config file')
        if not self.remove_devices:
            raise unittest.SkipTest(
                'Skipping test_S002_remove_valid_devices() since '
                'removable devices are not provided in config file')
        devices = ast.literal_eval(self.remove_devices)
        input_json = {"devices": devices}
        try:
            self.logging.debug(
                'Performing post operation remove on cio_ignore '
                'list with inpust json %s' % input_json)
            resp = self.session.request_post_json(
                uri_cio_ignore_remove, body=input_json,
                expected_status_values=[200, 202])
            if resp:
                self.logging.debug('task json returned from cio_ignore remove'
                                   ': %s' % resp)
                self.validator.validate_json(resp, self.task_schema)
                self.logging.info('Waiting for task completion')
                task_id = resp['id']
                task_resp = utils.wait_task_status_change(
                    self.session, task_id, task_final_status='finished')
                self.validator.validate_json(task_resp, self.task_schema)
                assert (task_resp['status'] == 'finished'),\
                    "remove task failed. task json response:" \
                    " %s" % task_resp
                self.logging.debug('Successfully removed devices %s from '
                                   'ignore list. Task response: %s'
                                   % (devices, task_resp))
            else:
                self.logging.info('Remove action on /cio_ignore returned'
                                  ' None/Empty response instead of task json')
                self.fail('Remove action on /cio_ignore returned '
                          'None/Empty response instead of task json')

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestCioIgnoreList.test_S002_remove_valid_devices()')

    def test_S003_remove_invalid_devices(self):
        """
        method to test remove action in cio_ignore api call with invalid
        devices (includes list of invalid id for single device, invalid
        range and empty device id)
        """
        self.logging.info(
            '--> TestCioIgnoreList.test_S003_remove_invalid_devices()')

        uri_cio_ignore_remove = self.uri_cio_ignore + '/remove'
        devices = ['invalid_device', '0.1.0900-0.0.0001', '  ']
        # devices list composes of invalid device id, invalid range and
        # empty device id

        input_json = {"devices": devices}
        try:
            self.logging.debug(
                'Performing post operation remove on cio_ignore '
                'list with input json %s' % input_json)
            resp = self.session.request_post_json(
                uri_cio_ignore_remove, body=input_json,
                expected_status_values=[200, 202])
            if resp:
                self.logging.debug('task json returned from cio_ignore remove'
                                   ': %s' % resp)
                self.validator.validate_json(resp, self.task_schema)
                task_id = resp['id']
                task_resp = utils.wait_task_status_change(
                    self.session, task_id, task_final_status='failed')
                self.validator.validate_json(task_resp, self.task_schema)
                assert (task_resp['status'] == 'failed'),\
                    "remove task which was expected to fail, finished" \
                    " successfully. task json response: %s" % task_resp
                self.logging.debug(
                    'As expected, failed to remove invalid devices. '
                    'Task response %s' % task_resp)
            else:
                self.logging.info('Remove action on /cio_ignore returned'
                                  ' None/Empty response instead of task json')
                self.fail('Remove action on /cio_ignore returned '
                          'None/Empty response instead of task json')

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestCioIgnoreList.test_S003_remove_invalid_devices()')

    def test_S004_remove_valid_and_invalid_devices(self):
        """
        method to test remove action in cio_ignore api call with combination
        of valid and invalid devices
        invalid devices includes list of invalid id for single device, invalid
        range and empty device id
        """
        self.logging.info(
            '--> TestCioIgnoreList.test_S004_remove_valid_'
            'and_invalid_devices()')

        uri_cio_ignore_remove = self.uri_cio_ignore + '/remove'
        if not self.remove_devices:
            raise unittest.SkipTest(
                'Skipping test_S004_remove_valid_and_invalid_devices() since'
                ' removable devices are not provided in config file')
        devices = ast.literal_eval(self.remove_devices)
        devices.extend(['invalid_device', '0.1.0900-0.0.0001', '  '])
        # appending invalid devices list which composes of invalid device id,
        #  invalid range and empty device id

        input_json = {"devices": devices}
        try:
            self.logging.debug(
                'Performing post operation remove on cio_ignore '
                'list with input json %s' % input_json)
            resp = self.session.request_post_json(
                uri_cio_ignore_remove, body=input_json,
                expected_status_values=[200, 202])
            if resp:
                self.logging.debug('task json returned from cio_ignore remove'
                                   ': %s' % resp)
                self.validator.validate_json(resp, self.task_schema)
                task_id = resp['id']
                task_resp = utils.wait_task_status_change(
                    self.session, task_id, task_final_status='failed')
                self.validator.validate_json(task_resp, self.task_schema)
                assert (task_resp['status'] == 'failed'),\
                    "remove task which was expected to fail, finished" \
                    " successfully. task json response: %s" % task_resp
                self.logging.debug(
                    'Result is as expected. Task response %s' % task_resp)
            else:
                self.logging.info('Remove action on /cio_ignore returned'
                                  ' None/Empty response instead of task json')
                self.fail('Remove action on /cio_ignore returned '
                          'None/Empty response instead of task json')

        except APIRequestError as error:
            self.logging.error(error.__str__())
            raise Exception(error)
        finally:
            self.logging.info(
                '<-- TestCioIgnoreList.test_S004_remove_valid_'
                'and_invalid_devices()')

    @classmethod
    def tearDownClass(self):
        """
        clean up
        :return:
        """
        pass
