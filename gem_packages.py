#!/usr/bin/python

import sys
import getopt

if sys.version_info < (2, 4):
    print "Your python interpreter is too old. Please consider upgrading."
    sys.exit(1)

import os
import logging
import optparse
#import hashlib
import datetime
import time
import commands
import platform
import shutil
import StringIO
from subprocess import Popen, PIPE

install_gems_path = "/usr/share/one/install_gems"
gems_dir = 'gems_dir'

time_format_definition = "%Y-%m-%dT%H:%M:%SZ"
log = logging.getLogger('gem_packages')
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
purge = 0



def main(argv):
    try:
        opts, args = getopt.getopt(argv,'hdp',['help','debug','purge='])
    except getopt.GetoptError:
        print 'gem_packages.py -h'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print 'gem_packages.py'
            print 'Required sudo conf:'
            print '    <user>        ALL= (ALL)      NOPASSWD:       /usr/bin/yum install *'
            print '    <user>        ALL= (ALL)      NOPASSWD:       /usr/bin/apt-get install *'
            print '    <user>        ALL= (ALL)      NOPASSWD:       /usr/bin/gem install fpm'
            print ''
            print 'Usage:'
            print '    gem_packages.py [OPTIONS]'
            print ''
            print 'Options:'
            print '    -h, --help   Shows this help'
            print '    -d, --debug  Enable debug output'
            print '    -p, --purge  Purge temporal gems dir'
            sys.exit()
        elif opt in ('-d','--debug'):
            log.setLevel(logging.DEBUG)
        elif opt in ('-p','--purge'):
            purge = 1

def execute_cmd(cmd):
    log.debug('Running: %s' % cmd)
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    if p.returncode == 0:
        return (output)
    else:
        log.debug(output)
        log.error("exit status %d" % p.returncode)
        sys.exit(2)

def install_packages(release):
    if (release == 'redhat') or (release == 'centos'):
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
    command = "sudo gem install fpm"
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
    path = os.getcwd()
    gems_dir = os.path.join(path, gems_dir)
    if purge:
        shutil.rmtree(gems_dir)
    if not os.path.isdir(gems_dir):
        try:
            os.makedirs(gems_dir)
        except:
            print("Error creating dir %d , Exiting" % gems_dir)
            sys.exit(2)
    print "Compiling required gems.. Please wait."
    command = "%s --showallgems" % install_gems_path
    output = execute_cmd(command)
    buf = StringIO.StringIO(output)
    for line in buf:
        command = "gem install --no-ri --no-rdoc --install-dir %s %s" % (gems_dir, line)
        output = execute_cmd(command)

def generate_packages(pkg):
    print "Creating gem packages."

    if (pkg == 'rpm'):
        prefix = "/usr/share/gems"
    elif (pkg == 'deb'):
        prefix = "/var/lib/gems"

    command = "find %s/cache -name '*.gem' | xargs -rn1 fpm --prefix %s -p %s -s gem -t %s" % (gems_dir, prefix, gems_dir, pkg)
    output = execute_cmd(command)
    print output

if __name__ == "__main__":
    main(sys.argv[1:])
    euid = os.geteuid()

    if euid == 0:
        print "This script cannot be executed as root. Exiting.."
        sys.exit(2)

    release = platform.dist()[0]
    package = install_packages(release)
    generate_gems()
    generate_packages(package)

    sys.exit(0)
