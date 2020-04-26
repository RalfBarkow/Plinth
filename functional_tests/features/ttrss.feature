# SPDX-License-Identifier: AGPL-3.0-or-later

@apps @ttrss @sso @backups
Feature: TT-RSS News Feed Reader
  Run TT-RSS News Feed Reader.

Background:
  Given I'm a logged in user
  Given the ttrss application is installed

Scenario: Enable ttrss application
  Given the ttrss application is disabled
  When I enable the ttrss application
  Then the ttrss service should be running

Scenario: Backup and restore ttrss
  Given the ttrss application is enabled
  And I subscribe to a feed in ttrss
  When I create a backup of the ttrss app data
  And I unsubscribe from the feed in ttrss
  And I restore the ttrss app data backup
  Then the ttrss service should be running
  And I should be subscribed to the feed in ttrss

Scenario: Disable ttrss application
  Given the ttrss application is enabled
  When I disable the ttrss application
  Then the ttrss service should not be running
