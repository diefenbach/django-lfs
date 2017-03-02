How to integrate localized version of TinyMCE
=============================================

LFS ships with main package of TinyMCE that doesn't contain any translation files.
It is easy to use internationalized version of TinyMCE by adding few things into your theme.

Steps
-----

#. Download TinyMCE

   Go to TinyMCE website and `download TinyMCE x.x jQuery package <http://www.tinymce.com/download/download.php>`_

#. Extract TinyMCE into your ``theme``

   Extract downloaded ``TinyMCE`` into your :doc:`Theme </developer/howtos/theme/index>`, e.g. ``theme/static/manage/tiny_mce_x_x/``

#. Download TinyMCE language file(s)

   Go to TinyMCE website and `download language file(s) <http://www.tinymce.com/i18n/index.php?ctrl=lang&act=download&pr_id=1>`_ that you need

#. Extract TinyMCE language files into your ``theme``

   Go to folder where you've just extracted main package of TinyMCE, e.g.: ``theme/static/manage/tiny_mce_x_x/``
   and extract language files into proper directories.

#. Copy ``manage_base.html`` to your theme

   Copy ``lfs/templates/manage/manage_base.html`` to your theme: ``mytheme/templates/manage/manage_base.html``

#. Copy ``lfs_tinymce.js`` to your theme

   Copy ``lfs/static/js/lfs_tinymce.js`` to your theme: ``mytheme/static/js/lfs_tinymce.js``
   (if you use different path then you have to update it at manage_base.html in step 7)

#. Modify ``lfs_tinymce.js`` (copy located at your theme)

   Change/add highlighted parts of TinyMCE initialization script:

   .. code-block:: javascript
     :emphasize-lines: 4,20

     // Theme options
     $(selector).tinymce({
         // Location of TinyMCE script
         script_url : '/static/manage/tiny_mce_x_x/tiny_mce.js',

         // General options
         theme : "advanced",
         plugins : "safari,save,iespell,directionality,fullscreen,xhtmlxtras,media",

         theme_advanced_buttons1 : buttons,
         theme_advanced_buttons2 : "",
         theme_advanced_buttons3 : "",
         theme_advanced_buttons4 : "",
         theme_advanced_toolbar_location : "top",
         theme_advanced_toolbar_align : "left",
         save_onsavecallback : "save",
         relative_urls : false,
         cleanup : false,
         height : height,
         language : LFS_LANGUAGE,
         content_css : "/static/css/tinymce_styles.css",
         setup : function(ed) {
             ed.addButton('image', {
                 onclick : function(e) {
                     imagebrowser(e, ed);
                 }
             });
         }
     });

#. Customize ``manage_base.html`` at your theme

   Replace:

   .. code-block:: html

     <script type="text/javascript" src="{% static 'tiny_mce-3.4.2/jquery.tinymce.js' %}"></script>

   with (use path to TinyMCE folder that you created in step 2):

   .. code-block:: html

     <script type="text/javascript" src="{% static 'manage/tiny_mce_x_x/jquery.tinymce.js' %}"></script>

   Add following code to <head> section:

   .. code-block:: html

     <script type="text/javascript">
       var LFS_LANGUAGE = '{{ LANGUAGE_CODE|lower }}';
     </script>

   Note that for some languages ``LANGUAGE_CODE`` used by Django may differ from language code used by TinyMCE.
   For such cases you'll probably have to write your own tag/filter that will map Django's language code to TinyMCE's
   language code (or you'll just hard code it).
