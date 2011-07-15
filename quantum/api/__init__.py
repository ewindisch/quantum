# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011 Citrix Systems
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
# @author: Salvatore Orlando, Citrix Systems

"""
Quantum API controllers.
"""

import logging
import routes
import webob.dec
import webob.exc

from quantum import manager
from quantum.api import faults
from quantum.api import networks
from quantum.api import ports
from quantum.common import flags
from quantum.common import wsgi


LOG = logging.getLogger('quantum.api')
FLAGS = flags.FLAGS


class APIRouterV01(wsgi.Router):
    """
    Routes requests on the Quantum API to the appropriate controller
    """

    def __init__(self, ext_mgr=None):
        mapper = routes.Mapper()
        self._setup_routes(mapper)
        super(APIRouterV01, self).__init__(mapper)

    def _setup_routes(self, mapper):
        # Loads the quantum plugin
        plugin = manager.QuantumManager().get_plugin()
        uri_prefix = '/tenants/{tenant_id}/'
        mapper.resource('network', 'networks',
                        controller=networks.Controller(plugin),
                        path_prefix=uri_prefix)
        mapper.resource('port', 'ports',
                        controller=ports.Controller(plugin),
                        parent_resource=dict(member_name='network',
                                             collection_name=uri_prefix +\
                                                 'networks'))
        mapper.connect("get_resource",
                       uri_prefix + 'networks/{network_id}/' \
                                    'ports/{id}/attachment{.format}',
                       controller=ports.Controller(plugin),
                       action="get_resource",
                       conditions=dict(method=['GET']))
        mapper.connect("attach_resource",
                       uri_prefix + 'networks/{network_id}/' \
                                    'ports/{id}/attachment{.format}',
                       controller=ports.Controller(plugin),
                       action="attach_resource",
                       conditions=dict(method=['PUT']))
        mapper.connect("detach_resource",
                       uri_prefix + 'networks/{network_id}/' \
                                    'ports/{id}/attachment{.format}',
                       controller=ports.Controller(plugin),
                       action="detach_resource",
                       conditions=dict(method=['DELETE']))
