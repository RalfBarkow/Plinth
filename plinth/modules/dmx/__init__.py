#
# This file is part of FreedomBox.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
FreedomBox app to configure DMX - The Context Machine.
"""

import pathlib

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from plinth.menu import main_menu

from plinth import actions
from plinth import app as app_module
from plinth import cfg, frontpage, menu
from plinth.daemon import Daemon
# from plinth.modules import names # FreedomBox app to configure name services.
from plinth.modules.firewall.components import Firewall
from plinth.modules.apache.components import Webserver

# from plinth.modules.users import add_user_to_share_group, register_group

from .manifest import clients  # noqa, pylint: disable=unused-import

version = 1

managed_services = ['dmx']

managed_packages = ['dmx']

managed_paths = [pathlib.Path('/var/lib/dmx/')]

name = _('DMX')

short_description = _('Platform for knowledge management and collaboration')

description = [
    _('DMX is a platform for knowledge management and collaboration.'),
    _('DMX is a web application. It comes with a built-in Jetty web server and a default web client that brings the application to your browser.')
]

clients = clients

# reserved_usernames = ['debian-transmission']

# group = ('bit-torrent', _('Download files using BitTorrent applications'))

# manual_page = 'Transmission'

app = None


class DmxApp(app_module.App):
    """FreedomBox app for DMX - The Context Machine."""

    app_id = 'dmx'

    def __init__(self):
        """Create components for the app."""
        super().__init__()
        menu_item = menu.Menu('menu-dmx', name, short_description,
                              'dmx', 'dmx:index',
                              parent_url_name='apps')
        self.add(menu_item)

        shortcut = frontpage.Shortcut(
            'shortcut-dmx', name, short_description=short_description,
            icon='glyphicon-refresh', description=description,
            configure_url=reverse_lazy('dmx:index'), login_required=True,
            clients=clients)
        self.add(shortcut)

        firewall = Firewall('firewall-dmx', name,
                            ports=['dmx-freedombox'], is_external=True)
        self.add(firewall)

        webserver = Webserver('webserver-dmx', 'dmx-freedombox')
        self.add(webserver)

        daemon = Daemon('daemon-dmx', managed_services[0],
                        listen_ports=[(8080, 'tcp4')])
        self.add(daemon)


def init():
    """Initialize the DMX module."""
    global app
    app = DmxApp()
    # register_group(group)

    setup_helper = globals()['setup_helper']
    if setup_helper.get_state() != 'needs-setup' and app.is_enabled():
        app.set_enabled(True)


def setup(helper, old_version=None):
    """Install and configure the module."""
    helper.install(managed_packages)

    # new_configuration = {
    #    'rpc-whitelist-enabled': False,
    #    'rpc-authentication-required': False
    # }
    helper.call('post', actions.superuser_run, 'dmx', ['enable'])
    #            ['merge-configuration'],
    #            input=json.dumps(new_configuration).encode())
    # add_user_to_share_group(reserved_usernames[0], managed_services[0])
    helper.call('post', app.enable)


def diagnose():
    """Run diagnostics and return the results."""
    results = []

    results.extend(
        action_utils.diagnose_url_on_all('https://{host}/dmx',
                                         check_certificate=False))

    return results
