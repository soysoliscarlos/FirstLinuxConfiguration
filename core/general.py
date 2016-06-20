# -*- coding: utf-8 -*-
import os
import sys
import socket
import ipaddress
import configparser
#from .runapp import default_config_file


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

    def get(self, _section, _var):
        return self._config.get(_section, _var)

    def read_section(self, _section):
        try:
            section = dict(self._config.items(_section))
        except configparser.NoSectionError:
            section = {}
        return section

    def read_config_vars(self, _section):
        dict_vars = self.read_section(_section)
        try:
            lock_file = dict_vars['lock_file']
        except KeyError:
            lock_file = False
        try:
            MyOS = dict_vars['myos']
        except KeyError:
            print('\nError: you must indicate your OS on the configuration file')
            print('Example:')
            print('    [general]')
            print('    MyOS = ubuntu or MyOS = debian\n')
            sys.exit(1)
        try:
            OSVersion = dict_vars['osversion']
        except KeyError:
            print('\nError: you must indicate your OS Version on the configuration file')
            print('Example:')
            print('    [general]')
            print('    OSVersion = 16.04 or OSVersion = 8\n')
            sys.exit(1)
        try:
            OSName = dict_vars['osname']
        except KeyError:
            print('\nError: you must indicate your OS Name on the configuration file')
            print('Example:')
            print('    [general]')
            print('    OSName = xenial or OSName = jessie\n')
            sys.exit(1)
        return {'lock_file': lock_file, 'MyOS': MyOS,
                'OSVersion': OSVersion, 'OSName': OSName}

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
    try:
        import psutil
    except ImportError:
        import pip
        pip.main(['install', 'psutil'])
        import psutil  # lint:ok
    if os.path.isfile(_lock_file):
        #print('if 2')
        with open(_lock_file, "r") as lf:
            pid = lf.read()
            pid = int(pid)
        if psutil.pid_exists(pid):
            #print('file exist')
            print('The process is already running...')
            print('Wait until the process is complete or delete the file:')
            print((('%s\n') % (_lock_file)))
            sys.exit(0)
            return True
        else:
            with open(_lock_file, "w") as lf:
                lf.write(str(os.getpid()) + '\n')
            return False
    elif not os.path.isfile(_lock_file):
        #print('if 1')
        with open(_lock_file, "a") as lf:
            lf.write(str(os.getpid()) + '\n')
        return False


def question(_Q, lock_file):
    _count = False
    while _count is False:
        SELECT = input("%s (Y/n)('q' to exit):" % _Q)
        if SELECT == "Y" or SELECT == "y" or SELECT == '':
            return True
        elif SELECT == "N" or SELECT == "n":
            return False
        elif SELECT == "Q" or SELECT == "q":
            os.remove(lock_file)
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
