# addon-installgems

## Description
This addon generates the extra gem packages (deb or rpm) required by OpenNebula service.

This configuration is useful for automate the deployment of OpenNebula service. The new packages can be uploaded to a local repository to be installed or used by any configuration management tool or PXE installation.

## Development

To contribute bug patches or new features, you can use the github Pull Request model. It is assumed that code and documentation are contributed under the Apache License 2.0. 

More info:
* [How to Contribute](http://opennebula.org/addons/contribute/)
* Support: [OpenNebula Support Forum](https://forum.opennebula.org/c/support)
* Development: [OpenNebula Development Forum](https://forum.opennebula.org/c/development)
* Issues Tracking: Github issues

## Authors

* Leader: Alvaro Simon (Alvaro.SimonGarcia@UGent.be)

## Compatibility

This add-on is compatible with OpenNebula >= 4.12

## Features

It replaces `install_gems` execution. It provides extra packages required by OpenNebula service to deploy automated installations.

## Limitations

Only Debian and RedHat linux OS flavours are supported at this moment.

## Requirements

* opennebula-ruby > 4.10.2
* Python 2.4
* This script uses fpm gem to generate OS packages. This gem is automatically installed by the addon. [fpm wiki](https://github.com/jordansissel/fpm/wiki)

## Installation

**NOTE:** For security reasons it is recommended to execute this addon in a sandbox rather than on a production system.
Install opennebula-ruby and this script in your target system as usual.

### Optional
To generate the repo files install these packages in RedHat:
~~~
# yum install createrepo redhat-lsb rpm-build
~~~
To generate Packages.gz install dpkg-dev in Debian:
~~~
# apt-get install dpkg-dev
~~~

## Configuration

* Set sudo to allow to execute these commands as root, as example to execute this script as oneadmin user:
~~~
oneadmin        ALL= (ALL)      NOPASSWD:       /usr/bin/yum install *
oneadmin        ALL= (ALL)      NOPASSWD:       /usr/bin/apt-get install *
oneadmin        ALL= (ALL)      NOPASSWD:       /usr/bin/gem install fpm mini_portile2 pkg-config
~~~

* Set `install_gems` path in `gem_packages.py` if it is needed:
~~~
install_gems_path = "/usr/share/one/install_gems"
~~~

* Set exclude_gems variable if it is required. In this case gem_packages will not generate sinatra and rack rpms: 
~~~
exclude_gems = ['sinatra', 'rack']
~~~

## Usage

* You must execute the script as regular user or oneadmin (never as root)
* To generate the new gem packages just run:
~~~
gem_packages.py
~~~
* The New deb/rpm packages will be available into gems_dir directory.

* Extra info:
~~~
gem_packages.py --help
~~~

## TODO

Upload the new packages to an internal repository configured by the user.

## References

* [fpm](https://github.com/jordansissel/fpm)

## License

Apache v2.0 license.
