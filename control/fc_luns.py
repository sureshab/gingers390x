#
# Project Ginger S390x
#
# Copyright IBM Corp, 2015-2016
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

from wok.control.base import Collection, Resource
from wok.control.utils import model_fn, UrlSubNode

LUNSCAN_REQUESTS = {
    'POST': {
        'enable': "GS390XSTG0001L",
        'disable': "GS390XSTG0002L",
        'trigger': "GS390XSTG0003L",
    }
}

FCLUNS_REQUESTS = {
    'POST': {
        'default': "GS390XSTG0004L"},
}

FCLUN_REQUESTS = {
    'DELETE': {'default': "GS390XSTG0005L"}
}


@UrlSubNode("lunscan")
class LUNScan(Resource):
    """
    Resource representing the status of LUN scanning
    """

    def __init__(self, model):
        super(LUNScan, self).__init__(model)
        self.admin_methods = ['GET', 'POST']
        self.role_key = "administration"
        self.uri_fmt = "/lunscan/%s"
        self.enable = self.generate_action_handler_task('enable')
        self.disable = self.generate_action_handler_task('disable')
        self.trigger = self.generate_action_handler_task('trigger')
        self.log_map = LUNSCAN_REQUESTS

    @property
    def data(self):
        return self.info


@UrlSubNode("fcluns")
class FCLUNs(Collection):
    """
    Collections representing the FC LUNs on the system
    """

    def __init__(self, model):
        super(FCLUNs, self).__init__(model)
        self.role_key = 'host'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = FCLUN
        self.log_map = FCLUNS_REQUESTS
        self.log_args.update({'hbaId': '', 'remoteWwpn': '', 'lunId': ''})

    def _get_resources(self, flag_filter):
        """
        Overriden this method, here get_list should return list dict
        which will be set to the resource, this way we avoid calling lookup
        again for each device.
        :param flag_filter:
        :return: list of resources.
        """
        try:
            get_list = getattr(self.model, model_fn(self, 'get_list'))
            idents = get_list(*self.model_args, **flag_filter)
            res_list = []
            for ident in idents:
                # internal text, get_list changes ident to unicode for sorted
                args = self.resource_args + [ident]
                res = self.resource(self.model, *args)
                res.info = ident
                res_list.append(res)
            return res_list
        except AttributeError:
            return []


class FCLUN(Resource):
    """
    Resource representing a single LUN
    """

    def __init__(self, model, ident):
        super(FCLUN, self).__init__(model, ident)
        self.role_key = 'host'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/fcluns/%s"
        self.log_map = FCLUN_REQUESTS

    @property
    def data(self):
        return self.info
