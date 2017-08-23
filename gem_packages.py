#!/usr/bin/python

import sys
import getopt

if sys.version_info < (2, 4):
    print "Your python interpreter is too old. Please consider upgrading."
    sys.exit(1)

import os
import logging
import optparse
import datetime
import time
import commands
import platform
import shutil
import StringIO
import glob
from subprocess import Popen, PIPE
from distutils.version import LooseVersion, StrictVersion
from os.path import expanduser

opennebula_path = "/usr/share/one"
install_gems_path = "%s/install_gems" % opennebula_path
lock_gems_path = "%s/Gemfile" % opennebula_path
gems_dir = '.gem'
exclude_gems = []


time_format_definition = "%Y-%m-%dT%H:%M:%SZ"
log = logging.getLogger('gem_packages')
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
purge = 0
createrepo = 0


def main(argv):
    global purge
    global createrepo
    try:
        opts, args = getopt.getopt(argv,'hdpc',['help','debug','purge', 'createrepo'])
    except getopt.GetoptError:
        print 'gem_packages.py -h'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print 'gem_packages.py'
            print 'Required sudo conf:'
            print '    <user>        ALL= (ALL)      NOPASSWD:       /usr/bin/yum install *'
            print '    <user>        ALL= (ALL)      NOPASSWD:       /usr/bin/apt-get install *'
            print '    <user>        ALL= (ALL)      NOPASSWD:       /usr/bin/gem install fpm mini_portile2 pkg-config'
            print ''
            print 'Usage:'
            print '    gem_packages.py [OPTIONS]'
            print ''
            print 'Options:'
            print '    -h, --help       Shows this help'
            print '    -d, --debug      Enable debug output'
            print '    -p, --purge      Purge temporal gems dir'
            print '    -c, --createrepo Generates repo dir or Packages.gz file'
            sys.exit()
        elif opt in ('-d','--debug'):
            log.setLevel(logging.DEBUG)
        elif opt in ('-p','--purge'):
            purge = 1
        elif opt in ('-c','--createrepo'):
            createrepo = 1

def execute_cmd(cmd):
    log.debug('Running: %s' % cmd)
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    if (p.returncode == 0) or (p.returncode == 34):
        return (output)
    else:
        log.debug(output)
        log.error("exit status %d" % p.returncode)
        sys.exit(2)

def install_packages(release):
    if (release == 'redhat') or (release == 'centos') or (release == 'ScientificSL'):
        print "redhat OS flavour detected."
        pkg_manager = "yum"
        pkg_fpm = "ruby-devel gcc"
        package = "rpm"

    elif (release == 'debian') or (release == 'Ubuntu'):
        print "debian OS flavour detected."
        pkg_manager = "apt"
        pkg_fpm = "ruby-dev gcc"
        package = "deb"

    else:
        print ("ERROR: Unknown distro {0}... exiting".format(release))
        log.error("Unknown distro: "+release)
        sys.exit(2)

    print "Installing required packages to generate gem packages."
    command = "sudo %s install -y %s" % (pkg_manager, pkg_fpm)
    output = execute_cmd(command)
    print "Intalling fpm gem."
    command = "sudo gem install fpm mini_portile2 pkg-config"
    output = execute_cmd(command)
    print "Installing required packages to compile new gems."
    command = "%s --showallpackages" % install_gems_path
    output = execute_cmd(command)
    packages = " ".join(output.split("\n"))
    command = "sudo %s install -y %s" % (pkg_manager, packages)
    output = execute_cmd(command)

    return package

def generate_gems():
    global gems_dir
    path = expanduser("~")
    gems_dir = os.path.join(path, gems_dir)
    if purge:
        shutil.rmtree(gems_dir)
    if not os.path.isdir(gems_dir):
        try:
            os.makedirs(gems_dir)
        except:
            print("Error creating dir %s , Exiting" % gems_dir)
            sys.exit(2)
    print "Compiling required gems.. Please wait."

    if os.path.isfile(lock_gems_path):
        log.debug("Found GemLock file: "+lock_gems_path)
        for gemfile in glob.glob(os.path.join(opennebula_path, 'Gemfile*')):
            try:
                shutil.copy2(gemfile, '.')
            except:
	        print("Error creating file %s , Exiting" % gemfile)
                sys.exit(3)
        command = "bundle install --path %s" % gems_dir
        output = execute_cmd(command)
        log.debug(output)

        # Workaround for nokogiri update
        command = "bundle update nokogiri"
        output = execute_cmd(command)

        log.debug(output)
    else:
        command = "%s --showallgems" % install_gems_path
        output = execute_cmd(command)
        buf = StringIO.StringIO(output)
        for line in buf:
            if not any(exclude_gem in line for exclude_gem in exclude_gems):
                command = "gem install --no-ri --no-rdoc --user-install %s" % (line)
                output = execute_cmd(command)
    gems_dir = "%s/ruby" % gems_dir

def generate_packages(pkg,version):
    print "Creating gem packages."

    if (pkg == 'rpm'):
        if (LooseVersion(version) < LooseVersion("7")):
            prefix = "/usr/lib/ruby/gems/1.8"
        else:
            prefix = "/usr/share/gems"
        log.debug("Found  RH/CentOS %s. prefix set to: %s" % (version, prefix))
    elif (pkg == 'deb'):
        prefix = "/var/lib/gems"

    command = "find %s/cache -name '*.gem' | xargs -rn1 fpm --prefix %s -p %s -s gem -x doc -x build_info -t %s" % (gems_dir, prefix, gems_dir, pkg)
    output = execute_cmd(command)
    log.debug(output)

def create_repo(pkg):
    if (pkg == 'rpm'):
        print "Creating rpm repo files."
        # it requires createrepo
        command = "createrepo -v %s" % (gems_dir)
    elif (pkg == 'deb'):
        # it requires dpkg-dev package
        print "Creating Packages.gz file."
        command = "dpkg-scanpackages %s /dev/null | gzip -9c > %s/Packages.gz" % (gems_dir,gems_dir)

    output = execute_cmd(command)

if __name__ == "__main__":
    main(sys.argv[1:])
    euid = os.geteuid()

    if euid == 0:
        print "This script cannot be executed as root. Exiting.."
        sys.exit(2)

    release = platform.dist()[0]
    version = platform.dist()[1]
    package = install_packages(release)
    generate_gems()
    generate_packages(package,version)

    if createrepo:
        create_repo(package)

    sys.exit(0)

