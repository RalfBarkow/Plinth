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
FreedomBox app for configuring MediaWiki.
"""

import logging

from django.contrib import messages
from django.utils.translation import ugettext as _

from plinth import actions, views
from plinth.modules import mediawiki

from . import is_private_mode_enabled, is_public_registration_enabled
from .forms import MediaWikiForm

logger = logging.getLogger(__name__)


class MediaWikiAppView(views.AppView):
    """App configuration page."""
    clients = mediawiki.clients
    name = mediawiki.name
    description = mediawiki.description
    diagnostics_module_name = 'mediawiki'
    app_id = 'mediawiki'
    form_class = MediaWikiForm
    manual_page = mediawiki.manual_page
    show_status_block = False
    template_name = 'mediawiki.html'
    icon_filename = mediawiki.icon_filename

    def get_initial(self):
        """Return the values to fill in the form."""
        initial = super().get_initial()
        initial.update({
            'enable_public_registrations': is_public_registration_enabled(),
            'enable_private_mode': is_private_mode_enabled()
        })
        return initial

    def form_valid(self, form):
        """Apply the changes submitted in the form."""
        old_config = self.get_initial()
        new_config = form.cleaned_data

        def is_unchanged(key):
            return old_config[key] == new_config[key]

        app_same = is_unchanged('is_enabled')
        pub_reg_same = is_unchanged('enable_public_registrations')
        private_mode_same = is_unchanged('enable_private_mode')

        if new_config['password']:
            actions.superuser_run('mediawiki', ['change-password'],
                                  input=new_config['password'].encode())
            messages.success(self.request, _('Password updated'))

        if app_same and pub_reg_same and private_mode_same:
            if not self.request._messages._queued_messages:
                messages.info(self.request, _('Setting unchanged'))
        elif not app_same:
            if new_config['is_enabled']:
                self.app.enable()
            else:
                self.app.disable()

        if not pub_reg_same:
            # note action public-registration restarts, if running now
            if new_config['enable_public_registrations']:
                if not new_config['enable_private_mode']:
                    actions.superuser_run('mediawiki',
                                          ['public-registrations', 'enable'])
                    messages.success(self.request,
                                     _('Public registrations enabled'))
                else:
                    messages.warning(
                        self.request, 'Public registrations ' +
                        'cannot be enabled when private mode is enabled')
            else:
                actions.superuser_run('mediawiki',
                                      ['public-registrations', 'disable'])
                messages.success(self.request,
                                 _('Public registrations disabled'))

        if not private_mode_same:
            if new_config['enable_private_mode']:
                actions.superuser_run('mediawiki', ['private-mode', 'enable'])
                if new_config['enable_public_registrations']:
                    # If public registrations are enabled, then disable it
                    actions.superuser_run('mediawiki',
                                          ['public-registrations', 'disable'])
                messages.success(self.request, _('Private mode enabled'))
            else:
                actions.superuser_run('mediawiki', ['private-mode', 'disable'])
                messages.success(self.request, _('Private mode disabled'))

            shortcut = mediawiki.app.get_component('shortcut-mediawiki')
            shortcut.login_required = new_config['enable_private_mode']

        return super().form_valid(form)
