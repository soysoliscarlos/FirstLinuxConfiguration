# -*- coding: utf-8 -*-

class iptables():

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
                        fw.write('iptables -A INPUT -s %s -j LOG --log-prefix "IP REJECT ASN" \n' % (IP))
                        fw.write('iptables -A INPUT -s %s -j REJECT &> /dev/null \n' % (IP))
                    elif ip_validator(IP, True) == (True, 'IPV6'):
                        fw.write('ip6tables -A INPUT -s %s -j LOG --log-prefix "IP REJECT ASN" \n' % (IP))
                        fw.write('ip6tables -A INPUT -s %s -j REJECT &> /dev/null \n' % (IP))

    def create_log_file(self):
        m = ["IP DROP", "IP ICMP", "IP REJECT ASN"]
        del_file(self.tmp_log)
        with open(self.tmp_log, "a") as fw:
            for i in m:
                fw.write(':msg,contains,%s /var/log/iptables.log \n' % (i))
        del_file(self.final_log)
        shutil.move(self.tmp_log, self.final_log)
        #

    def create_iptables(self, _asn):
        print("Creating iptables rules...\n")
        with open(self.tmp_iptables, "a") as fw:
            for ih in self.IPTABLES_HEAD:
                fw.write('%s \n' % (ih))

        Q = 'Do you want open some port?'
        if question(Q):
            self.allow_service()

        with open(self.tmp_iptables, "a") as fw:
            for ih in self.IPTABLES_MIDDLE:
                fw.write('%s \n' % (ih))

        Q = 'Do you want block the ASNs'
        if question(Q):
            self.block_asn(_asn)

        with open(self.tmp_iptables, "a") as fw:
            for ib in self.IPTABLES_BOTTOM:
                fw.write('%s \n' % (ib))

        del_file(self.final_iptables)
        shutil.move(self.tmp_iptables, self.final_iptables)

        for mode in stat.S_IEXEC, stat.S_IXGRP, stat.S_IXOTH:
            st = os.stat(self.final_iptables)
            os.chmod(self.final_iptables, st.st_mode | mode)
        print("Created iptables log file...\n")
        self.create_log_file()
        print("Created iptables rules...\n")
        fw = Linux_Cmd()
        print("Updating Log Service...\n")
        fw.command('service rsyslog restart')
        print("Updating rc.d...\n")
        fw.command('update-rc.d iptables.sh defaults')
        print("Activating Firewall...\n")
        fw.command('bash %s' % (self.final_iptables))


