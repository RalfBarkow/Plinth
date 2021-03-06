# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Functional, browser based tests for backups app.
"""

import os
import tempfile
import urllib.parse

import requests
from pytest import fixture
from pytest_bdd import parsers, scenarios, then, when

from plinth.tests import functional

scenarios('backups.feature')


@fixture(scope='session')
def downloaded_file_info():
    return dict()


@when(parsers.parse('I open the main page'))
def open_main_page(session_browser):
    _open_main_page(session_browser)


@then(parsers.parse('the main page should be shown'))
def main_page_is_shown(session_browser):
    assert (session_browser.url.endswith('/plinth/'))


@when(
    parsers.parse('I download the app data backup with name {archive_name:w}'))
def backup_download(session_browser, downloaded_file_info, archive_name):
    file_path = _download(session_browser, archive_name)
    downloaded_file_info['path'] = file_path


@when(parsers.parse('I restore the downloaded app data backup'))
def backup_restore_from_upload(session_browser, app_name,
                               downloaded_file_info):
    path = downloaded_file_info["path"]
    try:
        _upload_and_restore(session_browser, app_name, path)
    except Exception as err:
        raise err
    finally:
        os.remove(path)


def _open_main_page(browser):
    with functional.wait_for_page_update(browser):
        browser.find_link_by_href('/plinth/').first.click()


def _download_file_logged_in(browser, url, suffix=''):
    """Download a file from Plinth, pretend being logged in via cookies"""
    if not url.startswith("http"):
        current_url = urllib.parse.urlparse(browser.url)
        url = "%s://%s%s" % (current_url.scheme, current_url.netloc, url)
    cookies = browser.driver.get_cookies()
    cookies = {cookie["name"]: cookie["value"] for cookie in cookies}
    response = requests.get(url, verify=False, cookies=cookies)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        for chunk in response.iter_content(chunk_size=128):
            temp_file.write(chunk)
    return temp_file.name


def _download(browser, archive_name=None):
    functional.nav_to_module(browser, 'backups')
    href = f'/plinth/sys/backups/root/download/{archive_name}/'
    url = functional.base_url + href
    file_path = _download_file_logged_in(browser, url, suffix='.tar.gz')
    return file_path


def _upload_and_restore(browser, app_name, downloaded_file_path):
    functional.nav_to_module(browser, 'backups')
    browser.find_link_by_href('/plinth/sys/backups/upload/').first.click()
    fileinput = browser.driver.find_element_by_id('id_backups-file')
    fileinput.send_keys(downloaded_file_path)
    # submit upload form
    functional.submit(browser)
    # submit restore form
    with functional.wait_for_page_update(browser,
                                         expected_url='/plinth/sys/backups/'):
        functional.submit(browser)
