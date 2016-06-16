##!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import core

if __name__ == '__main__':

    try:
        dict_options = core.options()
        config_file = dict_options['config_file']
        default_config = core.config_file(core.default_config_file)
        default_dict_vars = default_config.read_config_vars('general')
        #necessary_packages = default_dict_vars['necessary_packages']
        value = dict_options['value']
        install_all = dict_options['install_all']
        stdout = dict_options['stdout']
        config = core.config_file(config_file)
        dict_vars = config.read_config_vars('general')
        lock_file = dict_vars['lock_file']
        if not lock_file:
            lock_file = default_dict_vars['lock_file']
        MyOS = dict_vars['MyOS'].lower()
        OSVersion = dict_vars['OSVersion']
        OSName = dict_vars['OSName'].lower()
        print(dict_options)
        print(('myfile %s' % (dict_vars)))
        print(('defaultfile %s' % (default_dict_vars)))
        if value:
            if core.check_root():
                if not core.lock_process(lock_file):
                    if core.is_connected():
                            core.install(default_config, config, install_all,
                            stdout, lock_file, MyOS, OSVersion, OSName)
                            core.del_file(lock_file)
                        #pass

        #else:
            #core.help_app('else Invalid option(s).')
    except KeyboardInterrupt:
        print('\nExit by the user by pressing "Ctrl + c"...\n')
        core.del_file(lock_file)