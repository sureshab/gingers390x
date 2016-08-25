from tests.fvt.fvt_base import TestBase
import utils
import time


class TestFCLuns(TestBase):
    default_schema = {"type": "object",
                      "properties": {"status": {"type": "string"},
                                     "product": {"type": "string"},
                                     "vendor": {"type": "string"},
                                     "configured": {"type": "string"},
                                     "hbaId": {"type": "string"},
                                     "remoteWwpn": {"type": "string"},
                                     "controllerSN": {"type": "string"},
                                     "lunId": {"type": "string"},
                                     "type": {"type": "string"}
                                     }
                      }
    uri_fcluns = '/plugins/gingers390x/fcluns'


    @classmethod
    def setUpClass(self):
        super(TestFCLuns, self).setUpClass()
        self.logging.info('--> TestFCLuns.setUpClass()')
        self.logging.debug('enable the fcp adapter '
                           'specified in config file')
        self.hba_id = utils.readconfig(self, 'config', 'FCLUNs', 'hba_id')
        try:
            utils.bring_zfcp_online(self.session, self.hba_id)
        except Exception, err:
            self.logging.error(str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- TestFCLun.setUpClass()')

    def test_f001_add_lun_with_hbaId_missing(self):
        """
        Add lun without specifying the hba ID. Fails with 400
        """
        try:
            self.logging.info('--> TestFCLuns.test_add_lun_with_hbaId_missing()')
            lun_data = {"remoteWwpn" : "0x500507680b244ac1", "lunId" : "0xc101000000000000"}
            self.session.request_post(uri=self.uri_fcluns,body=lun_data,expected_status_values=[400])
        except Exception, err:
            self.logging.error(str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- TestFCLuns.test_add_lun_with_hbaId_missing()')

    def test_f002_add_lun_with_remotewwpn_missing(self):
        """
        Add lun without specifying the remote WWPN. Fails with 400
        """
        try:
            self.logging.info('--> TestFCLuns.test_add_lun_with_remotewwpn_missing()')
            lun_data = {"hbaId" : "0.0.3080", "lunId" : "0xc101000000000000"}
            self.session.request_post(uri=self.uri_fcluns,body=lun_data,expected_status_values=[400])
        except Exception, err:
            self.logging.error(str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- TestFCLuns.test_add_lun_with_remotewwpn_missing()')

    def test_f003_add_lun_with_lunID_missing(self):
        """
        Add lun without specifying the lun ID. Fails with 400
        """
        try:
            self.logging.info('--> TestFCLuns.test_add_lun_with_lunID_missing()')
            lun_data = {"hbaId" : "0.0.3080", "remoteWwpn" : "0x500507680b244ac1"}
            self.session.request_post(uri=self.uri_fcluns,body=lun_data,expected_status_values=[400])
        except Exception, err:
            self.logging.error(str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- TestFCLuns.test_add_lun_with_lunID_missing()')

    def test_s001_add_lun(self):
        """
        Add lun by passing the hbaID, remoteWWPN and lunID specified in the config file
        """
        try:
            self.logging.info('--> TestFCLuns.test_add_lun()')
            hba_id = utils.readconfig(self, 'config', 'FCLUNs', 'hba_id')
            remote_wwpn = utils.readconfig(self, 'config', 'FCLUNs', 'remote_wwpn')
            lun_id = utils.readconfig(self, 'config', 'FCLUNs', 'lun_id')
            lun_data = {"hbaId" : hba_id, "remoteWwpn" : remote_wwpn, "lunId" : lun_id}
            self.session.request_post(uri=self.uri_fcluns,body=lun_data,expected_status_values=[201])
        except Exception, err:
            self.logging.error(str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- TestFCLuns.test_add_lun')

    def test_s002_get_list_of_luns(self):
        try:
            self.logging.info('--> TestFCLuns.test_get_luns()')
            resp_luns = self.session.request_get_json(self.uri_fcluns,[200])
            for lun in resp_luns:
                self.validator.validate_json(lun, self.default_schema)
        except Exception, err:
            self.logging.error(str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- TestFCLuns.test_get_luns()')

    def test_S003_get_single_lun(self):
        try:
            self.logging.info('--> TestFCLuns.test_get_single_lun()')
            hba_id = utils.readconfig(self, 'config', 'FCLUNs', 'hba_id')
            remote_wwpn = utils.readconfig(self, 'config', 'FCLUNs', 'remote_wwpn')
            lun_id = utils.readconfig(self, 'config', 'FCLUNs', 'lun_id')
            lun = hba_id + ':' + remote_wwpn + ':' + lun_id
            resp_lun = self.session.request_get_json(self.uri_fcluns + '/' + lun,[200])
            self.validator.validate_json(resp_lun, self.default_schema)
        except Exception, err:
            self.logging.error(str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- TestFCLuns.test_get_single_lun()')

    def test_S004_delete_lun(self):
        """
        Delete the lun specified in the config file
        :return:
        """
        try:
            self.logging.info('--> TestFCLuns.test_delete_lun()')
            hba_id = utils.readconfig(self, 'config', 'FCLUNs', 'hba_id')
            remote_wwpn = utils.readconfig(self, 'config', 'FCLUNs', 'remote_wwpn')
            lun_id = utils.readconfig(self, 'config', 'FCLUNs', 'lun_id')
            lun = hba_id + ':' + remote_wwpn + ':' + lun_id
            self.session.request_delete(uri=self.uri_fcluns + '/' + lun, expected_status_values=[204])
        except Exception, err:
            self.logging.error(str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- TestFCLuns.test_delete_pv()')

    @classmethod
    def tearDownClass(self):
        """
        clean up
        :return:
        """
        self.logging.info('--> TestFCLuns.tearDownClass()')
        self.logging.debug('disable the hba added in setup class')
        utils.bring_zfcp_offline(self.session, self.hba_id)
        self.logging.info('<-- TestFCLuns.tearDownClass()')
