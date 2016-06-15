# -*- coding: utf-8 -*-
import os
import sys
#import subprocess
#import re
#import socket
#import shutil
#import stat
#import ipaddress
#import platform
#import configparser
#import urllib.request
from .general import question
from .linux_cmd import Linux_Cmd

default_config_file = 'config/default_flc.conf'


NECESSARY_PACKAGES = ('whois', 'python3-launchpadlib')



specials_repositories = {
    'Google-Chrome': {
        'apt_key': ["wget -O /tmp/linux_signing_key.pub 'https://dl-ssl.google.com/linux/linux_signing_key.pub'",
                    "apt-key add /tmp/linux_signing_key.pub"],
        'source_list': '/etc/apt/sources.list.d/google-chrome.list',
        'deb_line': 'deb http://dl.google.com/linux/chrome/deb/ stable main',
        'packages': 'google-chrome-stable'},
    'Dropbox': {
        'apt_key': 'apt-key adv --keyserver pgp.mit.edu --recv-keys 5044912E',
        'source_list': '/etc/apt/sources.list.d/dropbox.list',
        'deb_line': 'deb http://linux.dropbox.com/ubuntu/ xenial main',
        'packages': 'dropbox'},
    }


class install_specials_repositories():

    def __init__(self, _specials_repositories, install_all,
                    lock_file, linux_cmd):
        self._specials_repositories = _specials_repositories
        self.install_all = install_all
        self.lock_file = lock_file
        self.linux_cmd = linux_cmd

    def install_oneapp(self, tuple_package):
        _q = True
        if not self.install_all:
            if not question('Do you want install %s?' % (tuple_package[0])):
                _q = False
        if _q:
            app = self.linux_cmd
            sr = tuple_package[1]
            if not app.check_pgk(sr['packages']):
                if not os.path.isfile(sr['source_list']):
                    with open(sr['source_list'], "a") as applist:
                        applist.write(sr['deb_line'])
                for i in sr['apt_key']:
                    app.command(i)
                app.update_cmd()
                app.multi_install_cmd(sr['packages'])

    def installApps(self):
        for k in list(self._specials_repositories.items()):
            self.install_oneapp(k)


def update_system(MyOS, stdout, lock_file):
    Q = 'Do you want update/upgrade the system?'
    if question(Q, lock_file):
        update = Linux_Cmd(MyOS, stdout)
        update.update_cmd()
        update.upgrade_cmd()


def install_list_package(_lst_pkg, lock_file):
    Q = 'Do you want install %s?' % (_lst_pkg)
    if question(Q, lock_file):
        pkg = Linux_Cmd()
        pkg.multi_install_cmd(_lst_pkg)


def install_ppa(_tuple_ppa, lock_file):
    _ppas = _tuple_ppa[0]
    _packages = _tuple_ppa[1]
    Q = 'Do you want add the PPA "%s" and install %s?' % (_ppas, _packages)
    if question(Q, lock_file):
        ppa = Linux_Cmd()
        ppa.install_and_add_ppa(_tuple_ppa)


#def install_gits(_git_pkg, _dest):
    #for _git in _git_pkg:
        #Q = 'Do you download the git repository "%s"?' % (_git)
        #if question(Q):
            #ppa = Linux_Cmd()
            #ppa.git_clone(_git, _dest)


#def firewall(_asn):
    #Q = 'Do you want create iptables?'
    #if question(Q):
        #fw = iptables()
        #fw.create_iptables(_asn)


#def secure_delete():
    #SRM_TMP = '/tmp/srm.sh'
    #SRM_FINAL = '/etc/init.d/srm.sh'
    #SRM_HEAD = ['#!/bin/bash',
                 #'### BEGIN INIT INFO',
                 #'# Provides: firewall',
                 #'# Required-Start: $syslog $remote_fs $network',
                 #'# Required-Stop: $syslog $remote_fs $network',
                 #'# Default-Start: 0',
                 #'# Default-Stop: 1 2 3 4 5 6',
                 #'# Description: Start firewall configuration',
                 #'### END INIT INFO',
                 #'',
                 #'smem',
                 #'swapoff /dev/dm-3',
                 #'sswap -v /dev/dm-3'
                 #]
    #del_file(SRM_TMP)
    #with open(SRM_TMP, "a") as applist:
        #for i in SRM_HEAD:
            #applist.write(i)
    #del_file(SRM_FINAL)
    #shutil.move(SRM_TMP, SRM_FINAL)

    #for mode in stat.S_IEXEC, stat.S_IXGRP, stat.S_IXOTH:
        #st = os.stat(SRM_FINAL)
        #os.chmod(SRM_FINAL, st.st_mode | mode)


