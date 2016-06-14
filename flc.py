##!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import core
import os


#def check_lock_file():
    #try:
        #lock_file = config.get('general', 'lock_file')
    #except:
        #lock_file = '/var/run/flc.lock'
    #return lock_file


#def check_os():


if __name__ == '__main__':
    config = core.config_file('flc_config.txt')
    dict_vars = config.read_config_vars('general')
    lock_file = dict_vars['lock_file']
    MyOS = dict_vars['MyOS'].lower()
    OSVersion = dict_vars['OSVersion']
    OSName = dict_vars['OSName'].lower()
    try:
        dict_options = core.options()
        value = dict_options['value']
        install_all = dict_options['install_all']
        stdout = dict_options['stdout']
        print(dict_options)
        if value:
            if core.check_root():
                if not core.lock_process(lock_file):
                    if core.is_connected():
                            core.install(config, install_all, stdout,
                            lock_file, MyOS, OSVersion, OSName)
                            #input()
                            core.del_file(lock_file)

        else:
            core.help_app('else Invalid option(s).')
    except KeyboardInterrupt:
        print('\nExit by the user by pressing "Ctrl + c"...\n')
        core.del_file(lock_file)