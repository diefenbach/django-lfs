===========
Customizing
===========

Themeing
========

1. Erzeugen eines Ordners für das Theme

2. Erzeugen eines Ordners "static" (mit Unterordner) innerhalb des Themeordners

3. Kopieren des LFS "templates" Ordner  in den Themeordner. Die Ordnerstruktur 
   sollte wie folgt aussehen::

      mytheme
         |____ static
         |        |____ css
         |        |____ js
         |        |____ img
         |
         |____ templates
                  |____ 404.html
                  |____ 500.html
                  |____ base.html
                  |____ cart
                  |____ catalog
                  |____ ...
    
4. Erzeugen einer symbolischen Verknüpfung zum mytheme/static Ordner innerhalb 
   des Standard static Ordners von Django::
   
      $ cd /path/to/django/static/
      $ ln -s /path/to/mytheme/static mytheme
   
5. Anpassen des Basistemplates "base.html", so dass die Dateien des Themeordners
   verwendet werden, beispielsweise::
   
      <link rel="stylesheet" type="text/css" href="/static/mytheme/css/main.css" />
   
6. Registrieren des Templateordners in "settings.py". Vor Standardordner für
   Templates::

      TEMPLATE_DIRS = (
          "/path/to/mytheme/templates/",
          "/path/to/lfs/templates/",
          ... 
      )