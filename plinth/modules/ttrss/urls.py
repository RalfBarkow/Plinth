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
URLs for the Tiny Tiny RSS module.
"""

from django.conf.urls import url

from plinth.modules import ttrss
from plinth.views import AppView

urlpatterns = [
    url(
        r'^apps/ttrss/$',
        AppView.as_view(app_id='ttrss', name=ttrss.name,
                        description=ttrss.description, clients=ttrss.clients,
                        icon_filename=ttrss.icon_filename,
                        manual_page=ttrss.manual_page, show_status_block=True),
        name='index'),
]
