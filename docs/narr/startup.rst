.. _startup_chapter:

Startup
=======

When you cause a :app:`Pyramid` application to start up in a console window,
you'll see something much like this show up on the console:

.. code-block:: text

  $ paster serve myproject/MyProject.ini
  Starting server in PID 16601.
  serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

This chapter explains what happens between the time you press the "Return"
key on your keyboard after typing ``paster serve myproject/MyProject.ini``
and the time the line ``serving on 0.0.0.0:6543 ...`` is output to your
console.

.. index::
   single: startup process

The Startup Process
-------------------

The easiest and best-documented way to start and serve a :app:`Pyramid`
application is to use the ``paster serve`` command against a
:term:`PasteDeploy` ``.ini`` file.  This uses the ``.ini`` file to infer
settings and starts a server listening on a port.  For the purposes of this
discussion, we'll assume that you are using this command to run your
:app:`Pyramid` application.

Here's a high-level time-ordered overview of what happens when you press
``return`` after running ``paster serve development.ini``.

#. The :term:`PasteDeploy` ``paster`` command is invoked under your shell
   with the arguments ``serve`` and ``development.ini``.  As a result, the
   :term:`PasteDeploy` framework recognizes that it is meant to begin to run
   and serve an application using the information contained within the
   ``development.ini`` file.

#. The PasteDeploy framework finds a section named either ``[app:main]``,
   ``[pipeline:main]``, or ``[composite:main]`` in the ``.ini`` file.  This
   section represents the configuration of a :term:`WSGI` application that
   will be served.  If you're using a simple application (e.g.
   ``[app:main]``), the application :term:`entry point` or :term:`dotted
   Python name` will be named on the ``use=`` line within the section's
   configuration.  If, instead of a simple application, you're using a WSGI
   :term:`pipeline` (e.g. a ``[pipeline:main]`` section), the application
   named on the "last" element will refer to your :app:`Pyramid` application.
   If instead of a simple application or a pipeline, you're using a Paste
   "composite" (e.g. ``[composite:main]``), refer to the documentation for
   that particular composite to understand how to make it refer to your
   :app:`Pyramid` application.

#. The application's *constructor* (named by the entry point reference or
   dotted Python name on the ``use=`` line of the section representing your
   :app:`Pyramid` application) is passed the key/value parameters mentioned
   within the section in which it's defined.  The constructor is meant to
   return a :term:`router` instance, which is a :term:`WSGI` application.

   For :app:`Pyramid` applications, the constructor will be a function named
   ``main`` in the ``__init__.py`` file within the :term:`package` in which
   your application lives.  If this function succeeds, it will return a
   :app:`Pyramid` :term:`router` instance.  Here's the contents of an example
   ``__init__.py`` module:

   .. literalinclude:: MyProject/myproject/__init__.py
      :language: python
      :linenos:

   Note that the constructor function accepts a ``global_config`` argument,
   which is a dictionary of key/value pairs mentioned in the ``[DEFAULT]``
   section of an ``.ini`` file.  It also accepts a ``**settings`` argument,
   which collects another set of arbitrary key/value pairs.  The arbitrary
   key/value pairs received by this function in ``**settings`` will be
   composed of all the key/value pairs that are present in the
   ``[app:MyProject]`` section (except for the ``use=`` setting) when this
   function is called by the :term:`PasteDeploy` framework when you run
   ``paster serve``.

   Our generated ``development.ini`` file looks like so:

   .. literalinclude:: MyProject/development.ini
      :language: ini
      :linenos:

   In this case, the ``myproject.__init__:main`` function referred to by the
   entry point URI ``egg:MyProject`` (see :ref:`MyProject_ini` for more
   information about entry point URIs, and how they relate to callables),
   will receive the key/value pairs ``{'reload_templates':'true',
   'debug_authorization':'false', 'debug_notfound':'false',
   'debug_routematch':'false', 'debug_templates':'true',
   'default_locale_name':'en'}``.

#. The ``main`` function first constructs a
   :class:`~pyramid.config.Configurator` instance, passing a root resource
   factory (constructor) to it as its ``root_factory`` argument, and
   ``settings`` dictionary captured via the ``**settings`` kwarg as its
   ``settings`` argument.

   The root resource factory is invoked on every request to retrieve the
   application's root resource.  It is not called during startup, only when a
   request is handled.

   The ``settings`` dictionary contains all the options in the
   ``[app:MyProject]`` section of our .ini file except the ``use`` option
   (which is internal to Paste) such as ``reload_templates``,
   ``debug_authorization``, etc.

#. The ``main`` function then calls various methods on the an instance of the
   class :class:`~pyramid.config.Configurator` method.  The intent of
   calling these methods is to populate an :term:`application registry`,
   which represents the :app:`Pyramid` configuration related to the
   application.

#. The :meth:`~pyramid.config.Configurator.make_wsgi_app` method is called.
   The result is a :term:`router` instance.  The router is associated with
   the :term:`application registry` implied by the configurator previously
   populated by other methods run against the Configurator.  The router is a
   WSGI application.

#. A :class:`~pyramid.events.ApplicationCreated` event is emitted (see
   :ref:`events_chapter` for more information about events).

#. Assuming there were no errors, the ``main`` function in ``myproject``
   returns the router instance created by ``make_wsgi_app`` back to
   PasteDeploy.  As far as PasteDeploy is concerned, it is "just another WSGI
   application".

#. PasteDeploy starts the WSGI *server* defined within the ``[server:main]``
   section.  In our case, this is the ``Paste#http`` server (``use =
   egg:Paste#http``), and it will listen on all interfaces (``host =
   0.0.0.0``), on port number 6543 (``port = 6543``).  The server code itself
   is what prints ``serving on 0.0.0.0:6543 view at http://127.0.0.1:6543``.
   The server serves the application, and the application is running, waiting
   to receive requests.

.. _deployment_settings:

Deployment Settings
-------------------

Note that an augmented version of the values passed as ``**settings`` to the
:class:`~pyramid.config.Configurator` constructor will be available in
:app:`Pyramid` :term:`view callable` code as ``request.registry.settings``.
You can create objects you wish to access later from view code, and put them
into the dictionary you pass to the configurator as ``settings``.  They will
then be present in the ``request.registry.settings`` dictionary at
application runtime.
