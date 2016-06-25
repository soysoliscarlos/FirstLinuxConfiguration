#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import socket
import configparser
import subprocess
import re
import apt

lock_file = '/var/run/flc.lock'
defaultPackages = ('python3-dev')
defaultUbuntu = ('whois', 'python3-launchpadlib')


def check_root():
    if os.getuid() == 0:
        print("User has root privileges...\n")
        return True  # Return if user is root
    else:
        print("I cannot run as a mortal... Sorry...")
        print(('Run: sudo %s \n' % (sys.argv[0])))
        sys.exit(1)  # Return if user is not root

#def check_OS_linux():
    #info = lsb_release.get_distro_information()
    #print(info)
    ##if info != 'Ubuntu' and info !='LinuxMint':
        #pass


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


def lock_process(_lock_file, MyOS):
    i = Linux_Cmd(MyOS)
    try:
        import psutil
    except ImportError:
        try:
            import pip  # lint:ok
        except ImportError:
            i.command('easy_install -U pip')
            #i.install_cmd('python-pip')
        finally:
            import pip  # lint:ok
            pip.main(['install', 'psutil'])
            import psutil  # lint:ok
    if os.path.isfile(_lock_file):
        with open(_lock_file, "r") as lf:
            pid = lf.read()
            pid = int(pid)
        if psutil.pid_exists(pid):
            print('The process is already running...')
            print('Wait until the process is complete or delete the file:')
            print((('%s\n') % (_lock_file)))
            exit(0)
            return True
        else:
            with open(_lock_file, "w") as lf:
                lf.write(str(os.getpid()) + '\n')
            return False
    elif not os.path.isfile(_lock_file):
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


