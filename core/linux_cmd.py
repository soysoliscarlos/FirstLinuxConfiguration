# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import re
import pip
#import socket
#import shutil
#import stat
#import ipaddress
#import platform
#import configparser
import urllib.request


#def check_OS_Version():
    #global myos
    #myos = None
    #if platform.system() == 'Linux' or platform.system() == 'linux2':
        #_os = platform.linux_distribution()
        #print(_os)
        #if _os is tuple:
            #osdistro = _os[0]
            #osversion = _os[0]
            #osname
        #elif _os is str and _os == 'Windows':
            #
        #
        #if _os[0] == 'Ubuntu' or _os[0] == 'ubuntu':
            #myos =
            #return True, 'Ubuntu'
        #return True, 'Debian'
    #else:
        #print('This OS is not based on Debian')
        #return False

class Linux_Cmd():

    def __init__(self, _MyOS, _stdout):
        #self._packages = _packages
        _sudo = ''
        _MyOS = _MyOS.lower()
        self.stdout = _stdout
        if _MyOS == 'ubuntu':
            _sudo = 'sudo'
        self._sudo = _sudo
        self._MyOS = _MyOS

    def command(self, _cmd, redirect_stdout=False, out_file=None):
        _get = False
        if re.findall("^wget.+", _cmd):
            _get = True
        _cmd = _cmd.split()
        if self._MyOS == 'ubuntu':
            _cmd.insert(0, self._sudo)
        #print(_cmd)
        if _get:
            if _cmd.index('-O'):
                out_file = _cmd[3]
                url = _cmd[4]
                url = re.findall("\'(.+)\'", url)
                urllib.request.urlretrieve(url[0],
                    filename=out_file)
            else:
                url = _cmd[3]
                url = re.findall("\'(.+)\'", url)
                urllib.request.urlretrieve(url[0],
                    filename=url[0])
        elif redirect_stdout:
            of = open(out_file, "w")
            #print('command redirect_stdout')
            subprocess.check_call(_cmd, stdout=of)
        elif self.stdout:
            #print('command self.stdout')
            subprocess.check_call(_cmd)
        else:
            #print('command else ')
            subprocess.check_call((_cmd), stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)

    def update_cmd(self):
        print('Updating List of Packages...\n')
        if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
            self.command('apt update')
        print('OK...\n')

    def upgrade_cmd(self):
        print('Upgrading Packages...\n')
        if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
            self.command('apt upgrade -y')
        for dist in pip.get_installed_distributions():
            print(('Upgrading with pip "%s"' % (dist.project_name)))
            #print(str(dist.split()))
            if dist.project_name == 'Pillow':
                #print('##############' + dist.project_name + '############')
                self.multi_install_cmd('libjpeg8-dev')
            elif dist.project_name == 'lxml':
                #print('##############' + dist.project_name + '############')
                self.multi_install_cmd('libxml2-dev libxslt-dev')
            elif dist.project_name == 'dbus-python':
                #print('##############' + dist.project_name + '############')
                self.multi_install_cmd('libdbus-1-dev libdbus-glib-1-dev')
            ## Upgrading all pip modules

            pip.main(['install', '--upgrade', dist.project_name])
            #if self._MyOS == 'ubuntu':
                #self.command('-H pip3 install --upgrade ' + dist.project_name)
            #else:
                #self.command('pip3 install --upgrade ' + dist.project_name)
    #subprocess.call("pip install --upgrade " + dist.project_name, shell=True)
        print('OK...\n')

    def autoremove_cmd(self):
        print('Autoremoving Packages...\n')
        if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
            self.command('apt autoremove -y')
        print('OK...\n')

    def check_pgk(self, _package):
        try:
            if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
                self.command('dpkg-query -s %s' % (_package))
                return True
        except subprocess.CalledProcessError:
            return False

    def install_and_add_ppa(self, _tuple_ppa):
        if self._MyOS == 'ubuntu':
            count = 1
            _ppas = _tuple_ppa[0]
            _packages = _tuple_ppa[1]
            for _ppa in _ppas:
                print(('Validating PPA: %s' % (_ppa)))
                if self.ppa_info(_ppa):
                    if not self.check_repository(_ppa):
                        print(('Adding PPA repository %s' % (_ppa)))
                        self.command('add-apt-repository -y %s' % (_ppa))
                        self.update_cmd()
                if count == len(_ppas):
                    self.multi_install_cmd(_packages)
                else:
                    count += 1

    def install_cmd(self, _package):
        if not self.check_pgk(_package):
            print(('Installing %s' % (_package)))
            if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
                self.command('apt install -y %s' % (_package))
                print('OK...\n')
        else:
            print(('%s is already install' % (_package)))

    def multi_install_cmd(self, _packages):
        if type(_packages) is list or type(_packages) is tuple:
            for _package in _packages:
                self.install_cmd(_package)
            print('')
        else:
            self.install_cmd(_packages)

    def ppa_info(self, _ppa):
        if self._MyOS == 'ubuntu':
            from launchpadlib.launchpad import Launchpad
            import httplib2
            import lazr.restfulclient.errors
            try:
                lp = Launchpad.login_anonymously('foo', 'production', None)
            except  httplib2.HttpLib2Error as e:
                print(('Error connection to launchpad.net:', e))
                sys.exit(1)
            ppa_name = _ppa
            m = re.search(r'^(ppa:)?(?P<user>[^/]+)/(?P<name>.+)', ppa_name)
            if m:
                _user, name = m.group('user', 'name')
            else:
                print(('Unvalid PPA name:', _ppa))
                sys.exit(1)
            try:
                owner = lp.people[_user]
                ppa = owner.getPPAByName(name=name)
                print(('PPA is Valid. Source URL:\n%s' % (ppa)))
                return True
            except lazr.restfulclient.errors.RestfulError as e:
                print(('Error getting PPA info:', e))
                return False
                sys.exit(1)

    def check_repository(self, _repository):
        check = False
        _source_list = os.listdir('/etc/apt/sources.list.d/')
        repo = re.findall('/+\S+', _repository)
        #print(repo)

        if repo:
            repo = repo[0].lstrip('/')
        else:
            repo = _repository
        for sl in _source_list:
            if re.search('\S+.list$', sl):
                if re.search(repo, sl):
                    print('Repository already exist\n')
                    check = True
                    return check

    def git_clone(self, _git, _dest=''):
        if not _dest == '':
            _folder = re.findall("^http.+(/.+)\.git", _git)
            _dest = os.path.join(_dest, _folder)
        self.command('git clone %s %s' % (_git, _dest))
