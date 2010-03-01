
Vim and Pdb integration

Requirements
------------

Vim installed on your machine should support both ``python`` and ``clientserver``
options.

Find out if it is the case by issuing the following command at the vim prompt:

    :version

If the options are supported, you will see ``+clientserver`` and ``+python`` in the
output. In the opposite case, you will see ``-clientserver`` or ``-python``.

Setup
-----

You might need to setup ``VIMPDB_VIMSCRIPT`` environment variable. It should hold
the command used at the shell prompt to launch Vim supporting the options
mentioned above. (Default value is ``vimpdb``).

You might need to setup ``VIMPDB_SERVERNAME`` environment variable. It should hold
the name of the Vim server you will be using. (Default value is ``VIMPDB``).

When a Vim supporting ``clientserver`` option has started, you can find its name by issuing the
following command at the Vim prompt:

    :echo v:servername

Debugging
---------

* Put ``vimpdb`` egg in your python path. 

* Add the following code (which should feel familiar) where you need it:

    import vimpdb; vimpdb.set_trace() 

* Start Vim.

* Start your script or application.

* When ``set_trace`` is met, Vim will spring to the foreground,
  showing the appropriate file at the right line.

* You can type commands right in the Vim buffer.

The following Pdb commands are currently supported :

  n 
    Next

  s 
    Step

  a 
    Args

  u 
    Up

  d 
    Down

  r 
    Return

  c 
    Continue

The following commands are specific to ``vimpdb`` :

  b 
    Sets a breakpoint at the line on which the cursor is sitting.

  w 
    Displays the value of the word on which the cursor is sitting.

  x 
    Switch to debugging with standard Pdb.

After having switched to Pdb, you can turn back to Vim debugging by issuing
``v(im)`` command in Pdb.

