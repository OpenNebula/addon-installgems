addon-installgems
===========

_Creation of distro packages to install opennebula ruby gems_
_This script uses fpm gem to generate OS packages_

* fpm wiki -- http://repository.egi.eu/

Requirements
------------

* OpenNebula > 4.10
* Python 2.4

Configuration
------------

 * Set sudo to allow to execute these commands as root:
~~~
<user_name>        ALL= (ALL)      NOPASSWD:       /usr/bin/yum install *
<user_name>        ALL= (ALL)      NOPASSWD:       /usr/bin/apt-get install *
<user_name>        ALL= (ALL)      NOPASSWD:       /usr/bin/gem install fpm
~~~

### Examples
To publish new gem packages just run:
~~~
./gem_packages.py
~~~
New deb/rpm packages will be available into gems_dir directory