def help_app(_message=False):
    if _message:
        print('Error: %s \n' % (_message))
    print('Usage:')
    print('    sudo %s config_file [options]\n' % (sys.argv[0]))
    print('Options:')
    print('    -y        Answer "yes" to all questions')
    print('    -v        View standart output')
    print('    --help    Display this message\n')
    print('Examples:')
    print('    sudo %s config_file -v' % (sys.argv[0]))
    print('    sudo %s config_file -y' % (sys.argv[0]))
    print('    sudo %s config_file -v -y' % (sys.argv[0]))
    print('    sudo %s config_file -y -v' % (sys.argv[0]))
    print('    sudo %s --help' % (sys.argv[0]))
    print('    %s --help\n' % (sys.argv[0]))
    sys.exit(1)


def install(default_config, config, install_all, stdout,
            lock_file, MyOS, OSVersion, OSName):
    yall = Linux_Cmd(MyOS, stdout)
    PACKAGES = config.joint_list_packages('packages')
    PPAS = config.ppas_and_pkg('ppas')
    default_dict_vars = default_config.read_section('general')
    default_packages = default_dict_vars['default_packages']
    default_ubuntu = default_dict_vars['default_ubuntu']
    #IPTABLES_ASN = config.iptables_asn('iptables_asn')
    if install_all:
        yall.update_cmd()
        yall.upgrade_cmd()
        yall.multi_install_cmd(default_packages)
        if len(PACKAGES) > 0:
            yall.multi_install_cmd(PACKAGES)
        if MyOS == 'ubuntu':
            yall.multi_install_cmd(default_ubuntu)
            if len(PPAS[0]) > 0 and len(PPAS[1]) > 0:
                yall.install_and_add_ppa(PPAS)
        #fw = iptables()
        #fw.create_iptables(IPTABLES_ASN)
    else:
        update_system(MyOS, stdout, lock_file)
        yall.multi_install_cmd(default_packages)
        if len(PACKAGES) > 0:
            install_list_package(PACKAGES, lock_file)
        if MyOS == 'ubuntu':
            yall.multi_install_cmd(default_ubuntu)
            if len(PPAS[0]) > 0 and len(PPAS[1]) > 0:
                install_ppa(PPAS, lock_file)
        #firewall(IPTABLES_ASN)
        ##install_gits(GIT_PKG, DEST_GIT)

    isr = install_specials_repositories(specials_repositories,
                                        install_all, lock_file, yall)
    isr.installApps()
    yall.autoremove_cmd()


def options():
    stdout = False
    install_all = False
    config_file = default_config_file
    ARGS = len(sys.argv)
    #print(ARGS)
    parameters = ['-y', '-v']

    def validing_parameters(parameters, isfile=False):
        stdout = False
        install_all = False
        args = len(sys.argv)
        lArg = []
        if isfile:
            args -= 2
        else:
            args -= 1
            if args > 2:
                help_app('Too many option \n')
        for _p in range(0, args):
        # Validating the n parameter
            lArg.append(None)
            for p in parameters:
                value = _p
                if isfile:
                    value = _p + 1
                if sys.argv[value + 1] == p:
                    lArg[_p] = p
                    if p == '-y':
                        install_all = True
                    elif p == '-v':
                        stdout = True
                    break
            if lArg[_p] is None:
                help_app('"%s" is not a valid option.' % (sys.argv[value + 1]))
            if len(lArg) > 1:
                if len(lArg) != len(set(lArg)):
                    help_app('Option "%s" is repeated.' % (lArg[0]))
        return (True, install_all, stdout)

    # Validing fields
    if ARGS > 4:
        help_app('Too many option \n')
    elif ARGS == 1:
        return {'value': True, 'stdout': stdout,
                'install_all': install_all, 'config_file': config_file}
    elif ARGS == 2:  # Only way to read the help
        if sys.argv[1] == '--help':
            help_app()
        elif not os.path.isfile(sys.argv[1]):
            if not validing_parameters(parameters):
                pass
        elif os.path.isfile(sys.argv[1]):
            return {'value': True, 'stdout': stdout,
                    'install_all': install_all, 'config_file': sys.argv[1]}
    elif ARGS >= 3:
        if os.path.isfile(sys.argv[1]):
            config_file = sys.argv[1]
            vp = validing_parameters(parameters, True)
        elif not os.path.isfile(sys.argv[1]):
            vp = validing_parameters(parameters)
        install_all = vp[1]
        stdout = vp[2]
    return {'value': True, 'stdout': stdout,
            'install_all': install_all, 'config_file': config_file}






