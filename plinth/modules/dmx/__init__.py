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
FreedomBox app for dmx.
"""

from django.utils.translation import ugettext_lazy as _

from plinth import action_utils, actions
from plinth import app as app_module
from plinth import frontpage, menu
from plinth.daemon import Daemon
from plinth.modules.apache.components import Webserver
from plinth.modules.firewall.components import Firewall

from .manifest import clients  # noqa, pylint: disable=unused-import


version = 1

managed_services = ['dmx']

managed_packages = ['dmx']

name = _('')

short_description = _('')

description = [
    _(''),
]

clients = clients

app = None


class dmxApp(app_module.App):
    """FreedomBox app for dmx."""

    app_id = 'dmx'

    def __init__(self):
        """Create components for the app."""
        super().__init__()
        menu_item = menu.Menu('menu-dmx', name, short_description,
                              'glyphicon-refresh', 'dmx:index',
                              parent_url_name='apps')
        self.add(menu_item)

        shortcut = frontpage.Shortcut(
            'shortcut-dmx', name, short_description=short_description,
            icon='glyphicon-refresh', url='/dmx', clients=clients,
            login_required=True)
        self.add(shortcut)

        firewall = Firewall('firewall-dmx', name, ports=['http', 'https'],
                            is_external=True)
        self.add(firewall)

        webserver = Webserver('webserver-dmx', 'dmx-freedombox')
        self.add(webserver)

        daemon = Daemon('daemon-dmx', managed_services[0])
        self.add(daemon)


def init():
    """Initialize the module."""
    global app
    app = dmxApp()

    setup_helper = globals()['setup_helper']
    if setup_helper.get_state() != 'needs-setup' and app.is_enabled():
        app.set_enabled(True)


def setup(helper, old_version=None):
    """Install and configure the module."""
    helper.install(managed_packages)
    helper.call('post', actions.superuser_run, 'dmx', ['enable'])
    helper.call('post', app.enable)


def diagnose():
    """Run diagnostics and return the results."""
    results = []

    results.extend(
        action_utils.diagnose_url_on_all('https://{host}/dmx',
                                         check_certificate=False))

    return results
