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

short_description = _(
    'Semantic web platform for knowledge management and collaboration')

description = [
    _('DMX – The Context Machine is a tool for authoring, structuring and exploring networked information. Based on a powerful associative database you can create Topicmaps and populate them with Topics. Topics represent individual items which can be related through Associations.'),
    _('DMX is a web application. It comes with a built-in Jetty web server and a default web client that brings the application to your browser. To explore and visualize your data you can use the web client.')
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

        daemon = Daemon('daemon-dmx', managed_services[0],
                        listen_ports=[(8080, 'tcp4'), (8081, 'tcp4'), (8443, 'tcp4')])
        # org.osgi.service.http.port,   TCP, IPv4, 8080 (8080)
        # dmx.websockets.port,          TCP, IPv4, 8081 (8081)
        # org.osgi.service.http.port.secure, IPv4, 8443 (8443)
        self.add(daemon)

        webserver = Webserver('webserver-dmx', 'dmx-freedombox',
                              urls=['http://{host}:8080/systems.dmx.webclient/'])
        self.add(webserver)

        firewall = Firewall('firewall-dmx', name,
                            ports=['http', 'https'], is_external=True)
        self.add(firewall)


def enable(self):
    """Enable the app by simply storing a flag in key/value store."""
    from plinth import kvstore
    super().enable()
    kvstore.set('dmx-enabled', True)
    utils.enable_connections(True)


def disable(self):
    """Disable the app by simply storing a flag in key/value store."""
    from plinth import kvstore
    super().disable()
    kvstore.set('dmx-enabled', False)
    utils.enable_connections(False)


def is_enabled(self):
    """Return whether all leader components are enabled and flag is set."""
    from plinth import kvstore
    enabled = super().is_enabled()
    return enabled and kvstore.get_default('dmx-enabled', False)


def init():
    """Initialize the module."""
    global app
    app = DmxApp()

    setup_helper = globals()['setup_helper']
    if setup_helper.get_state() != 'needs-setup' and app.is_enabled():
        app.set_enabled(True)


def setup(helper, old_version=None):
    """Install and configure the module."""
    helper.install(managed_packages)
# //FIXME Part 5: Customizing > Writing actions for:
#
# # Add the file /etc/apt/sources.list.d/dmx-repo.list
# ~$ sudo bash -c 'echo "deb https://download.dmx.systems/repos/ubuntu/ xenial/" >/etc/apt/sources.list.d/dmx-repo.list'
#
# # Add the key:
# ~$ curl -fsSL https://download.dmx.systems/repos/gpg | sudo apt-key add -
