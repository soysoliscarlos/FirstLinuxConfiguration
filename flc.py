#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import re
import socket
import shutil
import stat
import ipaddress
import platform
import configparser
import urllib.request

NECESSARY_PACKAGES = ('whois', 'python3-launchpadlib')

lock_file = '/var/run/script_install.lock'

specials_repositories = {
    'Google-Chrome': {
        'apt_key': ["wget -O /tmp/linux_signing_key.pub 'https://dl-ssl.google.com/linux/linux_signing_key.pub'",
                    "apt-key add /tmp/linux_signing_key.pub"],
        'source_list': '/etc/apt/sources.list.d/google-chrome.list',
        'deb_line': 'deb http://dl.google.com/linux/chrome/deb/ stable main',
        'packages': 'google-chrome-stable'},
    #'Dropbox': {
        #'apt_key': 'apt-key adv --keyserver pgp.mit.edu --recv-keys 5044912E',
        #'source_list': '/etc/apt/sources.list.d/dropbox.list',
        #'deb_line': 'deb http://linux.dropbox.com/ubuntu/ xenial main',
        #'packages': 'dropbox'},
    }


def check_root():
    if os.getuid() == 0:
        print("User has root privileges...\n")
        return True  # Return if user is root
    else:
        print("I cannot run as a mortal... Sorry...")
        print(('Run: sudo %s \n' % (sys.argv[0])))
        sys.exit(1)  # Return if user is not root


class config_file():

    def __init__(self, _file):
        _config = configparser.ConfigParser()
        _config.read(_file)
        self._config = _config

    def read_section(self, _section):
        try:
            section = dict(self._config.items(_section))
        except configparser.NoSectionError:
            section = {}
        return section

    def joint_list_packages(self, _section):
        packages = []
        section = self.read_section(_section)
        keys = list(section.keys())
        for v in keys:
            val = section[v].split()
            for mv in val:
                packages.append(mv)
        return packages

    def ppas_and_pkg(self, _section):
        packages = []
        ppas = []
        section = self.read_section(_section)
        count_sec = len(section)
        if count_sec % 2 == 0:
            x = int(len(section) / 2)
            try:
                for i in range(x):
                    v = i + 1
                    ppas.append(self._config.get(_section, "ppa%s" % (v)))
                    pkg = self._config.get(_section, "packages%s" % (v))
                    pkg = pkg.split()
                    for p in pkg:
                        packages.append(p)
            except:
                pass
        return ppas, packages

    def iptables_asn(self, _section):
        section = self.read_section(_section)
        return section


def is_connected():
    IS = "www.google.com"
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(IS)
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection((host, 80), 2)
        #print(s)
        #data = urllib.urlopen(IS)
        #print(data)
        print('System has internet connection...\n')

        return True
    except:
        print('System has not internet connection.')
        print('Connect the system to internet...\n')
        return False


def lock_process(_lock_file):
    if not os.path.isfile(_lock_file):
        with open(_lock_file, "a") as lf:
            lf.write('')
        return False
    else:
        print('The process is already running...')
        print('Wait until the process is complete or delete the file:')
        print((('%s\n') % (_lock_file)))
        sys.exit(0)
        return True


def question(_Q):
    _count = False
    while _count is False:
        SELECT = input("%s (Y/n)('q' to exit):" % _Q)
        if SELECT == "Y" or SELECT == "y" or SELECT == '':
            return True
        elif SELECT == "N" or SELECT == "n":
            return False
        elif SELECT == "Q" or SELECT == "q":
            del_file(lock_file)
            sys.exit(0)
        else:
            print('')
            print("You didn't choose a valid option. Select 'Y' or 'N'\n")
            print('')


def del_file(_file):
    if os.path.isfile(_file):
        os.remove(_file)
    return True


def ip_validator(_ip, subnet=False):
    if subnet:
        if ipaddress.ip_network(_ip):
            _ip = _ip[:-3]
    try:
        if ipaddress.ip_address(_ip):
            parts = _ip.split('.')
            ip = len(parts) == 4 and all(0 <= int(part) < 256 for part in parts)
            if ip:
                return True, 'IPV4'
            else:
                return True, 'IPV6'
    except ValueError:
        return False  # one of the 'parts' not convertible to integer
    except (AttributeError, TypeError):
        return False  # `ip` isn't even a string


def port_validator(_port):
    try:
        if int(_port) > 65535 or 0 >= int(_port):
            print('Number of port out of range.')
            return False
        elif 0 <= int(_port) <= 65535:
            return True
    except ValueError:
        return False


