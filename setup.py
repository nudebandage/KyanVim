from setuptools import setup, find_packages # Always prefer setuptools over distutils
from codecs import open # To use a consistent encoding
from os import path
here = path.abspath(path.dirname(__file__))
setup(
	name = 'kyanvim',
	# Versions should comply with PEP440. For a discussion on single-sourcing
	# the version across setup.py and the project code, see
	# https://packaging.python.org/en/latest/single_source_version.html
	version='0.1.0',
	description = 'kyanvim!',
	author='tmothy eichler',
	author_email='tim_eichler@hotmail.com',
	packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
	
	# List run-time dependencies here. These will be installed by pip when your
	# project is installed. For an analysis of "install_requires" vs pip's
	# requirements files see:
	# https://packaging.python.org/en/latest/requirements.html
	#~ install_requires=['peppercorn'],
	
	# List additional groups of dependencies here (e.g. development dependencies).
	# You can install these using the following syntax, for example:
	# $ pip install -e .[dev,test]
	#~ extras_require = {
	#~ 'dev': ['check-manifest'],
	#~ 'test': ['coverage'],
	#~ },
	
	# If there are data files included in your packages that need to be
	# installed, specify them here. If using Python 2.6 or less, then these
	# have to be included in MANIFEST.in as well.
	#~ package_data={
	#~ 'sample': ['package_data.dat'],
	#~ },
	
	# Although 'package_data' is the preferred approach, in some case you may
	# need to place data files outside of your packages.
	# see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
	# In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
	#~ data_files=[('my_data', ['data/data_file'])],
	
	# To provide executable scripts, use entry points in preference to the
	# "scripts" keyword. Entry points provide cross-platform support and allow
	# pip to create the appropriate form of executable for the target platform.
	#~ entry_points = {
			#~ 'console_scripts': [
				#~ 'sample=sample:main',],},
)
