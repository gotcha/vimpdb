===================
VIM Pdb integration
===================

.. contents::

Abstract
========

This package provides an integration of the Python debugger ``pdb`` into the
VIM editor.

Requirements
============

**vimpdb** has been used successfully under Linux, Mac OSX and Windows.

It **is compatible** with Python 2.6, 2.5 and 2.4. It is not known if it does work
with Python 3.0 (let us know).

**vimpdb** requires an installation of VIM that supports both ``python`` and
``clientserver`` options.

Find out if it is the case by issuing the following command at the VIM prompt::

    :version

If the options are supported, you will see ``+clientserver`` and ``+python`` in the
output. In the opposite case, you will see ``-clientserver`` or ``-python``.

On Linux and Windows, the default VIM build should already be server-enabled.

On Windows, the ``python`` option compiled in VIM depends on a specific Python
version. Find out if that specific version is installed and works in VIM by
issuing the following command at the VIM prompt::

    :python import sys; print sys.version

On Mac OSX, you'll want to use MacVIM_. MacVIM also has the ``python`` option 
compiled in by default.

.. _MacVIM: http://code.google.com/p/macvim/

Installation
============

Just install this package using ``easy_install`` or similar::

    $ easy_install vimpdb

If you look inside the package, you will see a VIM script file: ``vimpdb.vim``.
Do **not** move it to VIM configuration directory (like ``~/.vim/plugin``).

Configuration
=============

VIM script
----------

To communicate with the VIM instance where debugging happens,
**vimpdb** needs to launch another VIM instance in client mode. 

By default, **vimpdb** uses the ``vim`` script to start that VIM instance with 
clientserver support. If there exists such a ``vim`` script on your path, you are ok.

You can configure another script with the ``VIMPDB_VIMSCRIPT`` environment variable.
It must hold the script that **vimpdb** should use to launch a VIM instance 
with clientserver support.

On Windows, it should hold the path to ``vim.exe``, **not** to ``gvim.exe``.
Furthermore, do **not** include quotes in the enviromnent variable to take care
of whitespace in the path.

Server Name
-----------
By default, **vimpdb** speaks to the server named ``VIMPDB``.  
Note that the default ``servername`` used by VIM is ``VIM``.

If want **vimpdb** to use another server name, you need to setup the 
``VIMPDB_SERVERNAME`` environment variable. It should hold the name of the VIM
server you will be using for debugging. 

You may list the currently running VIM servers using::

    $ vim --serverlist
    VIM

Or, on a Mac::

    $ /Applications/MacVim.app/Contents/MacOS/Vim --serverlist
    VIM

When a VIM instance with ``clientserver`` support is running, you can find its name by issuing the
following command at the VIM prompt::

    :echo v:servername


Usage
=====

Starting VIM
------------

To start a VIM instance for debugging, issue the following command on the shell::

    $ vim --servername VIMPDB

Or, on a Mac, if you installed the ``mvim`` script::

    $ mvim --servername VIMPDB

Python code
-----------

Using **vimpdb** is easy -- just insert a call to ``set_trace`` in your code
almost as usual::

    import vimpdb; vimpdb.set_trace() 

Then start your python application/script.

When the python interpreter hits that line, VIM will get the focus and
load the source file at the right line.

VIM commands
------------

In VIM, you may now use the following commands:

.. csv-table:: VimPDB Commands
    :header-rows: 1

    Key, Command
    n , Next
    s , Step
    a , Args
    u , Up
    d , Down
    r , Return
    c , Continue
    b , Sets a breakpoint at the line on which the cursor is sitting.
    w , Displays the value of the word on which the cursor is sitting.
    x , Switch to debugging in shell with standard Pdb.
    v , Switch back to VimPdb from plain Pdb.

Standard Pdb hook
=================

If you find it hard to change habits and keep on typing 

::

    import pdb; pdb.set_trace()

you can add the following line to the  ``.pdbrc`` file sitting in your home
folder::

    import vimpdb; vimpdb.hookPdb()

This way, the command ``v(im)`` mentioned above is added to your standard Pdb
and you can switch to **vimpdb** at any time.

Known issues
============

* No convenient way to evaluate a Python expression.

Fixed issues
============

See changelog_

.. _changelog: http://pypi.python.org/pypi/vimpdb#id1

..  vim: set ft=rst ts=4 sw=4 expandtab tw=78 : 
