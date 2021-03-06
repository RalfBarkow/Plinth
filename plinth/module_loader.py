# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Discover, load and manage FreedomBox applications.
"""

import collections
import importlib
import logging
import pathlib
import re

import django

from plinth import cfg, setup
from plinth.signals import post_module_loading, pre_module_loading

logger = logging.getLogger(__name__)

loaded_modules = collections.OrderedDict()
_modules_to_load = None


def include_urls():
    """Include the URLs of the modules into main Django project."""
    for module_import_path in get_modules_to_load():
        module_name = module_import_path.split('.')[-1]
        _include_module_urls(module_import_path, module_name)


def load_modules():
    """
    Read names of enabled modules in modules/enabled directory and
    import them from modules directory.
    """
    pre_module_loading.send_robust(sender="module_loader")
    modules = {}
    for module_import_path in get_modules_to_load():
        module_name = module_import_path.split('.')[-1]
        try:
            modules[module_name] = importlib.import_module(module_import_path)
        except Exception as exception:
            logger.exception('Could not import %s: %s', module_import_path,
                             exception)
            if cfg.develop:
                raise

    ordered_modules = []
    remaining_modules = dict(modules)  # Make a copy
    for module_name in modules:
        if module_name not in remaining_modules:
            continue

        module = remaining_modules.pop(module_name)
        try:
            _insert_modules(module_name, module, remaining_modules,
                            ordered_modules)
        except KeyError:
            logger.error('Unsatified dependency for module - %s', module_name)

    logger.info('Module load order - %s', ordered_modules)

    for module_name in ordered_modules:
        _initialize_module(module_name, modules[module_name])
        loaded_modules[module_name] = modules[module_name]

    post_module_loading.send_robust(sender="module_loader")


def _insert_modules(module_name, module, remaining_modules, ordered_modules):
    """Insert modules into a list based on dependency order"""
    if module_name in ordered_modules:
        return

    dependencies = []
    try:
        dependencies = module.depends
    except AttributeError:
        pass

    for dependency in dependencies:
        if dependency in ordered_modules:
            continue

        try:
            module = remaining_modules.pop(dependency)
        except KeyError:
            logger.error('Not found or circular dependency - %s, %s',
                         module_name, dependency)
            raise

        _insert_modules(dependency, module, remaining_modules, ordered_modules)

    ordered_modules.append(module_name)


def _include_module_urls(module_import_path, module_name):
    """Include the module's URLs in global project URLs list"""
    from plinth import urls
    url_module = module_import_path + '.urls'
    try:
        urls.urlpatterns += [
            django.conf.urls.url(
                r'', django.conf.urls.include((url_module, module_name)))
        ]
    except ImportError:
        logger.debug('No URLs for %s', module_name)
        if cfg.develop:
            raise


def _initialize_module(module_name, module):
    """Call initialization method in the module if it exists"""
    # Perform setup related initialization on the module
    setup.init(module_name, module)

    try:
        init = module.init
    except AttributeError:
        logger.debug('No init() for module - %s', module.__name__)
        return

    try:
        init()
    except Exception as exception:
        logger.exception('Exception while running init for %s: %s', module,
                         exception)
        if cfg.develop:
            raise


def get_modules_to_load():
    """Get the list of modules to be loaded"""
    global _modules_to_load
    if _modules_to_load is not None:
        return _modules_to_load

    directory = pathlib.Path(cfg.config_dir) / 'modules-enabled'
    files = list(directory.glob('*'))
    if not files:
        # './setup.py install' has not been executed yet. Pickup files to load
        # from local module directories.
        directory = pathlib.Path(__file__).parent
        files = list(
            directory.glob('modules/*/data/etc/plinth/modules-enabled/*'))

    # Omit hidden files
    files = [
        file_ for file_ in files
        if not file_.name.startswith('.') and '.dpkg' not in file_.name
    ]

    modules = []
    for file_ in files:
        with file_.open() as file_handle:
            for line in file_handle:
                line = re.sub('#.*', '', line)
                line = line.strip()
                if line:
                    modules.append(line)

    _modules_to_load = modules
    return modules
