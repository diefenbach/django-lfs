Installation
============

Prequisites
-----------

Make sure you have installed:

   * Python 2.6.x http://www.python.org/download/
   * sqlite http://www.sqlite.org/download.html
   * mercurial http://mercurial.selenic.com/wiki
   * git http://git-scm.com/
   
Please note:

   * The dependency of mercurial and git will be disappear in near future. 
   * You can - of course - use another database but we provide a filled sqlite
     database for convenience.

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
Move on to :doc:`/user/getting_started`.