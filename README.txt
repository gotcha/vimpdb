===================
Vim Pdb integration
===================

Abstract
========

This package provides an integration od the Python debugger ``pdb`` into the
VIM editor.

Requirements
============

Vim installed on your machine should support both ``python`` and ``clientserver``
options.

Find out if it is the case by issuing the following command at the vim prompt::

    :version

If the options are supported, you will see ``+clientserver`` and ``+python`` in the
output. In the opposite case, you will see ``-clientserver`` or ``-python``.

For Mac OS X you'll want to use MacVIM_, for Linux and Windows the default build
should be already server-enabled.  MacVIM_ has python compiled in by default, also.

.. _MacVIM:: http://code.google.com/p/macvim/

Installation
============

Just install this package using ``easy_install`` or similar::

    $ easy_install vimpdb

Make sure that the ``easy_install`` script you use is actually the one
from the python installation your VIM uses.


Configuration
=============

You might need to setup ``VIMPDB_VIMSCRIPT`` environment variable. It should hold
the command used at the shell prompt to launch Vim supporting the options
mentioned above. (Default value is ``vimpdb``).

This script should also set the ``--servername`` option to specify a server
name.  You can think of this as a "window name" which is used to send remote
commands to -- this is how **vimpdb** communicates with a certain VIM instance.

Server Name
-----------

You might need to setup ``VIMPDB_SERVERNAME`` environment variable. It should hold
the name of the Vim server you will be using. (Default value is ``VIMPDB``).  You may
list the currently running VIM servers using::

    $ vim --serverlist
    VIM

Or, on a Mac::

    $ /Applications/MacVim.app/Contents/MacOS/Vim --serverlist
    VIM

Note that the default Servername is ``VIM``

Starting a Vim Server for Debugging
-----------------------------------

You may start a VIM server for debugging like so::

    $ vim --servername VIMPDB

Or, on a Mac, if you installed the ``mvim`` script::

    $ mvim --servername VIMPDB

When a Vim supporting ``clientserver`` option has started, you can find its name by issuing the
following command at the Vim prompt:

    :echo v:servername

Using
=====

Using **vimpdb** is easy -- just call ``set_trace`` as usually::

    import vimpdb; vimpdb.set_trace() 

Now, when the python interpreter hits that line, VIM will get the focus and
load the source file.

Now you'll be able to use the following commands:

.. csv-table:: VimPDB Commands
    :header-rows:: 1

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
    x , Switch to debugging with standard Pdb.
    v , Switch back from the plain PDB to VimPdb


..  vim: set ft=rst ts=4 sw=4 expandtab tw=78 : 