class Linux_Cmd():

    def __init__(self, _packages=None):
        self._packages = _packages
        self.view_output = VIEW_OUTPUT  # lint:ok
        self.Ubuntu = Ubuntu  # lint:ok
        if self.Ubuntu:  # lint:ok
            _sudo = 'sudo'
        else:
            _sudo = ''
        self._sudo = _sudo

    def command(self, _cmd, redirect_stdout=False, out_file=None):
        _get = False
        if re.findall("^wget.+", _cmd):
            _get = True
        _cmd = _cmd.split()
        _cmd.insert(0, self._sudo)
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
            subprocess.check_call(_cmd, stdout=of)
        elif self.view_output:
            subprocess.check_call(_cmd)
        else:
            subprocess.check_call((_cmd), stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)

    def update_cmd(self):
        print('Updating List of Packages...\n')
        self.command('apt update')
        print('OK...\n')

    def upgrade_cmd(self):
        print('Upgrading Packages...\n')
        self.command('apt upgrade -y')
        print('OK...\n')

    def autoremove_cmd(self):
        print('Autoremoving Packages...\n')
        self.command('apt autoremove -y')
        print('OK...\n')

    def check_pgk(self, _package):
        try:
            self.command('dpkg-query -s %s' % (_package))
            return True
        except subprocess.CalledProcessError:
            return False

    def install_and_add_ppa(self, _tuple_ppa):
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
        print(repo)

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


class iptables():
    tmp_iptables = '/tmp/iptables.sh'
    final_iptables = '/etc/init.d/iptables.sh'
    IPTABLES_HEAD = ['#!/bin/bash',
                 '### BEGIN INIT INFO',
                 '# Provides: firewall',
                 '# Required-Start: $syslog $remote_fs $network',
                 '# Required-Stop: $syslog $remote_fs $network',
                 '# Default-Start: 2 3 4 5',
                 '# Default-Stop: 0 1 6',
                 '# Description: Start firewall configuration',
                 '### END INIT INFO',
                 '',
                 '## para la primera vez, ejecutar la siguiente linea',
                 '## sudo update-rc.d iptables.sh defaults',
                 '',
                 '# Borrar cadenas anteriores',
                 'iptables -F',
                 'iptables -X',
                 'iptables -Z',
                 'iptables -t nat -F',
                 'ip6tables -F',
                 'ip6tables -X',
                 'ip6tables -Z',
                 'ip6tables -t nat -F',
                 '',
                 '## Condiciones por defecto',
                 'iptables -P INPUT DROP',
                 'ip6tables -P INPUT DROP',
                 '',
                 '## Desde el localhost se puede hacer todo',
                 'iptables -A INPUT -i lo -j ACCEPT',
                 'ip6tables -A INPUT -i lo -j ACCEPT',
                 '',
                 #'## Permitir ping',
                 #'iptables -A INPUT -i eth0 -p ICMP -j ACCEPT',
                 #'iptables -A OUTPUT -o eth0 -p ICMP -j ACCEPT',
                 #'',
                ]
    IPTABLES_MIDDLE = ['## Permitir conexiones establecidas',
                   'iptables -A INPUT -m state --state ESTABLISHED -j ACCEPT',
                   'ip6tables -A INPUT -m state --state ESTABLISHED -j ACCEPT',
                   '',
                   ]
    IPTABLES_BOTTOM = [
    '## Cerramos todos los puertos de INPUT que no permitimos anteriormente',
    'iptables -A INPUT -p tcp --dport 1:1024 -j DROP &> /dev/null',
    'iptables -A INPUT -p udp --dport 1:1024 -j DROP &> /dev/null',
    'ip6tables -A INPUT -p tcp --dport 1:1024 -j DROP &> /dev/null',
    'ip6tables -A INPUT -p udp --dport 1:1024 -j DROP &> /dev/null',
                  ]

    del_file(tmp_iptables)

    def __init__(self, IPTABLES_HEAD=IPTABLES_HEAD,
                       IPTABLES_MIDDLE=IPTABLES_MIDDLE,
                       IPTABLES_BOTTOM=IPTABLES_BOTTOM):
        self.IPTABLES_HEAD = IPTABLES_HEAD
        self.IPTABLES_MIDDLE = IPTABLES_MIDDLE
        self.IPTABLES_BOTTOM = IPTABLES_BOTTOM

    def allow_service(self):
        service = True
        while service is True:
            IPS = True
            PORT = input("Indicate port(1-65535):")
            if port_validator(PORT):
                while IPS is True:
                    IP = input("Indicate IP address(0.0.0.0 to 255.255.255.255):")
                    if ip_validator(IP):
                        with open(self.tmp_iptables, "a") as fw:
                            if ip_validator(IP) == (True, 'IPV4'):
                                fw.write('iptables -A INPUT -s %s -p tcp --dport %s -j ACCEPT \n'
                                    % (IP, PORT))
                            elif ip_validator(IP) == (True, 'IPV4'):
                                fw.write('ip6tables -A INPUT -s %s -p tcp --dport %s -j ACCEPT \n'
                                    % (IP, PORT))
                        Q = "Add another IP?:"
                        if not question(Q):
                            IPS = False
                    else:
                        print('\nYou did not write a valid IP address.')
                        print('Please write down a valid IP address.')
                Q = "Add another Service?:"
                if not question(Q):
                    service = False
            else:
                print('\nYou did not write a valid port number.')
                print('Please write down a valid port number.')

    def block_asn(self, _asn):
        asn_list = []
        asn_ips = []
        asn_file = '/tmp/asn.txt'
        del_file(asn_file)
        cmd = Linux_Cmd()
        for key in list(_asn.keys()):
            print(('\nBlocking %s ASN' % (key)))
            with open(self.tmp_iptables, "a") as fw:
                fw.write('\n## Blocking %s ASN\n' % (key))
            cmd.command('whois -H -h riswhois.ripe.net -- -F -K -i %s'
            % (_asn[key]),
                        True, asn_file)
            with open(asn_file, "r") as asn_read:
                for line in asn_read:
                    asn_list.append(line)
            for asn_item in asn_list:
                if not re.findall('^%', asn_item):
                    value = re.findall("\\t(.+)\\t", asn_item)
                    for v in value:
                        asn_ips.append(v)

            for IP in asn_ips:
                with open(self.tmp_iptables, "a") as fw:
                    if ip_validator(IP, True) == (True, 'IPV4'):
                        fw.write('iptables -A INPUT -s %s -j DROP &> /dev/null \n' % (IP))
                    elif ip_validator(IP, True) == (True, 'IPV6'):
                        fw.write('ip6tables -A INPUT -s %s -j DROP &> /dev/null \n' % (IP))

    def create_iptables(self, _asn):
        print("Creating iptables rules...\n")
        with open(self.tmp_iptables, "a") as fw:
            for ih in self.IPTABLES_HEAD:
                fw.write('%s \n' % (ih))

        Q = 'Do you want open some port?'
        if question(Q):
            self.allow_service()

        Q = 'Do you want block the ASNs'
        if question(Q):
            self.block_asn(_asn)

        with open(self.tmp_iptables, "a") as fw:
            for ih in self.IPTABLES_MIDDLE:
                fw.write('%s \n' % (ih))

        with open(self.tmp_iptables, "a") as fw:
            for ib in self.IPTABLES_BOTTOM:
                fw.write('%s \n' % (ib))

        del_file(self.final_iptables)
        shutil.move(self.tmp_iptables, self.final_iptables)

        for mode in stat.S_IEXEC, stat.S_IXGRP, stat.S_IXOTH:
            st = os.stat(self.final_iptables)
            os.chmod(self.final_iptables, st.st_mode | mode)

        print("Created iptables rules...\n")
        fw = Linux_Cmd()
        print("Updating rc.d...\n")
        fw.command('update-rc.d iptables.sh defaults')
        print("Activating Firewall...\n")
        fw.command('bash %s' % (self.final_iptables))


