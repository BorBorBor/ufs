µFS Microfinance System
=======================

Dependencies for production use
-------------------------------

- python-django (>= 1.0)
- Patches from bugs #5853 (in 1.0) and #5494 (not in 1.0)
  See http://code.djangoproject.com/
- python-reportlab -- for PDF reports
- gettext -- for translations
- A database supported by Django, e.g. PostgreSQL, including Python
  adapter, e.g. python-psycopg2


Additional dependencies for development
---------------------------------------

- ``sudo easy_install coverage`` (for checking test coverage)
- djangologging (for debugging, from
  http://code.google.com/p/django-logging/)


How to install
--------------

This is a rather rough guide on how to install µFS.

1. Get all the dependencies listed above.
2. Checkout latest source from revision control using
   ``bzr co http://itk.samfundet.no/bzr/itkufs/itkufs.mainline/``
3. Compile translation files (.po -> .mo) using
   ``django-admin.py compilemessages``
4. Add a itkufs/settings/local.py file which sets the DATABASE_* and
   SECRET_KEY options.
5. Setup your web server. WSGI-files for production and development are
   found in the apache folder.


How to setup
------------

After the installation is completed, do the following:

1. Run ./manage.py syncdb to create database tables and create a
   superuser.
2. Go to e.g. http://127.0.0.1:8000/admin/ and log in using the newly
   created superuser.
3. Create a group, and add the superuser as admin of the group.
4. Go to e.g. http://127.0.0.1:8000/ and use µFS.
6. Profit!

Additional groups must be added from the Django admin, just like the first
one. All other operations should be possible to do from the µFS interface.


..
    vim: ft=rst tw=74 ai
