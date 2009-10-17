Installation
============

Prequisites
-----------

Make sure you have installed:

   * Python (we recommend 2.6.x)
   * sqlite

Installation
------------

The installation is straightforward and should last just a few minutes.

   1. Get the installer: hg clone http://bitbucket.org/diefenbach/lfs-buildout-quickstart/
   2. cd lfs-buildout-quickstart
   3. python boostrap.py
   4. bin/buildout -v
   5. Start the server: bin/django runserver
   
Now open your browser and visit: 

   * The frontend: http://localhost:8000/
   * The management interface: http://localhost:8000/manage
   
That's all!

What's next?
------------
Move on to :doc:`getting_started`.