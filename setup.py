# python imports
import os
from setuptools import find_packages
from setuptools import setup

# lfs imports
from lfs import __version__

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(name='django-lfs',
      version=__version__,
      description='LFS - Lightning Fast Shop',
      long_description=README,
      classifiers=[
          'Environment :: Web Environment',
          'Framework :: Django',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
      keywords='django e-commerce online-shop',
      author='Kai Diefenbach',
      author_email='kai.diefenbach@iqpp.de',
      url='http://www.getlfs.com',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      dependency_links=["http://pypi.iqpp.de/"],
      install_requires=[
          'setuptools',
          'Django >= 1.10, < 1.11',
          'django-compressor == 2.1.1',
          'django-localflavor == 1.4.1',
          'django-paypal == 0.3.6',
          'django-portlets >= 1.5, < 1.6',
          'django-postal == 0.96',
          'django-reviews >= 1.2, < 1.3',
          'lfs-contact >= 1.3, < 1.4',
          'lfs-order-numbers >= 1.2, < 1.3',
          'lfs-paypal >= 1.4, < 1.5',
          'lfs-theme >= 0.11, < 0.12',
          'Pillow == 4.0',
      ],
      )
