addon-installgems
===========

_Creation of distro packages to install opennebula ruby gems_
_This script uses FPM gem to generate OS packages_

* FPM wiki -- http://repository.egi.eu/

Requirements
------------

* OpenNebula > 4.10
* Python 2.4

### Examples
To publish new gem packages just run:
~~~
./gem_packages.py
~~~
New deb/rpm packages will be available into gems_dir directory