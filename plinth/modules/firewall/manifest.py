# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Application manifest for firewall.
"""

from plinth.modules.backups.api import validate as validate_backup

backup = validate_backup({})
