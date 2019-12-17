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
FreedomBox app for myApp.
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

managed_services = ['myApp']

managed_packages = ['myApp']

name = _('')

short_description = _('')

description = [
    _(''),
]

clients = clients

app = None


class myAppApp(app_module.App):
    """FreedomBox app for myApp."""

    app_id = 'myApp'

    def __init__(self):
        """Create components for the app."""
        super().__init__()
        menu_item = menu.Menu('menu-myApp', name, short_description,
                              'glyphicon-refresh', 'myApp:index',
                              parent_url_name='apps')
        self.add(menu_item)

        shortcut = frontpage.Shortcut(
            'shortcut-myApp', name, short_description=short_description,
            icon='glyphicon-refresh', url='/myApp', clients=clients,
            login_required=True)
        self.add(shortcut)

        firewall = Firewall('firewall-myApp', name, ports=['http', 'https'],
                            is_external=True)
        self.add(firewall)

        webserver = Webserver('webserver-myApp', 'myApp-freedombox')
        self.add(webserver)

        daemon = Daemon('daemon-myApp', managed_services[0])
        self.add(daemon)


def init():
    """Initialize the module."""
    global app
    app = myAppApp()

    setup_helper = globals()['setup_helper']
    if setup_helper.get_state() != 'needs-setup' and app.is_enabled():
        app.set_enabled(True)


def setup(helper, old_version=None):
    """Install and configure the module."""
    helper.install(managed_packages)
    helper.call('post', actions.superuser_run, 'myApp', ['enable'])
    helper.call('post', app.enable)


def diagnose():
    """Run diagnostics and return the results."""
    results = []

    results.extend(
        action_utils.diagnose_url_on_all('https://{host}/myApp',
                                         check_certificate=False))

    return results