class install_specials_repositories():

    def __init__(self, _specials_repositories, q=False):
        self._specials_repositories = _specials_repositories
        self.q = q

    def install_oneapp(self, tuple_package):
        _q = True
        if self.q:
            if not question('Do you want install %s?' % (tuple_package[0])):
                _q = False
        if _q:
            app = Linux_Cmd()
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
        for k in self._specials_repositories.items():
            self.install_oneapp(k)


def update_system():
    Q = 'Do you want update/upgrade the system?'
    if question(Q):
        update = Linux_Cmd()
        update.update_cmd()
        update.upgrade_cmd()


def install_list_package(_lst_pkg):
    Q = 'Do you want install %s?' % (_lst_pkg)
    if question(Q):
        pkg = Linux_Cmd()
        pkg.multi_install_cmd(_lst_pkg)


def install_ppa(_tuple_ppa):
    _ppas = _tuple_ppa[0]
    _packages = _tuple_ppa[1]
    Q = 'Do you want add the PPA "%s" and install %s?' % (_ppas, _packages)
    if question(Q):
        ppa = Linux_Cmd()
        ppa.install_and_add_ppa(_tuple_ppa)


def install_gits(_git_pkg, _dest):
    for _git in _git_pkg:
        Q = 'Do you download the git repository "%s"?' % (_git)
        if question(Q):
            ppa = Linux_Cmd()
            ppa.git_clone(_git, _dest)


def firewall(_asn):
    Q = 'Do you want create iptables?'
    if question(Q):
        fw = iptables()
        fw.create_iptables(_asn)