class Linux_Cmd():

    def __init__(self, _MyOS='linux', _stdout=False):
        if _MyOS == 'ubuntu' or _MyOS == 'debian':
            cache = apt.Cache()
            self.cache = cache
            #self.cache.update()
            #self.cache.commit(apt.progress.base.AcquireProgress(),
                            #apt.progress.base.InstallProgress())
        _sudo = ''
        _MyOS = _MyOS.lower()
        self.stdout = _stdout
        if _MyOS == 'ubuntu':
            _sudo = 'sudo'
        self._sudo = _sudo
        self._MyOS = _MyOS

    def command(self, _cmd, out_file=False):
        _cmd = _cmd.split()
        if self._MyOS == 'ubuntu':
            _cmd.insert(0, self._sudo)
        if not self.stdout:
            subprocess.check_call((_cmd), stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        elif self.stdout:
            subprocess.check_call(_cmd)
        elif out_file:
            of = open(out_file, "w")
            subprocess.check_call(_cmd, stdout=of)

    def update_cmd(self):
        print('Updating List of Packages...\n')
        if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
            self.command('apt-get update')
        print('OK...\n')

    def upgrade_cmd(self):
        print('Upgrading Packages...\n')
        if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
            self.command('apt-get upgrade -y')
            #self.cache.open(None)
            #self.cache.upgrade()
            #self.cache.commit(apt.progress.base.AcquireProgress(),
                            #apt.progress.base.InstallProgress())
        ## Upgrading python modules

    def upgrade_pip(self):
        try:
            import pip
        except ImportError:
            #self.install_cmd('python3-pip')
            self.command('easy_install -U pip')
            import pip  # lint:ok
        for dist in pip.get_installed_distributions(False):
            try:
                print(('Checking/Upgrading with pip "{}"'.format(
                                                        dist.project_name)))
                if str(dist.project_name) == 'Pillow':
                    if self._MyOS == 'ubuntu':
                        pip_packages = self.review_pgks(('libjpeg8-dev',
                                                        'libjpeg-dev'))
                        self.multi_install_cmd(pip_packages)
                elif str(dist.project_name) == 'lxml':
                    if self._MyOS == 'ubuntu':
                        pip_packages = self.review_pgks(('libxml2-dev',
                                                        'libxslt1-dev'))
                        self.multi_install_cmd(pip_packages)
                elif str(dist.project_name) == 'SecretStorage':
                    if self._MyOS == 'ubuntu':
                        pip_packages = self.review_pgks(('libdbus-1-dev',
                                                        'libdbus-glib-1-dev'))
                        self.multi_install_cmd(pip_packages)
                ## Upgrading all pip modules
                if self.stdout:
                    pip.main(['install', '--upgrade', dist.project_name])
                else:
                    pip.main(['install', '--upgrade', '-q', dist.project_name])
            except KeyboardInterrupt:
                print('\nExit by the user by pressing "Ctrl + c"...\n')
        print('OK...\n')

    def autoremove_cmd(self):
        print('Autoremoving Packages...\n')
        if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
            self.command('apt-get autoremove -y')
        print('OK...\n')

    def check_pgk(self, _package):
        if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
            if self.cache[_package].is_installed:
                print(("{} is already installed...\n".format(_package)))
                return True
            else:
                print(("{} is not installed...\n".format(_package)))
                return False
        else:
            help_app('It is not a supported OS')

    def review_pgks(self, _package):
        install = []
        if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
            if type(_package) is tuple or type(_package) is list:
                for p in tuple(_package):
                    try:
                        if not self.cache[p].is_installed:
                            install.append(p)
                        else:
                            print(('"{}" is already installed...\n'.format(p)))
                    except:
                        install.append(p)
                if len(install) > 0:
                    return install
            else:
                if not self.cache[_package].is_installed:
                    install.append(_package)
                    return install
                else:
                    print(('"{}" is already installed...\n'.format(_package)))
            return install
        else:
            help_app('It is not a supported OS')

    def install_and_add_ppa(self, _tuple_ppa):
        if self._MyOS == 'ubuntu':
            count = 1
            _ppas = _tuple_ppa[0]
            _packages = _tuple_ppa[1]
            vpkg = yall.review_pgks(_tuple_ppa[1])
            if not vpkg[0]:
                _packages = vpkg[1]
            for _ppa in _ppas:
                print(('Validating PPA: %s' % (_ppa)))
                if not self.check_repository(_ppa):
                    if self.ppa_info(_ppa):
                        print(('Adding PPA repository %s' % (_ppa)))
                        self.command('add-apt-repository -y %s' % (_ppa))
                        self.update_cmd()
                if count == len(_ppas):
                    if not vpkg[0]:
                        self.multi_install_cmd(_packages)
                else:
                    count += 1

    def install_cmd(self, _package):
        #if not self.check_pgk(_package):
            if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
                print(('Installing {}'.format(_package)))
                self.command('apt-get install -y {}'.format(_package))
                #pkg = self.cache[_package]
                #pkg.mark_install()
                #self.cache.commit(apt.progress.base.AcquireProgress(),
                            #apt.progress.base.InstallProgress())
                print('OK...\n')

    def multi_install_cmd(self, _packages):
        if len(_packages) > 0:
            if type(_packages) is tuple or type(_packages) is list:
                for _package in _packages:
                    self.install_cmd(_package)
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
                exit(1)
            ppa_name = _ppa
            m = re.search(r'^(ppa:)?(?P<user>[^/]+)/(?P<name>.+)', ppa_name)
            if m:
                _user, name = m.group('user', 'name')
            else:
                print(('Unvalid PPA name:', _ppa))
                exit(1)
            try:
                owner = lp.people[_user]
                ppa = owner.getPPAByName(name=name)
                print(('PPA is Valid. Source URL:\n%s' % (ppa)))
                return True
            except lazr.restfulclient.errors.RestfulError as e:
                print(('Error getting PPA info:', e))
                return False
                exit(1)

    def check_repository(self, _repository):
        check = False
        _source_list = os.listdir('/etc/apt/sources.list.d/')
        repo = re.findall('/+\S+', _repository)
        if repo:
            repo = repo[0].lstrip('/')
        else:
            repo = _repository
        for sl in _source_list:
            if re.search('\S+.list$', sl):
                if re.search(repo, sl):
                    print(('Repository already exist: "{}"\n'.format(
                                                            _repository)))
                    check = True
        return check

    def git_clone(self, _git, _dest=''):
        if not _dest == '':
            _folder = re.findall("^http.+(/.+)\.git", _git)
            _dest = os.path.join(_dest, _folder)
        self.command('git clone %s %s' % (_git, _dest))


def help_app(_message=False):
    if _message:
        print('Error: %s \n' % (_message))
    print('Usage:')
    print('    sudo python3 %s config_file [options]\n' % (sys.argv[0]))
    print('Options:')
    print('    -y        Answer "yes" to all questions')
    print('    -v        View standart output')
    print('    --help    Display this message\n')
    print('Examples:')
    print('    sudo python3 %s config_file -v' % (sys.argv[0]))
    print('    sudo python3 %s config_file -y' % (sys.argv[0]))
    print('    sudo python3 %s config_file -v -y' % (sys.argv[0]))
    print('    sudo python3 %s config_file -y -v' % (sys.argv[0]))
    print('    sudo python3 %s --help' % (sys.argv[0]))
    print('    python3 %s --help\n' % (sys.argv[0]))
    exit(1)


def upgrade_system(MyOS, stdout, lock_file):
    update = Linux_Cmd(MyOS, stdout)
    Q = 'Do you want upgrade the system?'
    if question(Q, lock_file):
        update.upgrade_cmd()
    Q = 'Do you want upgrade the python modules(pip)?'
    if question(Q, lock_file):
        update.upgrade_pip()


def install_list_package(_lst_pkg, lock_file, MyOS, stdout):
    if len(_lst_pkg) > 0:
        str_lst_pkg = ', '.join(_lst_pkg)
        Q = 'Do you want install {}?'.format(str_lst_pkg)
        if question(Q, lock_file):
            pkg = Linux_Cmd(MyOS, stdout)
            pkg.multi_install_cmd(_lst_pkg)


def install_ppa(_tuple_ppa, lock_file):
    ask = False
    _ppas = _tuple_ppa[0]
    _packages = _tuple_ppa[1]
    str_ppas = ', '.join(_ppas)
    str_packages = ', '.join(_packages)
    if len(_ppas) > 0 and len(_packages) > 0:
        ask = True
        Q = 'Do you want add the PPA: "{}" and install: "{}"?'.format(
            str_ppas, str_packages)
    elif len(_ppas) == 0 and len(_packages) == 0:
        pass
    elif len(_ppas) == 0:
        ask = True
        Q = 'Do you want install: "{}"?'.format(str_packages)
    elif len(_packages) == 0:
        ask = True
        Q = 'Do you want add the PPA: "{}"'.format(str_ppas)
    if ask:
        if question(Q, lock_file):
            ppa = Linux_Cmd(MyOS, stdout)
            ppa.install_and_add_ppa(_tuple_ppa)


def install(config, install_all, stdout,
            lock_file, MyOS, OSVersion, OSName):
    yall = Linux_Cmd(MyOS, stdout)
    PACKAGES = config.joint_list_packages('packages')
    ## Variable for ubuntu
    if MyOS == 'ubuntu':
        ## Installing default packages for ubuntu
        yall.multi_install_cmd(yall.review_pgks(defaultUbuntu))
        ## Variables for ppa's and packages
        PPAS = config.ppas_and_pkg('ppas')
        ppas = PPAS[0]
        packages_ppas = PPAS[1]
        tmpppa = []
        for ppa in PPAS[0]:
            if not yall.check_repository(ppa):
                tmpppa.append(ppa)
        ppas = tmpppa
        packages_ppas = yall.review_pgks(PPAS[1])
        PPAS = (ppas, packages_ppas)
    ## Answer "yes" to all questions
    if install_all:
        ## Upgrading all packages and python modules with pip
        yall.upgrade_cmd()
        yall.upgrade_pip()
        if len(PACKAGES) > 0:
            yall.multi_install_cmd(yall.review_pgks(PACKAGES))
        ## Special packages and ppa's for ubuntu
        if MyOS == 'ubuntu':
            yall.multi_install_cmd(yall.review_pgks(defaultUbuntu))
            ## Installing ppa's and packages
            if len(ppas) > 0 and len(packages_ppas) > 0:
                yall.install_and_add_ppa(PPAS)
    else:
        upgrade_system(MyOS, stdout, lock_file)
        if len(PACKAGES) > 0:
            install_list_package(yall.review_pgks(PACKAGES), lock_file,
                                                    MyOS, stdout)
        if MyOS == 'ubuntu':
            if len(PPAS[0]) > 0 and len(PPAS[1]) > 0:
                install_ppa(PPAS, lock_file)
    yall.autoremove_cmd()


def options():
    stdout = False
    install_all = False
    ARGS = len(sys.argv)
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
        help_app('You must indicate a configuration file \n')
    elif ARGS == 2:  # Only way to read the help
        if sys.argv[1] == '--help':
            help_app()
        elif not os.path.isfile(sys.argv[1]):
            help_app('"{}" is not a configuration file \n'.format(sys.argv[1]))
        elif os.path.isfile(sys.argv[1]):
            return {'value': True, 'stdout': stdout,
                    'install_all': install_all, 'config_file': sys.argv[1]}
    elif ARGS > 2:
        if os.path.isfile(sys.argv[1]):
            config_file = sys.argv[1]
            vp = validing_parameters(parameters, True)
        elif not os.path.isfile(sys.argv[1]):
            vp = validing_parameters(parameters)
        install_all = vp[1]
        stdout = vp[2]
    return {'value': True, 'stdout': stdout,
            'install_all': install_all, 'config_file': config_file}


if __name__ == '__main__':
    try:
        dict_options = options()
        configfile = dict_options['config_file']
        value = dict_options['value']
        install_all = dict_options['install_all']
        stdout = dict_options['stdout']
        config = config_file(configfile)
        general_config = config.read_config_vars('general')
        MyOS = general_config['MyOS'].lower()
        OSVersion = general_config['OSVersion']
        OSName = general_config['OSName'].lower()
        if value:
            if check_root():
                if is_connected():
                    yall = Linux_Cmd(MyOS, stdout)
                    yall.update_cmd()
                    yall.command('easy_install -U pip')
                    yall.multi_install_cmd(yall.review_pgks(
                                            defaultPackages))
                    if not lock_process(lock_file, MyOS):
                            install(config, install_all, stdout, lock_file,
                                    MyOS, OSVersion, OSName)
                            del_file(lock_file)
    except KeyboardInterrupt:
        print('\nExit by the user by pressing "Ctrl + c"...\n')
        del_file(lock_file)