

from setuptools import setup, find_packages

setup(
	name='funmongo',
	version='0.1.3',
	description='A safe and easy to use MongoDB ORM for python',
	long_description="None",
	url='https://github.com/dbousque/funmongo',
	author='Dominik Bousquet',
	license='MIT',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Libraries',
		'Topic :: Database',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.3',
		'Programming Language :: Python :: 2.4',
		'Programming Language :: Python :: 2.5',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.0',
		'Programming Language :: Python :: 3.1',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6'
	],
	keywords='mongodb functional orm',
	packages=find_packages(exclude=['contrib', 'docs', 'tests']),
	install_requires=['pymongo', 'datetime']
)