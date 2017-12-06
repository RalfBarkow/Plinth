# Hacking

## Setting Up Development Environment Using Vagrant

Vagrant is a free software command line utility for managing the life
cycle of virtual machines.  The FreedomBox project provides ready-made
virtual machines (VMs) for use with Vagrant.  These images make setting up
an environment for Plinth development rather simple:  You can edit the Plinth
source code on your host and immediately see the effects in the running VM.
The entire setup is automatic and requires about 4.5 GB of disk space.

1. Install Vagrant and VirtualBox:

   $ sudo apt-get install virtualbox vagrant

2. To download, setup, run, and configure a VM for Plinth development
   using Vagrant, simply execute in your Plinth development folder:

   $ vagrant up

3. To access Plinth (from host), visit https://localhost:4430/plinth/

4. Edit the source code in your host machine's Plinth development folder.
   By default, this folder is shared within the VM, at /vagrant/.
   To actually reflect the changes in the running VM, run on your host:

   $ vagrant provision

## Installing Dependencies

Apart from dependencies listing in INSTALL file, Plinth may have additional
dependencies required by modules of Plinth.  To install these, run:

    $ sudo apt install -y $(plinth --list-dependencies)

## Manually Setting Up for Development

It is recommended that you use Vagrant to setup your development
environment.  However, for some reason, you wish setup manually, the
following tips will help:

1. Instead of running "setup.py install" after every source modification, run
   the following command:

    $ sudo python3 setup.py develop

    This will install the python package in a special development mode.  Run it
    normally.  Any updates to the code (and core package data files) do not
    require re-installation after every modification.

    CherryPy web server also monitors changes to the source files and reloads
    the server as soon as a file is modified.  Hence it is usually sufficient
    to modify the source and refresh the browser page to see the changes.

2. Plinth also support running without installing (as much as possible).
   Simply run it as:

    $ sudo ./run --debug

    In this mode, Plinth runs in working directory without need for
    installation.  It uses the plinth.conf config file in the working
    directory if no regular config file (/etc/plinth/plinth.conf) is found.
    It creates all that data and runtime files in data/var/*.

    *Note:* This mode is supported only in a limited manner.  The following are
    the unknown issues with it:

    1. Help pages are also not built. Run 'make -C doc' manually.

    2. Actions do not work when running as normal user without 'sudo' prefix.
       You need to add 'actions' directory to be allowed for 'sudo' commands.
       See data/etc/sudoers.d/plinth for a hint.

### Testing Inside a Virtual Machine

1. Checkout source on the host.

2. Share the source folder and mount it on virtual machine.  This could be done
   over NFS, SSH-fs or 'Shared Folders' feature on VirtualBox.

3. Run 'setup.py develop' or 'setup.py install' as described above on guest
   machine.

4. Access the guest machine's Plinth web UI from host after setting bridging or
   NATing for guest virtual machine.

## Running Tests

1. Run tests:

    $ python3 setup.py test

## Running the Test Coverage Analysis

1. Run the coverage tool:

    $ python3 setup.py test_coverage

    Invoking this command generates a binary-format '.coverage' data file in
    the top-level project directory which is recreated with each run, and
    writes a set of HTML and other supporting files which comprise the
    browsable coverage report to the 'plinth/tests/coverage/report' directory.
    Index.html presents the coverage summary, broken down by module.  Data
    columns can be sorted by clicking on the column header or by using mnemonic
    hot-keys specified in the keyboard widget in the upper-right corner of the
    page.  Clicking on the name of a particular source file opens a page that
    displays the contents of that file, with color-coding in the left margin to
    indicate which statements or branches were executed via the tests (green)
    and which statements or branches were not executed (red).

## Building the Documentation Separately

Plinth man page is built from DocBook source in the doc/ directory.
FreedomBox manual is downloaded from the wiki is also available there.
Both these are build during the installation process.

1. To build the documentation separately, run:

    $ make -C doc

## Repository

Plinth is available from [GitHub](https://github.com/freedombox/plinth).

## Bugs & TODO

You can report bugs on Plinth's [issue
tracker](https://github.com/freedombox/Plinth/issues).

For new developers looking to start contributing to the project, this
is a good place to pick up a task to work on.  Tasks that are labeled
as 'beginner' are easy to work on and have a known solution.  Also,
other developers are ready to guide you on the implementation for such
tasks.

Feel free to pickup a task from the issue by announcing it on the
issue or by creating a new issue for whatever task you are going to
work on.

## Submitting Your Changes

Once you have completed implementing the solution, request a merge
into the upstream.

Pacthes can be submitted in either of the two ways:

- Post your patches to the FreedomBox discuss mailing list.  Look at
  Git documention on how to create submittable patches out of your
  commits and post them to the list.

- Create a pull request on Github.  For information on placing a merge
  request, consult GitHub documentation.

## Coding Practices

Plinth confirms to [PEP 8](http://www.python.org/dev/peps/pep-0008/) Python
coding standard. Before placing a merge request, you should check your code
for errors with *flake8* and indent your code with *yapf*.

## Internationalization

Every module should `from gettext import gettext as _` and wrap
displayed strings with _().  We don't have the language stuff in place
yet (we have no translation files), but we need to put the
infrastructure in place for it from the start.  Use it like this:

    log.error(_("Couldn't import %s: %s"), path, e)

## Translations

Introduce yourself on #freedombox IRC (irc.debian.org) and start translating
the PO file from your language directory from:
Plinth/plinth/locale/
Introducing yourself is important since some work may have been done already
on Debian translators discussion lists and Weblate localization platform.
https://hosted.weblate.org/projects/freedombox/plinth/
https://www.debian.org/MailingLists/subscribe
For more information on translations: https://wiki.debian.org/FreedomBox/Translate