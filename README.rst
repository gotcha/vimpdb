===================
VIM Pdb integration
===================

.. contents::

Abstract
========

This package provides an integration of the Python debugger ``pdb`` into the
VIM editor.

Usage
=====

Python code
-----------

Using **vimpdb** is easy -- just insert a call to ``set_trace`` in your code
almost as usual::

    import vimpdb; vimpdb.set_trace() 

Then start your python application/script.

When the python interpreter hits that line, **vimpdb** will launch a VIM 
instance. VIM should get the focus; it loads the source file at the right line.

VIM commands
------------

In VIM, you may now use the following commands:

.. csv-table:: **vimpdb** commands
    :header-rows: 1

    Ex Command, Key binding, Details
    ``:PDBNext``, ``n`` , ``pdb`` (n)ext
    ``:PDBStep``, ``s`` , ``pdb`` (s)tep 
    ``:PDBArgs``, ``a`` , ``pdb`` (a)rgs
    ``:PDBUp``, ``u`` , ``pdb`` (u)p
    ``:PDBDown``, ``d`` , ``pdb`` (d)own
    ``:PDBReturn``, ``r`` , ``pdb`` (r)eturn
    ``:PDBContinue``, ``c`` , ``pdb`` (c)ontinue
    ``:PDBBreak``, ``b`` , Sets a breakpoint at the line on which the cursor is sitting; similar to ``pdb`` b(reak)
    ``:PDBClear``, ``B`` , Clears a breakpoint at the line on which the cursor is sitting; similar to ``pdb`` cl(ear)
    ``:PDBWord``, ``w`` , Evaluates the value of the identifier on which the cursor is sitting.
    ``:PDBEval``, ``?`` , Evaluates a Python expression after having asked for it.
    ``:PDBReset``, ``x`` , Switch back to normal debugging in shell with standard ``pdb``.
    N/A, ``v(im)`` , Switch back to **vimpdb**; only in plain ``pdb``.

Standard ``pdb`` hook
---------------------

If you find it hard to change habits and keep on typing 

::

    import pdb; pdb.set_trace()

you can add the following line to the  ``.pdbrc`` file sitting in your home
folder::

    import vimpdb; vimpdb.hookPdb()

This way, the command ``v(im)`` mentioned above is added to your standard 
``pdb`` and you can switch to **vimpdb** at any time.

Requirements
============

**vimpdb** has been used successfully under Linux, Mac OSX and Windows.

It **is compatible** with Python 2.7, 2.6, 2.5 and 2.4. 
It **is not compatible** with Python 3.1 (it should be the same for 3.0).

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

Standard installation with ``easy_install`` ::

    $ easy_install vimpdb

You can obviously also use ``pip``.

    If you look inside the package, you will see a VIM script file: ``vimpdb.vim``.
    Do **not** move it to VIM configuration directory (like ``~/.vim/plugin``).
    **vimpdb** knows how to make the script available to VIM.

Configuration
=============

Short story
-----------

**vimpdb** tries to avoid depending on any user configuration.
If it cannot detect the right configuration by itself, 
it will ask a few questions which you should be able to answer easily.

Long story
----------

When launched, **vimpdb** looks for its RC file : ``~/.vimpdbrc``. If it does
not find it, **vimpdb** creates that file for you from default values.

**vimpdb** tries a set of default values that should work.
It checks if those default values are appropriate.
If the default values do not work, **vimpdb** asks for other values 
interactively until it has checked that the values provided actually work.

The default values per OS are listed hereunder.

For Linux::

    vim_client_script = vim
    vim_server_script = gvim
    server_name = GVIM
    port = 6666

For MacOSX::

    vim_client_script = mvim
    vim_server_script = mvim
    server_name = VIM
    port = 6666

For Windows::

    vim_client_script = vim.exe
    vim_server_script = gvim.exe
    server_name = VIM
    port = 6666

See below for details about each option.

You are obviously allowed to create and tune that RC file.
Nevertheless, the RC file should hold values for all 4 options.
If one of them is missing, **vimpdb** breaks and complains accordingly.


VIM client script - ``vim_client_script``
-----------------------------------------

To communicate with the VIM instance where debugging happens,
**vimpdb** needs to launch another VIM instance in client mode. 

``vim_client_script`` option holds the script used to launch that VIM instance 
with ``clientserver`` support.

On Windows, it should hold ``vim.exe``, **not** ``gvim.exe``.
Furthermore, do **not** include quotes in the value to take care
of whitespace in the path.

VIM server script - ``vim_server_script``
-----------------------------------------

In case no VIM instance is running, **vimpdb** launches a VIM instance in
server mode.

``vim_server_script`` option holds the script used to launch that VIM instance
with ``clientserver`` support. As debugging in the VIM instance is written with
python, that instance must have ``python`` support.

On MacOSX and Linux, ``vim_server_script`` and ``vim_client_script`` can hold 
the same value.

On Windows, only the graphical VIM can be used as server, reason for the two 
separate default values as seen above.

Server Name - ``server_name``
-----------------------------

The VIM instance in server mode has a name.

By default, **vimpdb** speaks to the server named ``VIM``, which  
is the default ``servername`` used by VIM.

If you want **vimpdb** to use another server name, modify the 
``server_name`` option. It should hold the name of the VIM
server you want to be used for debugging. 

You may list the currently running VIM servers using::

    $ vim --serverlist
    VIM

Or, on a Mac::

    $ /Applications/MacVim.app/Contents/MacOS/Vim --serverlist
    VIM

When a VIM instance with ``clientserver`` support is running, you can find its 
name by issuing the following command at the VIM prompt::

    :echo v:servername

UDP Port - ``port``
-------------------

VIM communicates to **vimpdb** through a UDP socket. 
By default, the socket is opened on port 6666.

If that socket is not available in your system, you can specify an available
port number with the ``port`` option.

Known issues
============

None for now.

Backward Compatibility
======================

Before version 0.4.1, **vimpdb** RC file (``~/.vimpdbrc``) had a single 
``script`` option. That option has been turned into the ``vim_client_script``
option. The upgrade should be transparent.

Before version 0.4.0, **vimpdb** was configured through environment variables.
If you had a working configuration, upgrade should be transparent.
The values of ``VIMPDB_SERVERNAME`` and ``VIMPDB_VIMSCRIPT`` environment
variables are setup in the RC file (``~/.vimpdbrc``). 
They are put respectively in ``server_name`` and ``script`` options.

Fixed issues
============

See changelog_

.. _changelog: http://pypi.python.org/pypi/vimpdb#id1

..  vim: set ft=rst ts=4 sw=4 expandtab tw=78 : 