def secure_delete():
    SRM_TMP = '/tmp/srm.sh'
    SRM_FINAL = '/etc/init.d/srm.sh'
    SRM_HEAD = ['#!/bin/bash',
                 '### BEGIN INIT INFO',
                 '# Provides: firewall',
                 '# Required-Start: $syslog $remote_fs $network',
                 '# Required-Stop: $syslog $remote_fs $network',
                 '# Default-Start: 0',
                 '# Default-Stop: 1 2 3 4 5 6',
                 '# Description: Start firewall configuration',
                 '### END INIT INFO',
                 '',
                 'smem',
                 'swapoff /dev/dm-3',
                 'sswap -v /dev/dm-3'
                 ]
    del_file(SRM_TMP)
    with open(SRM_TMP, "a") as applist:
        for i in SRM_HEAD:
            applist.write(i)
    del_file(SRM_FINAL)
    shutil.move(SRM_TMP, SRM_FINAL)

    for mode in stat.S_IEXEC, stat.S_IXGRP, stat.S_IXOTH:
        st = os.stat(SRM_FINAL)
        os.chmod(SRM_FINAL, st.st_mode | mode)


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


def install():
    yall = Linux_Cmd()
    conf = config_file(sys.argv[1])
    PACKAGES = conf.joint_list_packages('packages')
    PPAS = conf.ppas_and_pkg('ppas')
    IPTABLES_ASN = conf.iptables_asn('iptables_asn')
    if INSTALL_ALL:  # lint:ok
        yall.update_cmd()
        yall.upgrade_cmd()
        yall.multi_install_cmd(NECESSARY_PACKAGES)
        if len(PACKAGES) > 0:
            yall.multi_install_cmd(PACKAGES)
        if len(PPAS[0]) > 0 and len(PPAS[1]) > 0:
            yall.install_and_add_ppa(PPAS)
        fw = iptables()
        fw.create_iptables(IPTABLES_ASN)
        sr = install_specials_repositories(specials_repositories)
        sr.installApps()

    else:
        update_system()
        yall.multi_install_cmd(NECESSARY_PACKAGES)
        if len(PACKAGES) > 0:
            install_list_package(PACKAGES)
        if len(PPAS[0]) > 0 and len(PPAS[1]) > 0:
            install_ppa(PPAS)
        firewall(IPTABLES_ASN)
        #install_gits(GIT_PKG, DEST_GIT)
        sr = install_specials_repositories(specials_repositories, True)
        sr.installApps()

    #install_app()
    yall.autoremove_cmd()


def options():
    global VIEW_OUTPUT
    VIEW_OUTPUT = False
    global INSTALL_ALL
    INSTALL_ALL = False
    arg1 = None
    arg2 = None
    ARGS = len(sys.argv)
    parameters = ['-y', '-v']
    # Validando presentación de los argumentos
    if ARGS > 4:
        help_app('Too many option \n')
    elif ARGS == 1:
        help_app('You did not indicate de configuration file \n')
    elif ARGS == 2:  # Only way to read the help
        if sys.argv[1] == '--help':
            help_app()
        elif not os.path.isfile(sys.argv[1]):
            help_app('Error: %s is not a file' % (sys.argv[1]))

        else:
            return True
    elif ARGS >= 4:
        # Validating the first parameter
        for p in parameters:
            if sys.argv[2] == p:
                arg1 = p
                break
        if arg1 is None:
            print("arg1 %s" % (arg1))
            help_app('"%s" is not a valid option.' % (sys.argv[2]))
        #print(arg1)
        # Validating the second parameter
        try:
            for p in parameters:
                if sys.argv[3] == p:
                    arg2 = p
                    break
            if arg2 is None:
                help_app('"%s" is not a valid option.' % (sys.argv[3]))
            elif sys.argv[3] == arg1:
                help_app('Option "%s" is repeated.' % (arg1))
        except IndexError:
            pass

    # Loading parameters
    if sys.argv[2] == '-y':
        INSTALL_ALL = True
    else:
        try:
            if sys.argv[3] == '-y':
                INSTALL_ALL = True
        except IndexError:
            pass
    if sys.argv[2] == '-v':
        VIEW_OUTPUT = True
    else:
        try:
            if sys.argv[3] == '-v':
                VIEW_OUTPUT = True
        except IndexError:
            pass

    return True


def check_OS_Version():
    global Ubuntu
    Ubuntu = None
    if platform.system() == 'Linux' or platform.system() == 'linux2':
        _os = platform.linux_distribution()
        if _os[0] == 'Ubuntu' or _os[0] == 'ubuntu':
            Ubuntu = True
            return True, 'Ubuntu'
        return True, 'Debian'
    else:
        print('This OS is not based on Debian')
        return False


if __name__ == '__main__':
    try:
        if options():
            if check_root():
                if not lock_process(lock_file):
                    if is_connected():
                        if check_OS_Version():
                            install()
        else:
            help_app('Else Error: Invalid option(s).')
    except KeyboardInterrupt:
        print('\nExit by the user by pressing "Ctrl + c"...\n')
    finally:
        del_file(lock_file)
