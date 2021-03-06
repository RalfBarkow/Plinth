# SPDX-License-Identifier: AGPL-3.0-or-later
"""
FreedomBox app to configure Tahoe-LAFS.
"""

import json
import os

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from plinth import actions
from plinth import app as app_module
from plinth import cfg, frontpage, menu
from plinth.daemon import Daemon
from plinth.modules.apache.components import Webserver, diagnose_url
from plinth.modules.firewall.components import Firewall
from plinth.utils import format_lazy

from .errors import TahoeConfigurationError
from .manifest import backup  # noqa, pylint: disable=unused-import

version = 1

managed_services = ['tahoe-lafs']

managed_packages = ['tahoe-lafs']

_description = [
    _('Tahoe-LAFS is a decentralized secure file storage system. '
      'It uses provider independent security to store files over a '
      'distributed network of storage nodes. Even if some of the nodes fail, '
      'your files can be retrieved from the remaining nodes.'),
    format_lazy(
        _('This {box_name} hosts a storage node and an introducer by default. '
          'Additional introducers can be added, which will introduce this '
          'node to the other storage nodes.'), box_name=_(cfg.box_name)),
]

port_forwarding_info = [
    ('TCP', 3456),
    ('TCP', 5678),
]

tahoe_home = '/var/lib/tahoe-lafs'
introducer_name = 'introducer'
storage_node_name = 'storage_node'
domain_name_file = os.path.join(tahoe_home, 'domain_name')
introducers_file = os.path.join(
    tahoe_home, '{}/private/introducers.yaml'.format(storage_node_name))
introducer_furl_file = os.path.join(
    tahoe_home, '{0}/private/{0}.furl'.format(introducer_name))

app = None


class TahoeApp(app_module.App):
    """FreedomBox app for Tahoe LAFS."""

    app_id = 'tahoe'

    def __init__(self):
        """Create components for the app."""
        super().__init__()
        info = app_module.Info(app_id=self.app_id, version=version,
                               name=_('Tahoe-LAFS'),
                               icon_filename='tahoe-lafs',
                               short_description=_('Distributed File Storage'),
                               description=_description)

        self.add(info)

        menu_item = menu.Menu('menu-tahoe', info.name, info.short_description,
                              info.icon_filename, 'tahoe:index',
                              parent_url_name='apps', advanced=True)
        self.add(menu_item)

        shortcut = frontpage.Shortcut(
            'shortcut-tahoe', info.name,
            short_description=info.short_description, icon=info.icon_filename,
            description=info.description, url=None,
            configure_url=reverse_lazy('tahoe:index'), login_required=True)
        self.add(shortcut)

        firewall = Firewall('firewall-tahoe', info.name,
                            ports=['tahoe-plinth'], is_external=True)
        self.add(firewall)

        webserver = Webserver('webserver-tahoe', 'tahoe-plinth')
        self.add(webserver)

        daemon = Daemon('daemon-tahoe', managed_services[0])
        self.add(daemon)

    def diagnose(self):
        """Run diagnostics and return the results."""
        results = super().diagnose()
        results.extend([
            diagnose_url('http://localhost:5678', kind='4',
                         check_certificate=False),
            diagnose_url('http://localhost:5678', kind='6',
                         check_certificate=False),
            diagnose_url('http://{}:5678'.format(get_configured_domain_name()),
                         kind='4', check_certificate=False)
        ])
        return results


class Shortcut(frontpage.Shortcut):
    """Frontpage shortcut to use configured domain name for URL."""
    def enable(self):
        """Set the proper shortcut URL when enabled."""
        super().enable()
        self.url = 'https://{}:5678'.format(get_configured_domain_name())


def is_setup():
    """Check whether Tahoe-LAFS is setup"""
    return os.path.exists(domain_name_file)


def get_configured_domain_name():
    """Extract and return the domain name from the domain name file.
    Throws TahoeConfigurationError if the domain name file is not found.
    """
    if not os.path.exists(domain_name_file):
        raise TahoeConfigurationError
    else:
        with open(domain_name_file) as dnf:
            return dnf.read().rstrip()


def init():
    """Initialize the module."""
    global app
    app = TahoeApp()

    setup_helper = globals()['setup_helper']
    if setup_helper.get_state() != 'needs-setup' and is_setup() \
       and app.is_enabled():
        app.set_enabled(True)


def setup(helper, old_version=None):
    """Install and configure the module."""
    helper.install(managed_packages)


def post_setup(configured_domain_name):
    """Actions to be performed after installing tahoe-lafs package."""
    actions.superuser_run('tahoe-lafs',
                          ['setup', '--domain-name', configured_domain_name])
    actions.run_as_user('tahoe-lafs', ['create-introducer'],
                        become_user='tahoe-lafs')
    actions.run_as_user('tahoe-lafs', ['create-storage-node'],
                        become_user='tahoe-lafs')
    actions.superuser_run('tahoe-lafs', ['autostart'])
    app.enable()


def add_introducer(introducer):
    """Add an introducer to the storage node's list of introducers.
    Param introducer must be a tuple of (pet_name, furl)
    """
    actions.run_as_user(
        'tahoe-lafs', ['add-introducer', "--introducer", ",".join(introducer)],
        become_user='tahoe-lafs')


def remove_introducer(pet_name):
    """Rename the introducer entry in the introducers.yaml file specified by
    the param pet_name.
    """
    actions.run_as_user('tahoe-lafs',
                        ['remove-introducer', '--pet-name', pet_name],
                        become_user='tahoe-lafs')


def get_introducers():
    """Return a dictionary of all introducers and their furls added to the
    storage node running on this FreedomBox.
    """
    introducers = actions.run_as_user('tahoe-lafs', ['get-introducers'],
                                      become_user='tahoe-lafs')

    return json.loads(introducers)


def get_local_introducer():
    """Return the name and furl of the introducer created on this FreedomBox.
    """
    introducer = actions.run_as_user('tahoe-lafs', ['get-local-introducer'],
                                     become_user='tahoe-lafs')

    return json.loads(introducer)
