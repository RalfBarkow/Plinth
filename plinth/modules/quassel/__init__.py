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
FreedomBox app for Quassel.
"""

import pathlib

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from plinth import actions
from plinth import app as app_module
from plinth import cfg, frontpage, menu
from plinth.daemon import Daemon
from plinth.modules import names
from plinth.modules.firewall.components import Firewall
from plinth.modules.letsencrypt.components import LetsEncrypt
from plinth.utils import format_lazy

from .manifest import backup, clients  # noqa, pylint: disable=unused-import

version = 1

managed_services = ['quasselcore']

managed_packages = ['quassel-core']

managed_paths = [pathlib.Path('/var/lib/quassel/')]

name = _('Quassel')

icon_filename = 'quassel'

short_description = _('IRC Client')

description = [
    format_lazy(
        _('Quassel is an IRC application that is split into two parts, a '
          '"core" and a "client". This allows the core to remain connected '
          'to IRC servers, and to continue receiving messages, even when '
          'the client is disconnected. {box_name} can run the Quassel '
          'core service keeping you always online and one or more Quassel '
          'clients from a desktop or a mobile can be used to connect and '
          'disconnect from it.'), box_name=_(cfg.box_name)),
    _('You can connect to your Quassel core on the default Quassel port '
      '4242.  Clients to connect to Quassel from your '
      '<a href="http://quassel-irc.org/downloads">desktop</a> and '
      '<a href="http://quasseldroid.iskrembilen.com/">mobile</a> devices '
      'are available.'),
]

clients = clients

reserved_usernames = ['quasselcore']

manual_page = 'Quassel'

port_forwarding_info = [('TCP', 4242)]

app = None


class QuasselApp(app_module.App):
    """FreedomBox app for Quassel."""

    app_id = 'quassel'

    def __init__(self):
        """Create components for the app."""
        super().__init__()
        menu_item = menu.Menu('menu-quassel', name, short_description,
                              'quassel', 'quassel:index',
                              parent_url_name='apps')
        self.add(menu_item)

        shortcut = frontpage.Shortcut(
            'shortcut-quassel', name, short_description=short_description,
            icon=icon_filename, description=description,
            configure_url=reverse_lazy('quassel:index'), clients=clients,
            login_required=True)
        self.add(shortcut)

        firewall = Firewall('firewall-quassel', name, ports=['quassel-plinth'],
                            is_external=True)
        self.add(firewall)

        letsencrypt = LetsEncrypt(
            'letsencrypt-quassel', domains=get_domains,
            daemons=managed_services, should_copy_certificates=True,
            private_key_path='/var/lib/quassel/quasselCert.pem',
            certificate_path='/var/lib/quassel/quasselCert.pem',
            user_owner='quasselcore', group_owner='quassel',
            managing_app='quassel')
        self.add(letsencrypt)

        daemon = Daemon('daemon-quassel', managed_services[0],
                        listen_ports=[(4242, 'tcp4'), (4242, 'tcp6')])
        self.add(daemon)


def init():
    """Initialize the quassel module."""
    global app
    app = QuasselApp()

    setup_helper = globals()['setup_helper']
    if setup_helper.get_state() != 'needs-setup' and app.is_enabled():
        app.set_enabled(True)


def setup(helper, old_version=None):
    """Install and configure the module."""
    helper.install(managed_packages)
    helper.call('post', app.enable)
    app.get_component('letsencrypt-quassel').setup_certificates()


def get_available_domains():
    """Return an iterator with all domains able to have a certificate."""
    return (domain.name for domain in names.components.DomainName.list()
            if domain.domain_type.can_have_certificate)


def set_domain(domain):
    """Set the TLS domain by writing a file to data directory."""
    if domain:
        actions.superuser_run('quassel', ['set-domain', domain])


def get_domain():
    """Read TLS domain from config file select first available if none."""
    domain = None
    try:
        with open('/var/lib/quassel/domain-freedombox') as file_handle:
            domain = file_handle.read().strip()
    except FileNotFoundError:
        pass

    if not domain:
        domain = next(get_available_domains(), None)
        set_domain(domain)

    return domain


def get_domains():
    """Return a list with the configured domain for quassel."""
    domain = get_domain()
    if domain:
        return [domain]

    return []
