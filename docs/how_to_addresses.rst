How to use localized addresses
==============================

Address localisation is turned on by default in LFS.
To turn off Address l10n: in settings.py set 
::
	LFS_ADDRESS_L10N = False


Customize address labels and requirement
----------------------------------------

If you wish to customize the address labels and whether the address line is 
required or not, you can add the following variables to settings.py
::
	POSTAL_ADDRESS_FIRSTNAME
	POSTAL_ADDRESS_LASTNAME
	POSTAL_ADDRESS_LINE1
	POSTAL_ADDRESS_LINE2
	POSTAL_ADDRESS_LINE3
	POSTAL_ADDRESS_LINE4
	POSTAL_ADDRESS_LINE5

each of these variables is set to a tuple of the format ('label', True/False)
'label' is used to label the field, and the second boolean value sets whether
the field is required or not, e.g.
::
	POSTAL_ADDRESS_LINE1 = ("Department", True)