from tests.fvt.fvt_base import TestBase
import utils
import time


class TestLunScan(TestBase):
    default_schema = {"type": "object",
                      "properties": {"current": {"type": "boolean"},
                                     "boot": {"type": "boolean"},
                                     }
                      }
    default_task_schema = {"type" : "object",
                          "properties": {"status": {"type": "string"},
                                         "message": {"type": "string"},
                                         "id": {"type": "string"},
                                         "target_uri": {"type": "string"},
                                         }
                          }
    uri_lunscan = '/plugins/gingers390x/lunscan'

    def test_S001_get_lunscan_status(self):
        try:
            self.logging.info('--> TestLunScan.test_get_lunscan_status()')
            resp_lun = self.session.request_get_json(self.uri_lunscan ,[200])
            self.validator.validate_json(resp_lun, self.default_schema)
        except Exception, err:
            self.logging.error(str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- TestLunScan.test_get_lunscan_status()')

    def test_S002_enable_lunscan(self):
        try:
            self.logging.info('--> TestLunScan.test_enable_lunscan()')
            resp_lun = self.session.request_post_json(self.uri_lunscan + '/enable' ,[200])
            get_status = self.session.request_get_json(self.uri_lunscan ,[200])
            self.assertEquals(resp_lun, get_status)
        except Exception, err:
            self.logging.error(str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- TestLunScan.test_enable_lunscan()')

    def test_S003_disable_lunscan(self):
        try:
            self.logging.info('--> TestLunScan.test_disable_lunscan()')
            resp_lun = self.session.request_post_json(self.uri_lunscan + '/disable' ,[200])
            get_status = self.session.request_get_json(self.uri_lunscan ,[200])
            self.assertEquals(resp_lun, get_status)
        except Exception, err:
            self.logging.error(str(err))
            raise Exception(str(err))
        finally:
            self.logging.info('<-- TestLunScan.test_disable_lunscan()')


