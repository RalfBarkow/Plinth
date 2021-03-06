# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Test module for custom context processors.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from django.http import HttpRequest

from plinth import cfg
from plinth import context_processors as cp
from plinth import menu as menu_module


@pytest.fixture(name='menu', autouse=True)
def fixture_menu():
    """Initialized menu module."""
    menu_module.init()


@patch('plinth.notification.Notification')
def test_common(Notification):
    """Verify that the common() function returns the correct values."""
    cfg.read()  # initialize config settings

    request = HttpRequest()
    request.path = '/aaa/bbb/ccc/'
    request.user = Mock()
    request.user.groups.filter().exists = Mock(return_value=True)
    request.session = MagicMock()
    response = cp.common(request)
    assert response is not None

    config = response['cfg']
    assert config is not None
    assert config.box_name == 'FreedomBox'

    assert response['box_name'] == 'FreedomBox'

    submenu = response['submenu']
    assert submenu is None

    urls = response['active_menu_urls']
    assert urls is not None
    assert ['/', '/aaa/', '/aaa/bbb/', '/aaa/bbb/ccc/'] == urls

    assert response['user_is_admin']


@patch('plinth.notification.Notification')
def test_common_border_conditions(Notification):
    """Verify that the common() function works for border conditions."""
    request = HttpRequest()
    request.path = ''
    request.user = Mock()
    request.user.groups.filter().exists = Mock(return_value=True)
    request.session = MagicMock()
    response = cp.common(request)
    assert response['active_menu_urls'] == []

    request.path = '/'
    response = cp.common(request)
    assert response['active_menu_urls'] == ['/']

    request.path = '/aaa/bbb'
    response = cp.common(request)
    assert response['active_menu_urls'] == ['/', '/aaa/']
